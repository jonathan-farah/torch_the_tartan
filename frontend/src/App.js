import React, { useState } from 'react';
import './App.css';
import VoiceRecognition from './components/VoiceRecognition';
import FaceRecognition from './components/FaceRecognition';

function App() {
  const [activeTab, setActiveTab] = useState('voice');

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎭 Torch the Tartan</h1>
        <p>Voice Actor & Facial Recognition for TV Shows</p>
      </header>

      <div className="container">
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'voice' ? 'active' : ''}`}
            onClick={() => setActiveTab('voice')}
          >
            🎤 Voice Recognition
          </button>
          <button
            className={`tab ${activeTab === 'face' ? 'active' : ''}`}
            onClick={() => setActiveTab('face')}
          >
            📸 Face Recognition
          </button>
        </div>

        <div className="content">
          {activeTab === 'voice' ? <VoiceRecognition /> : <FaceRecognition />}
        </div>
      </div>

      <footer className="App-footer">
        <p>Powered by AI • Voice Analysis & Facial Recognition</p>
      </footer>
    </div>
  );
}

export default App;
