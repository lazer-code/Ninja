import React, { useState, useEffect } from 'react';
import './App.css';
import './Menu.css';

function App() {
  const [query, setQuery] = useState('');
  const [title, setTitle] = useState('Ninjas');

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (query) {
          const encodedQuery = encodeURIComponent(query); // Encode the query
          const response = await fetch(`http://localhost:8000/search?query=${encodedQuery}`);
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          const data = await response.text(); // Read response as text
          console.log('Response data:', data); // Log response data
          setTitle(data.trim()); // Update title
        }
      } catch (error) {
        console.error('Failed to fetch:', error);
      }
    };

    fetchData();
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
            <h1>Hall of {title}</h1>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
