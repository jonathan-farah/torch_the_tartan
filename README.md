# 🎭 Torch the Tartan
For questions or issues, consult the Arize documentation or open a GitHub issue.- Improve models over time with data-driven insights- Understand user behavior and model usage- Detect and fix issues quickly- Ensure models are working correctlyThe Arize integration provides production-grade observability for the Torch the Tartan ML models. By monitoring predictions, features, and performance, you can:## Conclusion```energy < 0.01mean_pitch > 500 OR mean_pitch < 50```### Find Unusual Audio Features```face_count > 1```### Find Multi-Face Scenarios```timestamp > now() - 24herror_type = "prediction_failure"```### Find Recent Errors```# Compare confidence and latencycached = falsecached = true```### Find Cached vs Non-Cached Performance```latency_ms > 1000```### Find Slow Predictions```prediction_score < 0.7```### Find Low-Confidence PredictionsHere are some useful queries to run in Arize:## Example Queries- [ ] Cohort analysis (performance by TV show, image quality, etc.)- [ ] Custom metrics (user feedback, corrections)- [ ] Real-time alerting to Slack/email- [ ] Prediction explanations (why this actor/person?)- [ ] Feature importance tracking- [ ] Model comparison (test new models vs production)- [ ] Actual labels (ground truth) for performance metricsPotential additions to monitoring:## Future Enhancements- **Arize Support**: Email support@arize.com for help- **GitHub Issues**: Report bugs in this repository- **Arize Slack**: Join the community Slack for support- **Arize Documentation**: [docs.arize.com](https://docs.arize.com)## Support Resources- **Optimization**: Cache hits don't reduce Arize logs (still logged)- **Paid Tier**: Consider if logging >1M predictions/month- **Free Tier**: Usually sufficient for development/testingFor this application:- Data retention period- Number of models monitored- Number of predictions logged per monthArize pricing is typically based on:## Cost Considerations- **Permissions**: Use read-only keys if only viewing data- **Rotation**: Rotate API keys periodically- **.gitignore**: Ensure `.env` is in `.gitignore`- **.env**: Never commit `.env` to version control- **API Key**: Keep your Arize API key secret## Security Considerations   - Fix common failure modes   - Review error patterns to improve robustness   - All errors are logged to Arize5. **Handle Errors Gracefully**:   - More features = better drift detection   - Features help debug issues later   - Log all relevant features (not just predictions)4. **Leverage Features**:   - Use Arize to compare versions   - Document what changed in each version   - Increment version when changing model logic3. **Update Model Versions**:   - Investigate anomalies promptly   - Review dashboard weekly   - Set up alerts for key metrics2. **Monitor Actively**:   - Examples: `voice-recognition-v2`, `face-detection-prod`   - Include version info if you plan to iterate   - Use descriptive names that indicate model purpose1. **Set Meaningful Model IDs**:## Best PracticesThe monitor will detect missing credentials and disable itself with a console warning.   ```   ARIZE_SPACE_ID=   ARIZE_API_KEY=   ```bash2. **Option 2 - Set to empty**:   ```   # ARIZE_SPACE_ID=...   # ARIZE_API_KEY=...   # In .env, comment out or remove:   ```bash1. **Option 1 - Remove credentials**:To disable Arize monitoring:## Disabling Arize- No impact on user experience- Predictions continue normally- Warnings logged to consoleIf Arize is unavailable or misconfigured:- **Failures**: Non-blocking (if Arize is down, app continues)- **Network**: Predictions batched and sent asynchronously- **Memory**: Minimal (batched sends)- **Latency**: ~5-10ms added to each prediction (async logging)The Arize integration is designed to be lightweight:## Performance Impact   - Review features that caused the error   - Check logged error messages   - Use `prediction_id` to find specific prediction3. **Trace Errors**:   - Look for patterns (e.g., all low-brightness images fail)   - Compare to successful predictions   - Check if problematic predictions have unusual features2. **Analyze Features**:   - Filter by specific time ranges   - Filter by high latency (> 1000ms)   - Filter by low confidence (< 0.5)1. **Find Problematic Predictions**:When investigating issues:### Troubleshooting with Arize4. Analyze confidence, latency, and feature differences3. Compare performance between versions in Arize2. Deploy your changes1. Update `ARIZE_MODEL_VERSION` in `.env` (e.g., `1.1.0`)To test model improvements:### A/B Testing   - Track null/missing values   - Detect corrupt or malformed inputs   - Monitor for outliers in features3. **Data Quality Issues**:   - Track prediction latency trends   - Alert if confidence drops below baseline   - Monitor average confidence scores2. **Performance Degradation**:   - Alert when distributions shift significantly   - Monitor image feature distributions (brightness, contrast)   - Monitor audio feature distributions (pitch, spectral centroid)1. **Drift Detection**:Set up monitors in Arize for:### Custom Monitors## Advanced Usage- Slowest predictions- Unusual feature combinations- Low-confidence predictions (< 0.7)- Recent errors (last 24 hours)#### Debugging Dashboard- Context usage (TV show names for voice model)- Multi-face detection rates (for face model)- Prediction label distribution (which actors/people most common)- Confidence score distribution#### Model Performance Dashboard- Data drift scores- Missing value rates- Outlier detection (unusual feature values)- Feature distribution histograms#### Data Quality Dashboard- Error rate- Cache hit rate trend- Throughput (predictions per minute)- Prediction latency over time (p50, p95, p99)#### Performance Dashboard### Common Dashboards to Create- **Alert**: Alert on error rate spikes- **Why**: Quality control and debugging- **What**: Percentage of failed predictions#### Error Rate- **Track**: Compare `cached=true` vs `cached=false` predictions- **Why**: Indicates caching effectiveness- **What**: Percentage of predictions served from cache#### Cache Hit Rate- **Alert**: Alert if p95 latency exceeds threshold- **Why**: Performance degradation impacts UX- **What**: Time to generate predictions (milliseconds)#### Latency- **Alert**: Set up drift detection monitors- **Why**: Detect data drift (inputs changing)- **What**: How input features change over time#### Feature Distributions- **Alert**: Alert if average confidence drops below threshold- **Why**: Declining confidence may indicate model drift- **What**: Distribution of prediction scores over time#### Confidence Scores- **Alert**: Set up alerts for unusual spikes or drops- **Why**: Understand usage patterns, detect anomalies- **What**: How many predictions per time period#### Prediction Volume### Key Metrics to Monitor   - `torch-tartan-face-recognition`   - `torch-tartan-voice-recognition`3. **Verify Models**: You should see two models:2. **Check Dashboard**: Log into Arize and navigate to your space1. **Wait for Data**: After configuration, make some predictions (voice/face identifications)### Initial Setup## Using the Arize Dashboard- `features_json`: Stringified features (if available)- `model_type`: `voice` or `face`- `error_message`: Exception message- `error_type`: Always `prediction_failure`When predictions fail:### Error Logging- Environment: `PRODUCTION`- Model version: `1.0.0`- Model ID: `torch-tartan-face-recognition`- `prediction_timestamp`: When prediction occurred- `prediction_id`: Unique UUID for each prediction**Metadata:**- `latency_ms`: Time to generate prediction- `prediction_score`: Confidence (0.0-1.0)- `prediction_label`: Identified person name**Predictions:**- `cached`: Whether result came from cache- `face_count`: Number of faces detected- `aspect_ratio`: Face bounding box aspect ratio- `sharpness`: Image sharpness (Laplacian variance)- `contrast`: Image contrast level- `mean_brightness`: Average brightness (0-255)- `face_confidence`: MediaPipe detection confidence- `dimensions`: Image dimensions (WxH)**Features:**Every face prediction logs:### Face Recognition Model- Environment: `PRODUCTION`- Model version: `1.0.0`- Model ID: `torch-tartan-voice-recognition`- `prediction_timestamp`: When prediction occurred- `prediction_id`: Unique UUID for each prediction**Metadata:**- `latency_ms`: Time to generate prediction- `prediction_score`: Confidence (0.0-1.0)- `prediction_label`: Identified voice actor name**Predictions:**- `cached`: Whether result came from cache- `context`: TV show name (if provided)- `tempo`: Detected tempo in BPM- `energy`: Audio energy level- `zcr_mean`: Zero-crossing rate (voice/noise indicator)- `spectral_centroid_mean`: Spectral brightness measure- `pitch_std`: Pitch variation (standard deviation)- `mean_pitch`: Average pitch in Hz**Features:**Every voice prediction logs:### Voice Recognition Model## What Gets Logged   - Paste into `.env` as `ARIZE_SPACE_ID`   - Find Space ID in settings   - Open your space in the dashboard3. **Get Space ID**:   - Paste into `.env` as `ARIZE_API_KEY`   - Copy your API Key (JWT token format)   - Navigate to Account Settings2. **Get API Key**:   - Create a new space for your project   - Create an account (free tier available)   - Visit [arize.com](https://arize.com)1. **Sign up for Arize**:### Getting Your Credentials```ARIZE_MODEL_VERSION=1.0.0ARIZE_MODEL_ID_FACE=torch-tartan-face-recognitionARIZE_MODEL_ID_VOICE=torch-tartan-voice-recognition# Optional (defaults provided)ARIZE_SPACE_ID=your_space_id_hereARIZE_API_KEY=your_jwt_token_here# Required```bash### Environment Variables## Configuration   - Model version   - Model identifiers (voice, face)   - API credentials (key, space ID)3. **.env Configuration**: Environment variables for Arize   - Error handling: Logs failures with context   - Face endpoint: Logs image features, predictions, and face counts   - Voice endpoint: Logs audio features, predictions, and latency2. **app.py Integration**: Both API endpoints are instrumented   - `log_error()`: Logs prediction failures for debugging   - `log_face_prediction()`: Logs face recognition predictions   - `log_voice_prediction()`: Logs voice recognition predictions   - `ArizeMonitor` class: Manages Arize client and logging1. **arize_monitor.py**: Core monitoring module### Components## Architecture- Monitor system performance (latency, throughput)- Analyze feature distributions over time- Debug issues with specific predictions- Detect model drift and performance degradation- Track model predictions in real-timeArize AI provides production-grade machine learning monitoring, helping you:## OverviewThis document explains how the Torch the Tartan application integrates with Arize AI for ML observability and monitoring.A web application that uses AI to identify voice actors from TV shows and recognize people from photos. Built with React and Flask, leveraging machine learning for audio analysis and facial recognition with production-grade ML monitoring via Arize AI.

