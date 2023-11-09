import React from 'react';
import Car from './components/Car';
import './App.css';

function App() {

  return (
    <div className='app-body'>
      <canvas className='game-bg' />
      <Car />
    </div>
  );
}

export default App;
