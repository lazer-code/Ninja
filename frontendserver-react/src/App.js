import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import './Menu.css';

function App() {
  const [query, setQuery] = useState('All');
  const [data, setData] = useState([]);
  const [hasResults, setHasResults] = useState(true);
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8000');

    ws.current.onopen = () => console.log('WebSocket connection established');
    ws.current.onmessage = (event) => {
      try {
        const parsedData = JSON.parse(event.data);

        // Check if parsed data is an array and contains the expected fields
        if (Array.isArray(parsedData) && parsedData.length > 0) {
          setData(parsedData);
          setHasResults(true);
        } else {
          setData([]);
          setHasResults(false);
        }
      } catch (error) {
        console.error('Error parsing JSON:', error);
        setData([]);
        setHasResults(false);
      }
    };

    ws.current.onclose = () => console.log('WebSocket connection closed');
    ws.current.onerror = (error) => console.error('WebSocket error:', error);

    return () => ws.current.close();
  }, []);

  useEffect(() => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(query || 'All');
    }
  }, [query]);
  

  const handleChange = (e) => {
    const value = e.target.value.replace(/\s+/g, '');
    setQuery(value);
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
        <div className="container" id="container">
          <div className="overlay">
            <title2>Hall of</title2>
            <title1>Ninjas</title1>
          </div>
        </div>
      </div>

      <div className="content-body-container">
        <div className="content-container" id="content-container">
          <div>
            <h2>Results - {query || 'All'}</h2>
            {hasResults ? (
              <ul>
                {data.map((item, index) => (
                  <li key={index}>
                    <strong>Name:</strong> {item.name}<br />
                    <strong>ID:</strong> {item.id}<br />
                    <strong>Platform:</strong> {item.x_mitre_platforms.join(', ')}<br />
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
      </div>
    </>
  );
}

export default App;
