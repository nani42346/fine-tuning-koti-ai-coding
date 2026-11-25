import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import Intro from './Intro';
import reportWebVitals from './reportWebVitals';

// Shows the intro (landing) page first, then the main chat page.
function Root() {
  // Open http://localhost:3000/#app to skip the intro and go straight to the dashboard
  const [entered, setEntered] = useState(() => window.location.hash === "#app");

  if (!entered) return <Intro onEnter={() => setEntered(true)} />;

  return (
    <div className="app-enter">
      <App />
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
