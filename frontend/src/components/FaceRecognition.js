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
      console.log('Requesting camera access...');
      
      // Set camera active FIRST so video element gets rendered
      setCameraActive(true);
      
      // Wait for next render cycle so videoRef.current is available
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'user',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        } 
      });
      
      console.log('Camera stream obtained:', stream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        
        // Ensure video plays
        videoRef.current.onloadedmetadata = () => {
          console.log('Video metadata loaded, attempting to play...');
          videoRef.current.play()
            .then(() => {
              console.log('Video playing successfully');
            })
            .catch(err => {
              console.error('Error playing video:', err);
              alert('Video failed to play: ' + err.message);
            });
        };
        
        // Additional event listeners for debugging
        videoRef.current.onplay = () => {
          console.log('Video started playing');
        };
        
        videoRef.current.onerror = (e) => {
          console.error('Video error:', e);
          alert('Video element error: ' + e.message);
        };
        
        console.log('Camera activated');
      } else {
        console.error('Video ref is still null after waiting');
        alert('Video element not found - please try again');
        setCameraActive(false);
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      setCameraActive(false);
      alert('Could not access camera: ' + error.message + '\n\nPlease:\n1. Allow camera permissions\n2. Close other apps using the camera\n3. Check camera privacy settings');
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

    // Flash effect
    const flashOverlay = document.createElement('div');
    flashOverlay.style.position = 'fixed';
    flashOverlay.style.top = '0';
    flashOverlay.style.left = '0';
    flashOverlay.style.width = '100vw';
    flashOverlay.style.height = '100vh';
    flashOverlay.style.backgroundColor = 'white';
    flashOverlay.style.opacity = '0';
    flashOverlay.style.transition = 'opacity 0.15s';
    flashOverlay.style.pointerEvents = 'none';
    flashOverlay.style.zIndex = '9999';
    document.body.appendChild(flashOverlay);

    // Trigger flash
    setTimeout(() => {
      flashOverlay.style.opacity = '0.8';
    }, 10);

    setTimeout(() => {
      flashOverlay.style.opacity = '0';
    }, 150);

    setTimeout(() => {
      document.body.removeChild(flashOverlay);
    }, 300);

    // Play camera shutter sound
    const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUqjl8bllHQU2k9n1yn0vBSh+zPLaizsKD2S57OynWBUIR6Lh8r1wIgUsgs7y2Ik2CBxqvfDknE4MDlKo5fG5ZR0FNpPZ9cp9LwUofszy2os7Cg9kuezsqFkVCEii4fK9cCIFLILO8tmJNggcar3w5JxODA5SqOXxuWUdBTaT2fXKfS8FKH7M8tqLOwoQZLns7KlZFQhIouHyvXAiBSyCzvLZiTYIHGq98OScTgwOUqjl8bllHQU2k9n1yn0vBSh+zPLaizsKEGS57OypWRUISQL=');
    audio.volume = 0.3;
    audio.play().catch(() => {}); // Ignore if audio fails

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

        const response = await axios.post('http://localhost:5000/api/analyze-face', {
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
            <div className="camera-active-badge">
              📹 Camera Active
            </div>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="video-preview video-preview-active"
              style={{ display: 'block' }}
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
