"use client";

import React, { useState, useEffect, useRef } from "react";

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
};

export default function Home() {
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [query, setQuery] = useState("");
  const [data, setData] = useState([]);
  const [hasResults, setHasResults] = useState(true);
  const ws = useRef(null);
  const [showSearchBar, setShowSearchBar] = useState(false);
  const searchBarRef = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket("ws://localhost:8000");
    ws.current.onopen = () => ws.current.send("All");
    ws.current.onmessage = (event) => {
      try {
        const parsedData = JSON.parse(event.data);
        setData(Array.isArray(parsedData) && parsedData.length > 0 ? parsedData : []);
        setHasResults(parsedData.length > 0);
      } catch {
        setData([]);
        setHasResults(false);
      }
    };
    return () => ws.current.close();
  }, []);

  useEffect(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(query.trim() || "All");
    }
  }, [query]);

  const handleChange = (e) => setQuery(e.target.value.trim().replace(/\s+/g, ""));

  const handleItemClick = (index) => {
    setSelectedIndex((prevIndex) => (prevIndex === index ? null : index));
  };

  const toggleSearchBar = () => {
    setShowSearchBar((prev) => !prev);
  };

  const handleClickOutside = (e) => {
    if (searchBarRef.current && !searchBarRef.current.contains(e.target)) {
      setShowSearchBar(false);
    }
  };

  useEffect(() => {
    if (showSearchBar) {
      document.addEventListener("click", handleClickOutside);
    } else {
      document.removeEventListener("click", handleClickOutside);
    }

    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, [showSearchBar]);

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
            value={query}
            onChange={handleChange}
          />
        </div>
      </div>

      <div className="body-container">
        <div className="container">
          <div className="overlay">
            <title2>Attack like a</title2>
            <title1>Ninja</title1>
          </div>
        </div>
      </div>

      <div className="content-body-container">
        <div className="content-container">
          <h2>Results - {query || "All"}</h2>
          <ul>
            <li style={{ display: "flex", alignItems: "center", borderBottom: "5px solid #ccc" }}>
              <p style={{ flex: "1" }}>Name</p>
              <p style={{ flex: "1", textAlign: "center" }}>Platforms</p>
              <p style={{ flex: "1", textAlign: "center" }}>Phase Name</p>
              <p style={{ flex: "1", textAlign: "center" }}>Action</p>
            </li>
          </ul>
          {hasResults ? (
            <ul>
              {data.map(({ name, x_mitre_platforms, phase_name, description, x_mitre_detection, id }, index) => (
                <React.Fragment key={index}>
                  <li style={{ display: "flex", alignItems: "center", cursor: "pointer" }}>
                    <p style={{ flex: "1" }}>{name}</p>
                    <p style={{ flex: "2", display: "flex", justifyContent: "center" }}>
                      {x_mitre_platforms.map((platform) => (
                        <span className="icon-container" key={platform} style={{ margin: "0 4px" }}>
                          {platformIcons[platform] || platform}
                          <span className="tooltip">{platform}</span>
                        </span>
                      ))}
                    </p>
                    <p style={{ flex: "1", textAlign: "center" }}>{phase_name}</p>
                    <button onClick={() => handleItemClick(index)} style={{ marginLeft: "10px" }}>
                      {selectedIndex === index ? "v" : "^"}
                    </button>
                  </li>
                  {selectedIndex === index && (
                    <li style={{ padding: "10px", borderTop: "5px solid #ddd", borderBottom: "5px solid #ddd" }}>
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
              ))}
            </ul>
          ) : (
            <p>No Results</p>
          )}
        </div>
      </div>

      <button onClick={toggleSearchBar} className="fixed-button">
        AI
      </button>

      {showSearchBar && (
        <div ref={searchBarRef} className="search-bar">
          <input
            type="text"
            placeholder="Search..."
            value={query}
            onChange={handleChange}
          />
        </div>
      )}
    </>
  );
}
