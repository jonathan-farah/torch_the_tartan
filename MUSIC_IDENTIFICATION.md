# 🎵 Music Identification with Shazam

## Overview
The app now includes Shazam-powered music identification! Record audio from your environment and instantly identify songs playing in the background.

## Features
- **Real-time Music Recognition**: Record audio and identify songs using Shazam's API
- **Rich Metadata**: Get song title, artist, album, genre, release date, and cover art
- **Quick Links**: Direct links to Apple Music and Shazam
- **Phoenix Monitoring**: All music identifications are logged for observability

## How to Use

### 1. Navigate to Music ID Tab
Click on the "🎵 Music ID" tab in the app

### 2. Start Recording
- Click "🎤 Start Listening" to begin recording
- Record for at least 5-10 seconds for best results
- The timer shows recording duration

### 3. Stop & Identify
- Click "⏹️ Stop & Identify" to analyze the audio
- The app sends the recording to Shazam API
- Results appear within seconds

### 4. View Results
If a match is found, you'll see:
- Song title and artist
- Album cover art
- Album name
- Genre and release date
- Confidence score
- Links to Apple Music and Shazam

## API Endpoints

### POST /api/identify-music
Identify music from audio recording

**Request:**
```json
{
  "audio": "data:audio/webm;base64,<base64_audio>",
  "duration": 10
}
```

**Response (Success):**
```json
{
  "success": true,
  "track_found": true,
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "genres": "Pop",
  "release_date": "2023",
  "cover_art": "https://...",
  "apple_music_url": "https://...",
  "shazam_url": "https://...",
  "confidence": 0.95,
  "latency_ms": 1234
}
```

**Response (No Match):**
```json
{
  "success": true,
  "track_found": false,
  "message": "No music match found",
  "latency_ms": 1234
}
```

### POST /api/search-music
Search for music by name, artist, or lyrics

**Request:**
```json
{
  "query": "Bohemian Rhapsody",
  "limit": 5
}
```

**Response:**
```json
{
  "success": true,
  "tracks": [
    {
      "title": "Bohemian Rhapsody",
      "artist": "Queen",
      "cover_art": "https://...",
      "shazam_url": "https://..."
    }
  ],
  "count": 1
}
```

## Configuration

### Environment Variables
Add to `backend/.env`:
```env
SHAZAM_API_KEY=your_shazam_api_key_here
```

### API Key
Get your Shazam API key from RapidAPI:
1. Visit https://rapidapi.com/apidojo/api/shazam
2. Subscribe to the API (free tier available)
3. Copy your API key
4. Add it to `.env` file

## Technical Details

### Backend Components
- **shazam_client.py**: Shazam API client with singleton pattern
- **Endpoints**: `/api/identify-music` and `/api/search-music`
- **Integration**: Logged to Phoenix for monitoring

### Frontend Component
- **MusicIdentification.js**: React component with audio recording
- **Features**: 
  - MediaRecorder API for audio capture
  - Real-time recording timer
  - Beautiful results display
  - Error handling

### Audio Format
- Recorded as `audio/webm` in browser
- Converted to base64 for API transmission
- Shazam processes raw audio bytes

## Tips for Best Results
- Record for at least 5-10 seconds
- Ensure music is clearly audible
- Minimize background noise and conversation
- The music should be the dominant sound
- Get close to the audio source if possible

## Monitoring
All music identifications are logged to Phoenix:
- Track: Song title and artist
- Confidence: Match confidence score
- Latency: API response time
- Audio duration: Length of recording

View metrics at: http://localhost:6006

## Troubleshooting

### "Shazam API not configured"
- Check that `SHAZAM_API_KEY` is set in `.env`
- Restart the backend server

### "No music match found"
- Record for longer (10+ seconds)
- Ensure music is clearly audible
- Try getting closer to audio source
- Check if the song is in Shazam's database

### "Request timeout"
- Check internet connection
- Shazam API may be temporarily unavailable
- Try again in a few moments

### "Failed to access microphone"
- Grant microphone permissions in browser
- Check browser security settings
- Ensure microphone is connected and working

## Future Enhancements
- [ ] Audio history and favorites
- [ ] Spotify integration
- [ ] Lyrics display
- [ ] Similar songs recommendations
- [ ] Playlist creation
- [ ] Offline caching of identifications

## License
This feature uses the Shazam API via RapidAPI. See RapidAPI terms of service for usage limits and restrictions.