## Features

- **🎤 Voice Actor Identification**: Record audio from TV shows and identify voice actors using LLM-powered analysis
- **📸 Facial Recognition**: Capture or upload photos to identify people using computer vision
- **👁️ Real Computer Vision**: MediaPipe & OpenCV face detection with bounding boxes and landmarks
- **👥 Multi-Face Detection**: Detect and analyze multiple faces in a single image
- **🎬 Notable Projects**: View the actor's filmography and notable works alongside identification
- **⚡ Smart Caching**: Results are cached in a SQLite database for instant lookup on repeated searches
- **🔴 Live Detection Mode**: Optional real-time face detection preview from camera
- **📊 Detailed Analysis**: Face features including sharpness, brightness, contrast, and orientation
- **🎨 Modern UI**: Beautiful, responsive interface with real-time feedback and visualizations
- **🔊 Audio Analysis**: Extract acoustic features like pitch, spectral centroid, MFCCs, and more
- **🤖 AI-Powered**: Integrates with LLMs (OpenAI, Anthropic) for intelligent identification
- **📈 ML Observability**: Real-time model monitoring and performance tracking with Arize AI

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
- OpenCV for image processing and face detection
- MediaPipe for facial landmarks and features
- NumPy for feature extraction
- Flask-CORS for cross-origin requests
- SQLite for caching recognition results
- Arize AI for ML monitoring and observability
- pandas for data processing

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

