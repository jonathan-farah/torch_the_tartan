import React, { useState, useRef } from 'react';
import axios from 'axios';

const MusicIdentification = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [recordingTime, setRecordingTime] = useState(0);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const timerRef = useRef(null);

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
            
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                await identifyMusic(audioBlob);
                
                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());
                
                // Clear timer
                if (timerRef.current) {
                    clearInterval(timerRef.current);
                }
            };
            
            mediaRecorder.start();
            setIsRecording(true);
            setError(null);
            setResult(null);
            setRecordingTime(0);
            
            // Start timer
            timerRef.current = setInterval(() => {
                setRecordingTime(prev => prev + 1);
            }, 1000);
            
        } catch (err) {
            setError('Failed to access microphone: ' + err.message);
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    const identifyMusic = async (audioBlob) => {
        setLoading(true);
        setError(null);

        try {
            // Convert blob to base64
            const reader = new FileReader();
            reader.readAsDataURL(audioBlob);
            reader.onloadend = async () => {
                const base64Audio = reader.result;
                
                const response = await axios.post('http://localhost:5000/api/identify-music', {
                    audio: base64Audio,
                    duration: recordingTime
                });

                setResult(response.data);
            };
        } catch (err) {
            const errorMessage = err.response?.data?.message || err.response?.data?.error || err.message;
            const statusCode = err.response?.status;
            
            if (statusCode === 503) {
                setError(`🔒 Service Unavailable: ${errorMessage}`);
            } else {
                setError('Music identification failed: ' + errorMessage);
            }
        } finally {
            setLoading(false);
        }
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div style={{ padding: '20px' }}>
            <h2>🎵 Music Identification with Shazam</h2>
            <p style={{ color: '#666', marginBottom: '20px' }}>
                Record audio from your environment to identify songs playing in the background
            </p>
            
            <div style={{ marginBottom: '20px' }}>
                {!isRecording ? (
                    <button 
                        onClick={startRecording}
                        disabled={loading}
                        style={{
                            padding: '15px 30px',
                            fontSize: '18px',
                            cursor: loading ? 'not-allowed' : 'pointer',
                            backgroundColor: loading ? '#ccc' : '#1DB954',
                            color: 'white',
                            border: 'none',
                            borderRadius: '50px',
                            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                        }}
                    >
                        🎤 Start Listening
                    </button>
                ) : (
                    <div>
                        <button 
                            onClick={stopRecording}
                            style={{
                                padding: '15px 30px',
                                fontSize: '18px',
                                cursor: 'pointer',
                                backgroundColor: '#f44336',
                                color: 'white',
                                border: 'none',
                                borderRadius: '50px',
                                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                                animation: 'pulse 1.5s ease-in-out infinite'
                            }}
                        >
                            ⏹️ Stop & Identify ({formatTime(recordingTime)})
                        </button>
                        <style>{`
                            @keyframes pulse {
                                0%, 100% { opacity: 1; }
                                50% { opacity: 0.7; }
                            }
                        `}</style>
                    </div>
                )}
            </div>

            {loading && (
                <div style={{
                    padding: '20px',
                    backgroundColor: '#e3f2fd',
                    borderRadius: '5px',
                    marginBottom: '20px',
                    textAlign: 'center'
                }}>
                    <div style={{ fontSize: '24px', marginBottom: '10px' }}>🔍</div>
                    <p style={{ margin: 0 }}>Identifying music...</p>
                </div>
            )}

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

            {result && result.success && result.track_found && (
                <div style={{
                    padding: '20px',
                    backgroundColor: '#f5f5f5',
                    borderRadius: '10px',
                    marginTop: '20px'
                }}>
                    <div style={{ display: 'flex', gap: '20px', alignItems: 'start' }}>
                        {result.cover_art && (
                            <img 
                                src={result.cover_art} 
                                alt="Album Cover"
                                style={{
                                    width: '150px',
                                    height: '150px',
                                    borderRadius: '10px',
                                    boxShadow: '0 4px 8px rgba(0,0,0,0.2)'
                                }}
                            />
                        )}
                        
                        <div style={{ flex: 1 }}>
                            <h3 style={{ margin: '0 0 10px 0', fontSize: '24px' }}>
                                🎵 {result.title}
                            </h3>
                            <p style={{ 
                                margin: '0 0 10px 0', 
                                fontSize: '18px', 
                                color: '#666' 
                            }}>
                                by <strong>{result.artist}</strong>
                            </p>
                            
                            {result.album && result.album !== 'Unknown Album' && (
                                <p style={{ margin: '0 0 5px 0', color: '#888' }}>
                                    <strong>Album:</strong> {result.album}
                                </p>
                            )}
                            
                            {result.genres && result.genres !== 'Unknown' && (
                                <p style={{ margin: '0 0 5px 0', color: '#888' }}>
                                    <strong>Genre:</strong> {result.genres}
                                </p>
                            )}
                            
                            {result.release_date && result.release_date !== 'Unknown' && (
                                <p style={{ margin: '0 0 5px 0', color: '#888' }}>
                                    <strong>Released:</strong> {result.release_date}
                                </p>
                            )}
                            
                            <p style={{ 
                                margin: '10px 0', 
                                fontSize: '14px', 
                                color: '#4CAF50' 
                            }}>
                                ✓ Confidence: {(result.confidence * 100).toFixed(0)}%
                            </p>
                            
                            <div style={{ 
                                marginTop: '15px', 
                                display: 'flex', 
                                gap: '10px',
                                flexWrap: 'wrap'
                            }}>
                                {result.apple_music_url && (
                                    <a 
                                        href={result.apple_music_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        style={{
                                            padding: '8px 16px',
                                            backgroundColor: '#FC3C44',
                                            color: 'white',
                                            textDecoration: 'none',
                                            borderRadius: '5px',
                                            fontSize: '14px'
                                        }}
                                    >
                                        🎵 Apple Music
                                    </a>
                                )}
                                
                                {result.shazam_url && (
                                    <a 
                                        href={result.shazam_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        style={{
                                            padding: '8px 16px',
                                            backgroundColor: '#0088FF',
                                            color: 'white',
                                            textDecoration: 'none',
                                            borderRadius: '5px',
                                            fontSize: '14px'
                                        }}
                                    >
                                        📱 View on Shazam
                                    </a>
                                )}
                            </div>
                            
                            {result.latency_ms && (
                                <p style={{ 
                                    fontSize: '12px', 
                                    color: '#999', 
                                    marginTop: '15px' 
                                }}>
                                    Identified in {result.latency_ms.toFixed(0)}ms
                                </p>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {result && result.success && !result.track_found && (
                <div style={{
                    padding: '20px',
                    backgroundColor: '#fff3cd',
                    color: '#856404',
                    borderRadius: '5px',
                    marginTop: '20px',
                    textAlign: 'center'
                }}>
                    <div style={{ fontSize: '48px', marginBottom: '10px' }}>🤔</div>
                    <h3>No Music Found</h3>
                    <p>
                        We couldn't identify any music in the recording. 
                        Try recording closer to the audio source or ensure music is playing clearly.
                    </p>
                </div>
            )}

            <div style={{
                marginTop: '30px',
                padding: '15px',
                backgroundColor: '#e8f5e9',
                borderRadius: '5px',
                fontSize: '14px',
                color: '#2e7d32'
            }}>
                <strong>💡 Tips:</strong>
                <ul style={{ margin: '10px 0 0 20px', padding: 0 }}>
                    <li>Record for at least 5-10 seconds for best results</li>
                    <li>Ensure the music is clearly audible</li>
                    <li>Minimize background noise and conversation</li>
                    <li>The music should be the dominant sound in the recording</li>
                </ul>
            </div>
        </div>
    );
};

export default MusicIdentification;
