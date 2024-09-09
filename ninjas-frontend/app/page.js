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
  const [popupData, setPopupData] = useState([]);
  const ws = useRef(null);
  const [isOpen, setIsOpen] = useState(false);
  const [requestSource, setRequestSource] = useState('server');
  const popupRef = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8000');
    ws.current.onopen = () => ws.current.send('All');
    ws.current.onmessage = (event) => {
      try {
        const parsedData = JSON.parse(event.data);
        setData(Array.isArray(parsedData) && parsedData.length > 0 ? parsedData : []);
        setHasResults(parsedData.length > 0);
        setRequestSource('server');
      } catch {
        setData([]);
        setHasResults(false);
        setRequestSource('server');
      }
    };
    return () => ws.current.close();
  }, [requestSource]);

  useEffect(() => {
    if (isOpen && popupRef.current) {
      const scrollToPopup = () => {
        const popupTop = popupRef.current.getBoundingClientRect().top + window.scrollY;
        window.scrollTo({ top: popupTop - 100, behavior: 'smooth' });
      };
      scrollToPopup();
    }
  }, [isOpen, popupData]);

  useEffect(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(query.trim() || 'All');
    }
  }, [query]);

  const handleChange = (e) => setQuery(e.target.value.trim().replace(/\s+/g, ''));

  const togglePopup = () => setIsOpen(prev => !prev);

  const handleItemClick = (itemName) => {
    const itemData = data.find(item => item.name === itemName);
    setSelected(itemName);
    setPopupData(itemData ? [itemData] : []);

    if (!isOpen) togglePopup();

    setRequestSource('user');

    if (ws.current?.readyState === WebSocket.OPEN) ws.current.send(`select ${itemName}`);
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
            <title2>Attack like a</title2>
            <title1>Ninja</title1>
          </div>
        </div>
      </div>

      {isOpen && selected && (
        <div className="overlaypopup" ref={popupRef}>
          <div className="content-body-container">
            <div className="content-container">
              <button onClick={togglePopup}>X</button>
              <h2>Details - {selected}</h2>
              {popupData.length ? (
                popupData.map(({ id, name, description, x_mitre_platforms = [], x_mitre_detection, phase_name }) => (
                  <div key={id}>
                    <h3>Id</h3>
                    <p>{id}</p>
                    <br></br>

                    <h3>Description</h3>
                    <p>{description}</p>
                    <br></br>

                    <h3>Platforms</h3>
                    <p>{x_mitre_platforms.map(platform => (
                      <span className="icon-container" key={platform}>
                        {platformIcons[platform] || platform}
                        <span className="tooltip">{platform}</span>
                      </span>
                    ))}</p>
                    <br></br>

                    <h3>Detection</h3>
                    <p>{x_mitre_detection}</p>
                    <br></br>

                    <h3>Phase Name</h3>
                    <p>{phase_name}</p>
                  </div>
                ))
              ) : (
                <p>No Details Available</p>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="content-body-container">
        <div className="content-container">
          <h2>Results - {query || 'All'}</h2>
          <ul>
              <li style={{ display: 'flex', alignItems: 'center', borderBottom: '5px solid #ccc'}}>
                <p style={{ flex: '1' }}>Name</p>
                <p style={{ flex: '1', textAlign: 'center' }}>Platforms</p>
                <p style={{ flex: '1', textAlign: 'right' }}>Phase Name</p>
              </li>
          </ul>
          {hasResults ? (
            <ul>
              {data.map(({ name, x_mitre_platforms, phase_name }, index) => (
                <li key={index} onClick={() => handleItemClick(name)} style={{ display: 'flex', alignItems: 'center'}}>
                  <p style={{ flex: '1' }}>{name}</p>
                  <p style={{ flex: '2', display: 'flex', justifyContent: 'center' }}>
                    {x_mitre_platforms.map(platform => (
                      <p className="icon-container" key={platform} style={{ margin: '0 4px' }}>
                        {platformIcons[platform] || platform}
                        <p className="tooltip">{platform}</p>
                      </p>
                    ))}
                  </p>
                  <p style={{ flex: '1', textAlign: 'right' }}>{phase_name}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p>No Results</p>
          )}
        </div>
      </div>
    </>
  );
}
