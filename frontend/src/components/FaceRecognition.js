import React, { useState, useRef } from 'react';
import axios from 'axios';
import './FaceRecognition.css';

const FaceRecognition = () => {
  const [capturedImage, setCapturedImage] = useState(null);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [liveDetection, setLiveDetection] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const detectionIntervalRef = useRef(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'user' } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setCameraActive(true);
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      alert('Could not access camera. Please check permissions.');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
      setCameraActive(false);
    }
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current);
      detectionIntervalRef.current = null;
      setLiveDetection(false);
    }
  };

  const toggleLiveDetection = () => {
    setLiveDetection(!liveDetection);
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);

    canvas.toBlob((blob) => {
      setCapturedImage(blob);
      setUploadedImage(null);
      setResult(null);
    });

    stopCamera();
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setUploadedImage(file);
      setCapturedImage(null);
      setResult(null);
    }
  };

  const analyzeface = async () => {
    const imageToAnalyze = capturedImage || uploadedImage;
    
    if (!imageToAnalyze) {
      alert('Please capture or upload an image first');
      return;
    }

    setLoading(true);
    try {
      const reader = new FileReader();
      reader.readAsDataURL(imageToAnalyze);
      reader.onloadend = async () => {
        const base64Image = reader.result;

        const response = await axios.post('/api/analyze-face', {
          image: base64Image
        });

        setResult(response.data);
      };
    } catch (error) {
      console.error('Error analyzing face:', error);
      alert('Error analyzing face: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  const clearImage = () => {
    setCapturedImage(null);
    setUploadedImage(null);
    setResult(null);
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  const currentImage = capturedImage || uploadedImage;

  return (
    <div className="face-recognition">
      <h2>📸 Facial Recognition</h2>
      <p className="description">
        Capture or upload a photo to identify the person
      </p>

      <div className="camera-section">
        {!cameraActive && !currentImage && (
          <div className="camera-controls">
            <button onClick={startCamera} className="btn btn-camera">
              📷 Start Camera
            </button>
            <div className="divider">OR</div>
            <label htmlFor="file-upload" className="btn btn-upload">
              📁 Upload Image
            </label>
            <input
              id="file-upload"
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </div>
        )}

        {cameraActive && (
          <div className="video-container">
            {liveDetection && (
              <div className="live-detection-badge">
                🔴 Live Detection Active
              </div>
            )}
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="video-preview"
            />
            <div className="video-controls">
              <button onClick={capturePhoto} className="btn btn-capture">
                📸 Capture Photo
              </button>
              <button 
                onClick={toggleLiveDetection} 
                className={`btn ${liveDetection ? 'btn-stop' : 'btn-live'}`}
              >
                {liveDetection ? '⏸️ Stop Live' : '🔴 Live Detection'}
              </button>
              <button onClick={stopCamera} className="btn btn-cancel">
                ❌ Cancel
              </button>
            </div>
          </div>
        )}

        <canvas ref={canvasRef} style={{ display: 'none' }} />

        {currentImage && (
          <div className="image-preview">
            <img
              src={URL.createObjectURL(currentImage)}
              alt="Preview"
              className="preview-image"
            />
            <div className="image-controls">
              <button
                onClick={analyzeface}
                className="btn btn-analyze"
                disabled={loading}
              >
                {loading ? '🔄 Analyzing...' : '🔍 Identify Person'}
              </button>
              <button
                onClick={clearImage}
                className="btn btn-clear"
                disabled={loading}
              >
                🗑️ Clear
              </button>
            </div>
          </div>
        )}
      </div>

      {result && (
        <div className="results">
          {result.cached && (
            <div className="cache-badge">
              ⚡ Retrieved from cache (accessed {result.cache_hits} times)
            </div>
          )}
          
          {result.face_count > 0 && (
            <div className="face-count-badge">
              👥 {result.face_count} {result.face_count === 1 ? 'Face' : 'Faces'} Detected
              {result.total_people && result.total_people > 1 && (
                <span> • {result.total_people} people identified</span>
              )}
            </div>
          )}
          
          {result.annotated_image && (
            <div className="annotated-image-section">
              <h4>Face Detection Visualization</h4>
              <img 
                src={result.annotated_image} 
                alt="Annotated with face detection" 
                className="annotated-image"
              />
            </div>
          )}
          
          {result.people && result.people.length > 0 ? (
            result.people.map((person, index) => (
              <div key={index} className="actor-profile" style={{marginBottom: '2rem'}}>
                <div className="profile-header">
                  <div className="profile-image-container">
                    <img 
                      src={person.photo || `https://ui-avatars.com/api/?name=${encodeURIComponent(person.name)}&size=200&background=667eea&color=fff&bold=true`}
                      alt={person.name}
                      className="profile-image"
                      onError={(e) => {
                        e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(person.name)}&size=200&background=667eea&color=fff&bold=true`;
                      }}
                    />
                    <div className="confidence-badge">
                      {(person.confidence * 100).toFixed(0)}% Match
                    </div>
                    {index === 0 && result.total_people > 1 && (
                      <div className="primary-badge">Primary</div>
                    )}
                  </div>
                  
                  <div className="profile-info">
                    <h2 className="actor-name">{person.name}</h2>
                    <p className="actor-title">Actor / Performer</p>
                    {person.face_confidence && (
                      <p className="face-quality">
                        Face Detection: {(person.face_confidence * 100).toFixed(0)}%
                      </p>
                    )}
                  </div>
                </div>

                <div className="profile-section">
                  <h3 className="section-title">🎬 Notable Projects</h3>
                  {person.notable_projects && person.notable_projects.length > 0 ? (
                    <div className="projects-grid">
                      {person.notable_projects.map((project, projIndex) => (
                        <div key={projIndex} className="project-card">
                          <div className="project-icon">🎭</div>
                          <div className="project-name">{project}</div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="no-data">No notable projects available</p>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="result-card">
              <div className="result-item">
                <strong>Primary Person:</strong>
                <span className="actor-name">{result.person_name || 'Unknown'}</span>
              </div>
              {result.confidence && (
                <div className="result-item">
                  <strong>Confidence:</strong>
                  <span>{(result.confidence * 100).toFixed(1)}%</span>
                </div>
              )}
              {result.notable_projects && result.notable_projects.length > 0 && (
                <div className="result-item notable-projects">
                  <strong>Notable Projects:</strong>
                  <ul className="projects-list">
                    {result.notable_projects.map((project, index) => (
                      <li key={index}>{project}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
          
          {result.faces && result.faces.length > 1 && (
            <div className="all-faces-section">
              <h4>📊 All Detected Faces</h4>
              <div className="faces-grid">
                {result.faces.map((face, index) => (
                  <div key={index} className="face-card">
                    <div className="face-info">
                      <strong>Face {index + 1}</strong>
                      <span>Confidence: {(face.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="face-details">
                      <div>Size: {face.bbox.width}x{face.bbox.height}px</div>
                      {face.features && face.features.sharpness && (
                        <div>Sharpness: {face.features.sharpness.toFixed(2)}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.features && (
            <details className="features-details">
              <summary>📊 Image Features</summary>
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

export default FaceRecognition;
