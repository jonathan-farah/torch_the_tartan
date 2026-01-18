import os
import requests
import base64
import tempfile
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ShazamClient:
    """Client for Music Identification using AudD.io API (free tier)"""
    
    def __init__(self):
        # AudD.io API - you can use 'test' as demo key or get a free key at https://audd.io
        self.api_key = os.getenv('AUDD_API_KEY', 'test')
        self.base_url = 'https://api.audd.io/'
        self.enabled = True
        print(f"✓ Music identification client initialized (AudD.io free API)")
    
    def identify_music(self, audio_base64: str) -> Dict[str, Any]:
        """
        Identify music from audio data using AudD.io API
        
        Args:
            audio_base64: Base64 encoded audio data
            
        Returns:
            Dict with song title, artist, album, and other metadata
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Music identification not configured'
            }
        
        try:
            # Remove data URI prefix if present
            if ',' in audio_base64:
                audio_base64 = audio_base64.split(',')[1]
            
            # Decode base64 to bytes
            audio_bytes = base64.b64decode(audio_base64)
            
            # Save to temporary file (AudD.io accepts file uploads)
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name
            
            try:
                # Send to AudD.io API
                with open(temp_path, 'rb') as audio_file:
                    response = requests.post(
                        self.base_url,
                        data={'api_token': self.api_key, 'return': 'apple_music,spotify'},
                        files={'file': audio_file},
                        timeout=30
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check if a match was found
                    if result.get('status') == 'success' and result.get('result'):
                        track = result['result']
                        
                        return {
                            'success': True,
                            'track_found': True,
                            'title': track.get('title', 'Unknown'),
                            'artist': track.get('artist', 'Unknown Artist'),
                            'album': track.get('album', 'Unknown Album'),
                            'genres': ', '.join(track.get('genres', [])) if track.get('genres') else 'Unknown',
                            'release_date': track.get('release_date', 'Unknown'),
                            'cover_art': track.get('apple_music', {}).get('artwork', {}).get('url', '').replace('{w}', '500').replace('{h}', '500') if track.get('apple_music') else '',
                            'apple_music_url': track.get('apple_music', {}).get('url', ''),
                            'spotify_url': track.get('spotify', {}).get('external_urls', {}).get('spotify', ''),
                            'shazam_url': '',
                            'preview_url': track.get('spotify', {}).get('preview_url', ''),
                            'confidence': 0.90
                        }
                    else:
                        return {
                            'success': True,
                            'track_found': False,
                            'message': 'No music match found'
                        }
                else:
                    return {
                        'success': False,
                        'error': f'AudD.io API error: {response.status_code}',
                        'message': response.text
                    }
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout',
                'message': 'The music identification service took too long to respond'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'message': str(e)
            }
    
    def search_track(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Search for tracks by name, artist, or lyrics using AudD.io API"""
        try:
            response = requests.get(
                f'{self.base_url}/findLyrics/',
                params={
                    'api_token': self.api_key,
                    'q': query
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('status') == 'success' and result.get('result'):
                    tracks = [result['result']] if not isinstance(result['result'], list) else result['result']
                    
                    return {
                        'success': True,
                        'tracks': [{
                            'title': track.get('title', 'Unknown'),
                            'artist': track.get('artist', 'Unknown Artist'),
                            'album': track.get('album', 'Unknown Album'),
                            'cover_art': '',
                            'preview_url': ''
                        } for track in tracks[:limit]]
                    }
                else:
                    return {
                        'success': True,
                        'tracks': []
                    }
            else:
                return {
                    'success': False,
                    'error': f'Search error: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
_shazam_client = None

def get_shazam_client() -> ShazamClient:
    """Get or create the Shazam client singleton"""
    global _shazam_client
    if _shazam_client is None:
        _shazam_client = ShazamClient()
    return _shazam_client
