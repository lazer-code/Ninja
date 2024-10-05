"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";

const platformIcons = {
  Windows: <img src="/icons/windows.png" alt="Windows" />,
  Linux: <img src="/icons/linux.png" alt="Linux" />,
  macOS: <img src="/icons/macos.png" alt="macOS" />,
  Network: <img src="/icons/network.png" alt="Network" />,
  PRE: <img src="/icons/pre.png" alt="PRE" />,
  Containers: <img src="/icons/containers.png" alt="Containers" />,
  IaaS: <img src="/icons/iaas.png" alt="IaaS" />,
  "Azure AD": <img src="/icons/azure.png" alt="Azure AD" />,
  "Office 365": <img src="/icons/office.png" alt="Office 365" />,
  SaaS: <img src="/icons/saas.png" alt="SaaS" />,
  "Google Workspace": <img src="/icons/google.png" alt="Google Workspace" />,
  Infected: <img src="/icons/infected.png" alt="Infected"/>,
  Clean: <img src="/icons/clean.png" alt="Clean"/>
};

export default function Home() {
  const [AISearchbar, setAISearchbar] = useState("");
  const [searchbar, setSearchbar] = useState("");
  const [finalSearch, setFinalSearch] = useState("All");
  const [showSearchBar, setShowSearchBar] = useState(false);
  const [searchType, setSearchType] = useState("Normal Search");
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [data, setData] = useState([]);
  const [wsReady, setWsReady] = useState(false);
  const [isFile, setIsFile] = useState(false);
  const [dataDict, setDataDict] = useState({});
  const [count, setCount] = useState(30);

  const ws = useRef(null);
  const searchBarRef = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket("ws://localhost:8000");
      sendData("All", searchType);
  }, []);

  const sendData = (query, type) => {
    if (ws.current && wsReady)
      ws.current.send(`${type} ${query || "All"}`);

    else
    {
      ws.current = new WebSocket("ws://localhost:8000");
      const handleOpen = () => {
        
        if (ws.current && ws.current.readyState === WebSocket.OPEN)
          ws.current.send(`${type} ${query || "All"}`);
      };
      ws.current.addEventListener("open", handleOpen, { once: true });
    }

    ws.current.addEventListener("message", (event) => {
      try
      {
        const parsedData = JSON.parse(event.data);
        setData(Array.isArray(parsedData) ? parsedData : []);
      }
      
      catch (error)
      {
        if (event.data === 'malicious')
          setData([{ id: "N/A", name: "Malicious", description: "This result is classified as malicious", x_mitre_platforms: ['infected'], phase_name: "N/A", x_mitre_detection: "N/A" }]);
        
        else
          setData([]);
      }
    });
  };

  const handleSearchBarChanged = (e) => {
    const value = e.target.value;

    if (value == "")
      setFinalSearch("All");

    setSearchbar(value);
    setIsFile(false);
    setSearchType("Normal Search");
    sendData(value, "Normal Search");
    setFinalSearch(value);
  };

  const handleAISearchBarChanged = (e) => {
    setAISearchbar(e.target.value);
  };

  const handleItemClicked = useCallback((index) => {
    setSelectedIndex((prevIndex) => (prevIndex === index ? null : index));
  }, []);

  const toggleSearchBar = () => setShowSearchBar((prev) => !prev);

  const handleClickOutside = useCallback((e) => {
    if (searchBarRef.current && !searchBarRef.current.contains(e.target)) {
      setShowSearchBar(false);
    }
  }, []);

  useEffect(() => {
    if (showSearchBar)
      document.addEventListener("click", handleClickOutside);
    
    else
      document.removeEventListener("click", handleClickOutside);

    return () => document.removeEventListener("click", handleClickOutside);
  }, [showSearchBar, handleClickOutside]);

  useEffect(() => {
    if (isFile && count > 0)
    {
        const interval = setInterval(() => {
            if (dataDict && Object.keys(dataDict).length > 0)
            {
                clearInterval(interval);
                setCount(-1);
            }
            
            else
                setCount(prevCount => prevCount - 1);
        }, 1000);

        return () => clearInterval(interval);
    }
}, [isFile, count, dataDict]);

  const handleSendClick = () => {
    setSearchType("AI Search");
    sendData(AISearchbar, "AI Search");
    setFinalSearch(AISearchbar);
  };

  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    const maxSize = 650 * 1024 * 1024;

    try
    {
      const size = file.size;
      setIsFile(true);

      try
      {
        if (size > maxSize)
        {
            alert('File size exceeds 650 MB');
            e.target.value = '';
        }

        else
        {
            let offset = 0;
            const chunkSize = 0.5 * 1024 * 1024;
            const totalChunks = Math.ceil(file.size / chunkSize);
    
            if (!(ws.current && wsReady))
                ws.current = new WebSocket("ws://localhost:8000");
    
            ws.current.onopen = () => {
                ws.current.send(JSON.stringify({ filename: file.name, totalChunks }));
                sendChunk();
            };

            const sendChunk = () => {
                if (offset < file.size) 
                {
                    const chunk = file.slice(offset, offset + chunkSize);
                    const reader = new FileReader();
    
                    reader.onload = () => {
                        ws.current.send(reader.result);
                        offset += chunkSize;
                        sendChunk();
                    };
    
                    reader.readAsArrayBuffer(chunk);
                }

                else 
                {
                  ws.current.send('EOF');
                  setDataDict({});
                  
                  setTimeout(() => {
                      setIsFile(true);
                  }, 1000);
                
                }
            };

            ws.current.addEventListener("message", (event) => {
                try
                {
                    const parsedData = JSON.parse(event.data);
                    if (parsedData)
                        setDataDict(parsedData);
                }
                
                catch (error)
                {
                    console.error("Error parsing message:", error);
                }
            });
        }
      }
    
      catch (error) {}
    }

    catch (error) {}


};

  return (
    <>
      <div className="menu">
      <div className="home">
        <a href="LoginPage.html">Home</a>
      </div>
      <div className="search">
        <input
          type="text"
          placeholder="Search..."
          value={searchbar}
          onChange={handleSearchBarChanged}
          onFocus={handleSearchBarChanged}
        />
      </div>
      
      <div className="file-uploader">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="file-input"
          id="fileinput"
          accept="*"
        />
        <label className="file-label" onClick={() => fileInputRef.current.click()}>
          Check A File
        </label>
      </div>
    </div>

      <div className="body-container">
        <div className="container">
          <div className="overlay">
            <h2>Attack like a</h2>
            <h1>Ninja</h1>
          </div>
        </div>
      </div>

      {!isFile && (
        <div className="content-body-container">
          <div className="content-container">
            <title1>Guide</title1>
            <title2>AI</title2>
            <ul>
              <li>You can use your own language</li>
              <li>Spell mistakes aren't corrected</li>
              <li>For search in the inner database of attacks, you must use one of those keywords: id, name, phase name, description, detection</li>
              <li>The keywords must be separate as words. To demonstrate, md5, hash, id, phase name</li>
              <li>All keywords: id, description, phase_name, name, platform, detection, md5, sha1, sha256, sha512, bcrypt, aes, rsa, url, website, link, ip, ipaddress.</li>
              <li>Usage example for database search for all attacks with "windows" within its name: search in database for object with name windows</li>
              <li>Usage example for virustotal search for md5 virus status: check md5 xxxxx</li>
            </ul>
          </div>
        </div>
      )}

      {!isFile && (
        <div className="content-body-container">
          <div className="content-container">
            <h3>{searchType} Results - {finalSearch}</h3>
            <ul>
              {data.length > 0 ? (
                data.map(({ id, name, description, x_mitre_platforms = [], phase_name, x_mitre_detection }, index) => (
                  <React.Fragment key={id}>
                    <li style={{ display: "flex", alignItems: "center", cursor: "pointer" }}>
                      <p style={{ flex: "1" }}>{name}</p>
                      <p style={{ flex: "2", display: "flex", justifyContent: "center" }}>
                        {Array.isArray(x_mitre_platforms) && x_mitre_platforms.length > 0 ? (
                          x_mitre_platforms.map((platform) => (
                            <span className="icon-container" key={platform}>
                              {platformIcons[platform] || platform}
                              <span className="tooltip">{platform}</span>
                            </span>
                          ))
                        ) : (
                          <span>{data}</span>
                        )}
                      </p>
                      <p style={{ flex: "1", textAlign: "center" }}>{phase_name}</p>
                      {(x_mitre_platforms && x_mitre_platforms.length > 0) && (
                        <button onClick={() => handleItemClicked(index)}>
                          {selectedIndex === index ? "v" : "^"}
                        </button>
                      )}
                    </li>
                    {selectedIndex === index && (
                      <li style={{ borderTop: "5px solid #ddd", borderBottom: "5px solid #ddd" }}>
                        <div>
                          <h3>Id</h3>
                          <p>{id}</p>
                          <br />
                          <h3>Description</h3>
                          <p>{description}</p>
                          <br />
                          <h3>Detection</h3>
                          <p>{x_mitre_detection}</p>
                          <br />
                        </div>
                      </li>
                    )}
                  </React.Fragment>
                ))
              ) : (
                <p>No Results</p>
              )}
            </ul>
          </div>
        </div>
      )}

      <button onClick={toggleSearchBar} className="fixed-button">
        AI
      </button>

      {showSearchBar && (
        <div ref={searchBarRef} className="search-bar">
          <p></p>
          <input
            type="text"
            placeholder="Search data within the database or 'virustotal'..."
            value={AISearchbar}
            onChange={handleAISearchBarChanged}
          />
          <button onClick={handleSendClick} className="send-button">
            <div className="icon-container">
              <img src="/icons/send.png" alt="Send" />
            </div>
          </button>
        </div>
      )}

      {isFile && count >= 0 && (
        <div className="content-body-container">
        <div className="content-container">
          <h1>Sandbox Results - Waiting ({count})</h1>
        </div>
      </div>
      )}

      {isFile && count <= 0 &&(
        <div className="content-body-container">
          <div className="content-container">
            <h1>Sandbox Results</h1>
            <div className="lists-container">
              {Object.keys(dataDict).map((key) => (
                <div key={key}>
                  <br/>
                  <h3>{key.replace(/_/g, ' ').toUpperCase()} ({dataDict[key].length})</h3>
                  {dataDict[key].length > 0 ? (
                    <ul>
                      {dataDict[key].map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  ) : (
                    <p>None</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}