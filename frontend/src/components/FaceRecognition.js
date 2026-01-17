import React, { useState, useRef } from 'react';
import axios from 'axios';
import './FaceRecognition.css';

const FaceRecognition = () => {
  const [capturedImage, setCapturedImage] = useState(null);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

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
          <h3>👤 Identification Results</h3>
          <div className="result-card">
            <div className="result-item">
              <strong>Person:</strong>
              <span>{result.person.name}</span>
            </div>
            <div className="result-item">
              <strong>Confidence:</strong>
              <span>{(result.person.confidence * 100).toFixed(1)}%</span>
            </div>
            {result.person.features_detected && (
              <div className="result-item">
                <strong>Face Detected:</strong>
                <span>{result.person.features_detected.face_found ? '✅ Yes' : '❌ No'}</span>
              </div>
            )}
            {result.person.features_detected?.image_dimensions && (
              <div className="result-item">
                <strong>Image Size:</strong>
                <span>{result.person.features_detected.image_dimensions}</span>
              </div>
            )}
            {result.person.features_detected?.note && (
              <div className="note">
                <strong>Note:</strong> {result.person.features_detected.note}
              </div>
            )}
          </div>

          {result.person.matches && result.person.matches.length > 0 && (
            <div className="matches-section">
              <h4>Possible Matches:</h4>
              <ul className="matches-list">
                {result.person.matches.map((match, index) => (
                  <li key={index} className="match-item">
                    <span className="match-name">{match.name}</span>
                    <span className="match-confidence">
                      {(match.confidence * 100).toFixed(1)}%
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FaceRecognition;
