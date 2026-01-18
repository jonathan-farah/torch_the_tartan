import os
import requests
from typing import Optional, Dict, Any
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ShazamClient:
    """Client for Shazam API - music identification from audio"""
    
    def __init__(self):
        self.api_key = os.getenv('SHAZAM_API_KEY')
        self.base_url = 'https://shazam.p.rapidapi.com'
        
        if not self.api_key:
            print("Warning: SHAZAM_API_KEY not set. Music identification disabled.")
            self.enabled = False
        else:
            self.enabled = True
            print(f"✓ Shazam client initialized with API key")
    
    def identify_music(self, audio_base64: str) -> Dict[str, Any]:
        """
        Identify music from audio data
        
        Args:
            audio_base64: Base64 encoded audio data
            
        Returns:
            Dict with song title, artist, album, and other metadata
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Shazam API not configured'
            }
        
        try:
            # Remove data URI prefix if present
            if ',' in audio_base64:
                audio_base64 = audio_base64.split(',')[1]
            
            # Decode base64 to bytes
            audio_bytes = base64.b64decode(audio_base64)
            
            headers = {
                'X-RapidAPI-Key': self.api_key,
                'X-RapidAPI-Host': 'shazam.p.rapidapi.com',
                'Content-Type': 'text/plain'
            }
            
            # Shazam API expects the raw audio bytes
            response = requests.post(
                f'{self.base_url}/songs/v2/detect',
                headers=headers,
                params={'locale': 'en-US'},
                data=audio_bytes,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if a match was found
                if 'track' in result:
                    track = result['track']
                    
                    return {
                        'success': True,
                        'track_found': True,
                        'title': track.get('title', 'Unknown'),
                        'artist': track.get('subtitle', 'Unknown Artist'),
                        'album': track.get('sections', [{}])[0].get('metadata', [{}])[0].get('text', 'Unknown Album') if track.get('sections') else 'Unknown Album',
                        'genres': track.get('genres', {}).get('primary', 'Unknown'),
                        'release_date': track.get('sections', [{}])[0].get('metadata', [{}])[1].get('text', 'Unknown') if len(track.get('sections', [{}])[0].get('metadata', [])) > 1 else 'Unknown',
                        'cover_art': track.get('images', {}).get('coverart', ''),
                        'apple_music_url': track.get('url', ''),
                        'shazam_url': track.get('share', {}).get('href', ''),
                        'preview_url': track.get('hub', {}).get('actions', [{}])[0].get('uri', '') if track.get('hub', {}).get('actions') else '',
                        'confidence': 0.95  # Shazam doesn't provide confidence, assuming high if found
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
                    'error': f'Shazam API error: {response.status_code}',
                    'message': response.text
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout',
                'message': 'Shazam API request timed out after 30 seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Identification failed',
                'message': str(e)
            }
    
    def search_track(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Search for tracks by name, artist, or lyrics
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            Dict with list of matching tracks
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Shazam API not configured'
            }
        
        try:
            headers = {
                'X-RapidAPI-Key': self.api_key,
                'X-RapidAPI-Host': 'shazam.p.rapidapi.com'
            }
            
            response = requests.get(
                f'{self.base_url}/search',
                headers=headers,
                params={
                    'term': query,
                    'locale': 'en-US',
                    'limit': limit
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                
                tracks = []
                if 'tracks' in result and 'hits' in result['tracks']:
                    for hit in result['tracks']['hits']:
                        track = hit.get('track', {})
                        tracks.append({
                            'title': track.get('title', 'Unknown'),
                            'artist': track.get('subtitle', 'Unknown Artist'),
                            'cover_art': track.get('images', {}).get('coverart', ''),
                            'shazam_url': track.get('share', {}).get('href', '')
                        })
                
                return {
                    'success': True,
                    'tracks': tracks,
                    'count': len(tracks)
                }
            else:
                return {
                    'success': False,
                    'error': f'Search failed: {response.status_code}'
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
