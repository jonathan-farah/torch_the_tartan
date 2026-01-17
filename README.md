# 🎭 Torch the Tartan

A web application that uses AI to identify voice actors from TV shows and recognize people from photos. Built with React and Flask, leveraging machine learning for audio analysis and facial recognition.

## Features

- **🎤 Voice Actor Identification**: Record audio from TV shows and identify voice actors using LLM-powered analysis
- **📸 Facial Recognition**: Capture or upload photos to identify people using computer vision
- **🎨 Modern UI**: Beautiful, responsive interface with real-time feedback
- **🔊 Audio Analysis**: Extract acoustic features like pitch, spectral centroid, MFCCs, and more
- **🤖 AI-Powered**: Integrates with LLMs (OpenAI, Anthropic) for intelligent identification

## Tech Stack

### Frontend
- React 18
- Axios for API calls
- MediaRecorder API for audio capture
- getUserMedia API for camera access
- Responsive CSS with animations

### Backend
- Python Flask
- librosa for audio analysis
- PIL for image processing
- NumPy for feature extraction
- Flask-CORS for cross-origin requests

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- pip and npm

### Backend Setup

1. Navigate to the backend directory:
```powershell
cd backend
```

2. Create a virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install dependencies:
```powershell
pip install -r requirements.txt
```

4. Create environment file:
```powershell
cp .env.example .env
```

5. (Optional) Add your LLM API keys to `.env`:
```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

### Frontend Setup

1. Navigate to the frontend directory:
```powershell
cd frontend
```

2. Install dependencies:
```powershell
npm install
```

## Running the Application

### Start the Backend

From the `backend` directory:
```powershell
.\venv\Scripts\Activate.ps1
python app.py
```

The backend will run on `http://localhost:5000`

### Start the Frontend

From the `frontend` directory:
```powershell
npm start
```

The frontend will run on `http://localhost:3000`

## Usage

### Voice Actor Identification

1. Click the **Voice Recognition** tab
2. (Optional) Enter TV show context for better results
3. Click **Start Recording** to capture audio
4. Play audio from your TV show
5. Click **Stop Recording** when done
6. Click **Analyze Voice** to identify the voice actor
7. View the results including confidence score and audio features

### Facial Recognition

1. Click the **Face Recognition** tab
2. Either:
   - Click **Start Camera** to take a photo, or
   - Click **Upload Image** to select an existing photo
3. Click **Identify Person** to analyze the face
4. View the results including confidence score and detected features

## Advanced Configuration

### Integrating with Real LLM APIs

To get actual voice actor identifications (instead of placeholders), integrate with an LLM:

1. Uncomment the LLM package in `backend/requirements.txt`:
```python
openai==1.10.0  # or
anthropic==0.8.1
```

2. Install the package:
```powershell
pip install openai  # or anthropic
```

3. Update the `identify_voice_actor_with_llm()` function in `backend/app.py` to call the API

### Adding Real Facial Recognition

To get actual facial recognition (instead of placeholders):

1. Uncomment face recognition packages in `backend/requirements.txt`:
```python
face-recognition==1.3.0
opencv-python==4.9.0.80
```

2. Install the packages:
```powershell
pip install face-recognition opencv-python
```

3. Update the `identify_person_from_face()` function in `backend/app.py` to use face_recognition library

## Project Structure

```
torch_the_tartan/
├── backend/
│   ├── app.py                 # Flask server with API endpoints
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   └── uploads/              # Temporary file storage
├── frontend/
│   ├── public/
│   │   └── index.html        # HTML template
│   ├── src/
│   │   ├── components/
│   │   │   ├── VoiceRecognition.js    # Voice analysis component
│   │   │   ├── VoiceRecognition.css
│   │   │   ├── FaceRecognition.js     # Face recognition component
│   │   │   └── FaceRecognition.css
│   │   ├── App.js            # Main app component
│   │   ├── App.css
│   │   ├── index.js          # React entry point
│   │   └── index.css
│   └── package.json          # Node dependencies
├── .gitignore
└── README.md
```

## API Endpoints

### `GET /health`
Check server status

### `POST /api/analyze-voice`
Analyze audio and identify voice actor
- **Body**: `{ "audio": "base64_encoded_audio", "context": "optional_tv_show_name" }`
- **Returns**: Voice actor information, confidence score, and audio features

### `POST /api/analyze-face`
Analyze image and identify person
- **Body**: `{ "image": "base64_encoded_image" }`
- **Returns**: Person information, confidence score, and detected features

## Audio Features Extracted

- Mean Pitch (Hz)
- Pitch Standard Deviation
- Spectral Centroid
- Zero Crossing Rate
- MFCCs (Mel-frequency cepstral coefficients)
- Energy Level
- Tempo (BPM)

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support (requires HTTPS for camera/microphone)
- Mobile browsers: ✅ Supported

**Note**: Camera and microphone access requires HTTPS in production or localhost in development.

## Security Considerations

- Never commit `.env` files with real API keys
- Use HTTPS in production for secure media access
- Implement rate limiting for API endpoints in production
- Sanitize and validate all user inputs
- Consider adding authentication for production deployments

## Future Enhancements

- [ ] Build database of known voices/faces for matching
- [ ] Real-time streaming analysis
- [ ] Multi-person detection in images
- [ ] Voice cloning detection
- [ ] Export analysis results
- [ ] Support for video files
- [ ] Integration with IMDb/TMDB APIs
- [ ] User accounts and history

## Troubleshooting

### Camera/Microphone Not Working
- Check browser permissions
- Ensure you're on HTTPS or localhost
- Try a different browser

### Backend Errors
- Verify Python version (3.8+)
- Check all dependencies are installed
- Review backend console logs

### Frontend Not Connecting to Backend
- Ensure backend is running on port 5000
- Check CORS settings in `backend/app.py`
- Verify proxy setting in `frontend/package.json`

## License

MIT License - feel free to use this project for any purpose.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- librosa for audio analysis
- React for the frontend framework
- Flask for the backend server
- OpenAI/Anthropic for LLM capabilities