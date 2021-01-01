import React, {useEffect} from 'react';
//import logo from './logo.svg';
import './App.css';
//9:55

function App() {
//now taking the data and rendering it on the screen

///this with fetch simply grabs the data and has it appear in the console.
  useEffect(() => {
  fetch('/movies').then(response => response.json().then(data => {

  console.log(data);

  }))

  }, [])
  return (
    <div className="App">

    </div>
  );
}

export default App;
