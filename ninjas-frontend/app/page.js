"use client";

import React, { useState, useEffect, useRef } from 'react';

const platformIcons = {
  Windows: <img src="/icons/windows.png" alt="Windows" />,
  Linux: <img src="/icons/linux.png" alt="Linux" />,
  macOS: <img src="/icons/macos.png" alt="macOS" />,
  Network: <img src="/icons/network.png" alt="Network" />,
  PRE: <img src="/icons/pre.png" alt="PRE" />,
  Containers: <img src="/icons/containers.png" alt="Containers" />,
  IaaS: <img src="/icons/iaas.png" alt="IaaS" />,
  'Azure AD': <img src="/icons/azure.png" alt="Azure AD" />,
  'Office 365': <img src="/icons/office.png" alt="Office 365" />,
  SaaS: <img src="/icons/saas.png" alt="SaaS" />,
  'Google Workspace': <img src="/icons/google.png" alt="Google Workspace" />
};

export default function Home() {
  const [selected, setSelected] = useState('');
  const [query, setQuery] = useState('');
  const [data, setData] = useState([]);
  const [hasResults, setHasResults] = useState(true);
  const ws = useRef(null);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8000');

    ws.current.onopen = () => {
      ws.current.send('All');
    };

    ws.current.onmessage = (event) => {
      try {
        const parsedData = JSON.parse(event.data);
        const isValid = Array.isArray(parsedData) && parsedData.length > 0;
        setData(isValid ? parsedData : []);
        setHasResults(isValid);
      } catch {
        setData([]);
        setHasResults(false);
      }
    };

    return () => ws.current.close();
  }, []);

  useEffect(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(query.trim() || 'All');
    }
  }, [query]);

  const handleChange = (e) => setQuery(e.target.value.trim().replace(/\s+/g, ''));

  const togglePopup = () => {
    setIsOpen(!isOpen);
  };

  const handleItemClick = (itemName) => {
    setSelected(itemName);
    togglePopup();    
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(`select ${itemName}`);
    }
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
            value={query}
            onChange={handleChange}
          />
        </div>
      </div>

      <div className="body-container">
        <div className="container">
          <div className="overlay">
            <title2>Hall of</title2>
            <title1>Ninjas</title1>
          </div>
        </div>
      </div>

      <div className="content-body-container">
        <div className="content-container">
          <h2>Results - {query || 'All'}</h2>
          {hasResults ? (
            <ul>
              {data.map((item, index) => (
                <li key={index} onClick={() => handleItemClick(item.name)}>
                  <strong>Name:</strong> {item.name}<br />
                  <strong>ID:</strong> {item.id}<br />
                  <strong>Platform:</strong> {item.x_mitre_platforms.map(platform => (
                    <span className="icon-container" key={platform}>
                      {platformIcons[platform] || platform}
                      <span className="tooltip">{platform}</span>
                    </span>
                  ))}<br />
                  <strong>Detection:</strong> {item.x_mitre_detection}<br />
                  <strong>Phase Name:</strong> {item.phase_name}<br />
                </li>
              ))}
            </ul>
          ) : (
            <p>No Results</p>
          )}
        </div>
      </div>

      <div>
      {isOpen && selected && (
        <div className="overlaypopup">
          <div className="content-body-container">
            <div className="content-container">
              <button onClick={togglePopup}>X</button>

              <h2>Details - {selected}</h2>
              {data.length > 0 ? (
                data.filter(item => item.name === selected).map(item => (
                  <div key={item.id}>
                    <p><strong>ID:</strong> {item.id}</p>
                    <p><strong>Name:</strong> {item.name}</p>
                    <p><strong>Description:</strong> {item.description}</p>
                    <p><strong>Platform:</strong> {(item.x_mitre_platforms || []).map(platform => (
                      <span className="icon-container" key={platform}>
                        {platformIcons[platform] || platform}
                        <span className="tooltip">{platform}</span>
                      </span>
                    ))}</p>
                    <p><strong>Detection:</strong> {item.x_mitre_detection}</p>
                    <p><strong>Phase Name:</strong> {item.phase_name}</p>
                  </div>
                ))
              ) : (
                <p>No Details Available</p>
              )}
            </div>
          </div>
        </div>
      )}



    </div>
    </>
  );
}
