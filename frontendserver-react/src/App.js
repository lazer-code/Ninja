import logo from './logo.svg';
import './App.css';

function App() {
  return (
    <body>
      <div id="menu-container"></div>
      <div class="menu-toggle" id="menu-toggle">
        <div class="bar horizontal"></div>
        <div class="bar horizontal"></div>
        <div class="bar horizontal"></div>
      </div>
      
      <div class="body-container">
        <div class="container" id="container">
            <div class="overlay">
                <h1>Home of</h1>
                <h2>Ninjas</h2>
            </div>
        </div>
      </div>
    
      <script src="scripts.js"></script>
    </body>    
  );
}

export default App;