5. Configure Arize AI (optional but recommended):
- Sign up for [Arize AI](https://arize.com) if you don't have an account
- Get your Space ID from the Arize dashboard
- Update `.env` with your Arize credentials:
```
ARIZE_API_KEY=your_api_key_here
ARIZE_SPACE_ID=your_space_id_here
```

6. (Optional) Add your LLM API keys to `.env`:
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
7. View the results including:
   - Actor name
   - Notable projects and filmography
   - Confidence score
   - Audio features
   - Cache status (if previously searched)
7. View the results including confidence score and audio features

### Facial Recognition

1. Click the **Face Recogniti:
   - Person name
   - Notable projects and filmography
   - Confidence score
   - Detected features
   - Cache status (if previously searched)
2. Either:
   - Click **Start Camera** to take a photo, or
   - Click **Upload Image** to select an existing photo
3. Click **Identify Person** to analyze the face
4. View the results including confidence score and detected features

## Advanced Configuration

## Advanced Configuration

### ML Monitoring with Arize AI

The application includes production-grade ML monitoring via Arize AI to track model performance, detect drift, and debug issues.

#### What Gets Monitored

**Voice Recognition Model:**
- Prediction labels (actor names)
- Confidence scores
- Audio features (pitch, spectral centroid, zero-crossing rate, energy, tempo, MFCCs)
- Prediction latency
- Cache hit rates
- Context information (TV show names)

**Face Recognition Model:**
- Prediction labels (person names)
- Confidence scores
- Image features (brightness, contrast, sharpness, aspect ratio, face dimensions)
- Detection confidence from MediaPipe
- Number of faces detected
- Prediction latency
- Cache hit rates

#### Setting Up Arize

1. **Create an Arize Account**:
   - Sign up at [arize.com](https://arize.com)
   - Create a new space for this project

2. **Get Your Credentials**:
   - API Key: Found in your account settings
   - Space ID: Found in your space settings

3. **Configure `.env`**:
```
ARIZE_API_KEY=your_api_key_here
ARIZE_SPACE_ID=your_space_id_here
ARIZE_MODEL_ID_VOICE=torch-tartan-voice-recognition
ARIZE_MODEL_ID_FACE=torch-tartan-face-recognition
ARIZE_MODEL_VERSION=1.0.0
```

4. **View Your Dashboards**:
   - Log into Arize and navigate to your space
   - View real-time predictions, performance metrics, and alerts
   - Set up monitors for model drift, data quality issues, and performance degradation

#### What You Can Track

- **Prediction Volume**: How many predictions per day/hour
- **Confidence Distribution**: Are confidence scores stable or declining?
- **Feature Drift**: Are input features changing over time?
- **Performance Metrics**: Latency trends and cache effectiveness
- **Error Rates**: Track failed predictions and their causes
- **Data Quality**: Detect anomalies in audio/image features

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
│   ├── database.py            # SQLite caching system
│   ├── face_detection.py      # MediaPipe/OpenCV face detection
│   ├── arize_monitor.py       # Arize AI monitoring integration
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   ├── .env                  # Environment configuration (create from .env.example)
│   ├── recognition_cache.db  # SQLite database (generated)
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
├── CACHING_IMPLEMENTATION.md  # Cache system documentation
└── README.md                 # This file
```
│   │   │   ├── VoiceRecognition.js    # Voice analysis component
│   │   │   ├── VoiceRecognition.css
│   │   │   ├── FaceRecognition.js     # Face recognition component
│   │   │   └── FaceRecognition.css
│   │   ├── App.js            # Main app component
│   │   ├── App.css
│   │   ├── index.js          # React entry point
│   │   └── index.css
│   └GET /api/cache-stats`
Get cache statistics including number of cached entries and total hits

### `POST /api/clear-cache`
Clear all cached recognition results

### `POST /api/analyze-voice`
Analyze audio and identify voice actor
- **Body**: `{ "audio": "base64_encoded_audio", "context": "optional_tv_show_name" }`
- **Returns**: Actor name, notable projects, confidence score, audio features, and cache status

### `POST /api/analyze-face`
Analyze image and identify person using computer vision
- **Body**: `{ "image": "base64_encoded_image" }`
- **Returns**: Person name, notable projects, confidence score, detected features, face count, annotated image with bounding boxes, landmarks, and cache status

### `POST /api/analyze-voice`
Analyze audio and identify voice actor
- **Body**: `{ "audio": "base64_encoded_audio", "context": "optional_tv_show_name" }`
- **Returns**: Voice actor information, confidence score, and audio features

### `POST /api/analyze-face`
Analyze image and identify person
- **Body**: `{ "image": "base64_encoded_image" }`
- **Returns**: Person information, confidence score, and detected features

## Computer Vision Features

### Face Detection
- **MediaPipe Face Detection**: High-accuracy face detection with confidence scores
- **Bounding Boxes**: Visual overlays showing detected face locations
- **Multiple Faces**: Support for detecting and analyzing multiple faces in one image
- **Face Landmarks**: 468-point facial landmark detection using MediaPipe Face Mesh
- **Quality Analysis**: Automatic assessment of image quality and face orientation

### Extracted Features
- Face bounding box coordinates
- Face dimensions and size
- Brightness and contrast analysis
- Image sharpness measurement
- Face orientation (frontal, profile, angle)
- Color analysis (RGB values)
- Key facial points (eyes, nose, mouth)

### Live Detection Mode
- Real-time face detection preview (optional)
- Visual feedback during camera usage
- Toggle on/off during camera session

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
x] Database caching for faster repeated lookups
- [x] Display actor filmography and notable projects
- [ ] Build database of known voices/faces for matching
- [ ] Real-time streaming analysis
- [ ] Multi-person detection in images
- [ ] Voice cloning detection
- [ ] Export analysis results
- [ ] Support for video files
- [ ] Integration with IMDb/TMDB APIs
- [ ] User accounts and history
- [ ] Analytics dashboard for cache performancePI endpoints in production
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

### Arize Not Logging Predictions
- Verify `ARIZE_API_KEY` and `ARIZE_SPACE_ID` are set in `.env`
- Check backend console for Arize initialization messages
- Ensure internet connectivity (Arize requires network access)
- Check Arize dashboard for incoming predictions (may take a few minutes)

## License

MIT License - feel free to use this project for any purpose.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [librosa](https://librosa.org/) for audio analysis
- [React](https://react.dev/) for the frontend framework
- [Flask](https://flask.palletsprojects.com/) for the backend server
- [OpenCV](https://opencv.org/) for computer vision
- [MediaPipe](https://mediapipe.dev/) for face detection and landmarks
- [Arize AI](https://arize.com/) for ML observability and monitoring
- [OpenAI](https://openai.com/)/[Anthropic](https://anthropic.com/) for LLM capabilities