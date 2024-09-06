import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import './Menu.css';

function App() {
  const [query, setQuery] = useState('');
  const [title, setTitle] = useState('Ninjas');
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8000');

    ws.current.onopen = () => console.log('WebSocket connection established');
    ws.current.onmessage = (event) => {
      setTitle(event.data.trim()); // Update title with server response
    };
    ws.current.onclose = () => console.log('WebSocket connection closed');
    ws.current.onerror = (error) => console.error('WebSocket error:', error);

    return () => ws.current.close();
  }, []);

  useEffect(() => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN && query) {
      ws.current.send(query);
    }
  }, [query]);

  const handleChange = (e) => {
    const value = e.target.value.replace(/\s+/g, ''); // Remove all spaces
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
            <h1>Hall of</h1>
            <h2>Ninjas</h2>
            <h3>{title}</h3>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
