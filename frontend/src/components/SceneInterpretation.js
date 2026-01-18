import React, { useState, useRef } from 'react';
import axios from 'axios';

const SceneInterpretation = () => {
    const [isCapturing, setIsCapturing] = useState(false);
    const [cameraStream, setCameraStream] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const videoRef = useRef(null);
    const canvasRef = useRef(null);

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { width: 1280, height: 720 } 
            });
            
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
            }
            
            setCameraStream(stream);
            setIsCapturing(true);
            setError(null);
        } catch (err) {
            setError('Failed to access camera: ' + err.message);
        }
    };

    const stopCamera = () => {
        if (cameraStream) {
            cameraStream.getTracks().forEach(track => track.stop());
            setCameraStream(null);
        }
        setIsCapturing(false);
    };

    const captureAndAnalyze = async (withFaces = false) => {
        if (!videoRef.current || !canvasRef.current) return;

        const video = videoRef.current;
        const canvas = canvasRef.current;
        const context = canvas.getContext('2d');

        // Set canvas size to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Draw video frame to canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert canvas to base64
        const imageBase64 = canvas.toDataURL('image/jpeg');

        // Analyze
        setLoading(true);
        setError(null);

        try {
            const endpoint = withFaces 
                ? 'http://localhost:5000/api/analyze-face-with-scene'
                : 'http://localhost:5000/api/interpret-scene';

            const response = await axios.post(endpoint, {
                image: imageBase64,
                context: '' // Optional: could add user context here
            });

            setResult(response.data);
        } catch (err) {
            setError('Analysis failed: ' + (err.response?.data?.error || err.message));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px' }}>
            <h2>🎬 Scene Interpretation with Overshoot AI</h2>
            
            <div style={{ marginBottom: '20px' }}>
                {!isCapturing ? (
                    <button 
                        onClick={startCamera}
                        style={{
                            padding: '10px 20px',
                            fontSize: '16px',
                            cursor: 'pointer',
                            backgroundColor: '#4CAF50',
                            color: 'white',
                            border: 'none',
                            borderRadius: '5px'
                        }}
                    >
                        Start Camera
                    </button>
                ) : (
                    <>
                        <button 
                            onClick={stopCamera}
                            style={{
                                padding: '10px 20px',
                                fontSize: '16px',
                                cursor: 'pointer',
                                backgroundColor: '#f44336',
                                color: 'white',
                                border: 'none',
                                borderRadius: '5px',
                                marginRight: '10px'
                            }}
                        >
                            Stop Camera
                        </button>
                        <button 
                            onClick={() => captureAndAnalyze(false)}
                            disabled={loading}
                            style={{
                                padding: '10px 20px',
                                fontSize: '16px',
                                cursor: loading ? 'not-allowed' : 'pointer',
                                backgroundColor: loading ? '#ccc' : '#2196F3',
                                color: 'white',
                                border: 'none',
                                borderRadius: '5px',
                                marginRight: '10px'
                            }}
                        >
                            {loading ? 'Analyzing...' : 'Interpret Scene'}
                        </button>
                        <button 
                            onClick={() => captureAndAnalyze(true)}
                            disabled={loading}
                            style={{
                                padding: '10px 20px',
                                fontSize: '16px',
                                cursor: loading ? 'not-allowed' : 'pointer',
                                backgroundColor: loading ? '#ccc' : '#9C27B0',
                                color: 'white',
                                border: 'none',
                                borderRadius: '5px'
                            }}
                        >
                            {loading ? 'Analyzing...' : 'Analyze Faces + Scene'}
                        </button>
                    </>
                )}
            </div>

            {isCapturing && (
                <div style={{ marginBottom: '20px' }}>
                    <video 
                        ref={videoRef}
                        autoPlay 
                        playsInline
                        style={{ 
                            width: '100%', 
                            maxWidth: '640px',
                            border: '2px solid #ddd',
                            borderRadius: '5px'
                        }}
                    />
                </div>
            )}

            <canvas ref={canvasRef} style={{ display: 'none' }} />

            {error && (
                <div style={{
                    padding: '15px',
                    backgroundColor: '#ffebee',
                    color: '#c62828',
                    borderRadius: '5px',
                    marginBottom: '20px'
                }}>
                    {error}
                </div>
            )}

            {result && (
                <div style={{
                    padding: '20px',
                    backgroundColor: '#f5f5f5',
                    borderRadius: '5px',
                    marginTop: '20px'
                }}>
                    <h3>Analysis Results</h3>
                    
                    {result.annotated_image && (
                        <div style={{ marginBottom: '20px' }}>
                            <img 
                                src={result.annotated_image} 
                                alt="Annotated" 
                                style={{ 
                                    maxWidth: '100%',
                                    border: '2px solid #ddd',
                                    borderRadius: '5px'
                                }} 
                            />
                        </div>
                    )}

                    {result.person_name && (
                        <div style={{ marginBottom: '15px' }}>
                            <h4>👤 Identified Person</h4>
                            <p><strong>Name:</strong> {result.person_name}</p>
                            <p><strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}%</p>
                            {result.notable_projects && result.notable_projects.length > 0 && (
                                <div>
                                    <strong>Notable Projects:</strong>
                                    <ul>
                                        {result.notable_projects.map((project, idx) => (
                                            <li key={idx}>{project}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                            <p><strong>Faces Detected:</strong> {result.face_count}</p>
                        </div>
                    )}

                    <div style={{ 
                        backgroundColor: 'white', 
                        padding: '15px', 
                        borderRadius: '5px',
                        marginTop: '15px'
                    }}>
                        <h4>🎬 Scene Interpretation</h4>
                        
                        {result.scene_interpretation && (
                            <div style={{ marginBottom: '15px' }}>
                                <strong>Scene Description:</strong>
                                <p>{result.scene_interpretation}</p>
                            </div>
                        )}

                        {result.interpretation && (
                            <div style={{ marginBottom: '15px' }}>
                                <strong>Interpretation:</strong>
                                <p>{result.interpretation}</p>
                            </div>
                        )}

                        {result.scene_description && (
                            <div style={{ marginBottom: '15px' }}>
                                <strong>Description:</strong>
                                <p>{result.scene_description}</p>
                            </div>
                        )}

                        {result.interaction_analysis && (
                            <div style={{ marginBottom: '15px' }}>
                                <strong>Interaction Analysis:</strong>
                                <p>{result.interaction_analysis}</p>
                            </div>
                        )}

                        {result.setting && (
                            <div style={{ marginBottom: '15px' }}>
                                <strong>Setting:</strong>
                                <p>{result.setting}</p>
                            </div>
                        )}

                        {result.story_context && (
                            <div style={{ marginBottom: '15px' }}>
                                <strong>Story Context:</strong>
                                <p>{result.story_context}</p>
                            </div>
                        )}

                        {result.mood && (
                            <div style={{ marginBottom: '15px' }}>
                                <strong>Mood:</strong>
                                <p>{result.mood}</p>
                            </div>
                        )}

                        {result.elements && result.elements.length > 0 && (
                            <div style={{ marginBottom: '15px' }}>
                                <strong>Elements:</strong>
                                <ul>
                                    {result.elements.map((element, idx) => (
                                        <li key={idx}>{element}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {(result.overshoot_confidence || result.confidence) && (
                            <p style={{ fontSize: '12px', color: '#666', marginTop: '10px' }}>
                                <strong>Analysis Confidence:</strong> {
                                    ((result.overshoot_confidence || result.confidence) * 100).toFixed(1)
                                }%
                            </p>
                        )}

                        {result.latency_ms && (
                            <p style={{ fontSize: '12px', color: '#666' }}>
                                <strong>Analysis Time:</strong> {result.latency_ms.toFixed(0)}ms
                            </p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default SceneInterpretation;
