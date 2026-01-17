import React, { useState, useRef } from 'react';
import axios from 'axios';
import './VoiceRecognition.css';

const VoiceRecognition = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [context, setContext] = useState('');
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setResult(null);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const analyzeVoice = async () => {
    if (!audioBlob) {
      alert('Please record audio first');
      return;
    }

    setLoading(true);
    try {
      // Convert blob to base64
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      reader.onloadend = async () => {
        const base64Audio = reader.result;

        const response = await axios.post('/api/analyze-voice', {
          audio: base64Audio,
          context: context
        });

        setResult(response.data);
      };
    } catch (error) {
      console.error('Error analyzing voice:', error);
      alert('Error analyzing voice: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  const clearRecording = () => {
    setAudioBlob(null);
    setResult(null);
    audioChunksRef.current = [];
  };

  return (
    <div className="voice-recognition">
      <h2>🎤 Voice Actor Identification</h2>
      <p className="description">
        Record audio from a TV show and let our AI identify the voice actor
      </p>

      <div className="input-section">
        <label htmlFor="context">TV Show / Context (optional):</label>
        <input
          id="context"
          type="text"
          value={context}
          onChange={(e) => setContext(e.target.value)}
          placeholder="e.g., The Simpsons, Breaking Bad..."
          className="context-input"
        />
      </div>

      <div className="recording-controls">
        {!isRecording ? (
          <button
            onClick={startRecording}
            className="btn btn-record"
            disabled={loading}
          >
            🎙️ Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="btn btn-stop"
          >
            ⏹️ Stop Recording
          </button>
        )}

        {audioBlob && !isRecording && (
          <>
            <button
              onClick={analyzeVoice}
              className="btn btn-analyze"
              disabled={loading}
            >
              {loading ? '🔄 Analyzing...' : '🔍 Analyze Voice'}
            </button>
            <button
              onClick={clearRecording}
              className="btn btn-clear"
              disabled={loading}
            >
              🗑️ Clear
            </button>
          </>
        )}
      </div>

      {isRecording && (
        <div className="recording-indicator">
          <div className="pulse"></div>
          <span>Recording in progress...</span>
        </div>
      )}

      {audioBlob && !isRecording && (
        <div className="audio-preview">
          <p>✅ Audio recorded successfully</p>
          <audio controls src={URL.createObjectURL(audioBlob)} />
        </div>
      )}

      {result && (
        <div className="results">
          <h3>🎭 Analysis Results</h3>
          <div className="result-card">
            <div className="result-item">
              <strong>Voice Actor:</strong>
              <span>{result.voice_actor.name}</span>
            </div>
            <div className="result-item">
              <strong>Confidence:</strong>
              <span>{(result.voice_actor.confidence * 100).toFixed(1)}%</span>
            </div>
            {result.voice_actor.reasoning && (
              <div className="result-item">
                <strong>Analysis:</strong>
                <p>{result.voice_actor.reasoning}</p>
              </div>
            )}
            {result.voice_actor.note && (
              <div className="note">
                <strong>Note:</strong> {result.voice_actor.note}
              </div>
            )}
          </div>

          {result.features && (
            <details className="features-details">
              <summary>📊 Audio Features</summary>
              <div className="features-grid">
                {Object.entries(result.features).map(([key, value]) => (
                  <div key={key} className="feature-item">
                    <span className="feature-label">{key.replace(/_/g, ' ')}:</span>
                    <span className="feature-value">
                      {typeof value === 'number' ? value.toFixed(2) : value}
                    </span>
                  </div>
                ))}
              </div>
            </details>
          )}
        </div>
      )}
    </div>
  );
};

export default VoiceRecognition;
