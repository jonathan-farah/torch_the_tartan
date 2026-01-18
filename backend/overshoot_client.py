import os
import requests
from typing import Optional, Dict, Any
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OvershootClient:
    """Client for Overshoot API - scene understanding and interpretation"""
    
    def __init__(self):
        self.api_key = os.getenv('OVERSHOOT_API_KEY')
        self.base_url = 'https://api.overshoot.io/v1'
        
        if not self.api_key:
            print("Warning: OVERSHOOT_API_KEY not set. Scene interpretation disabled.")
            self.enabled = False
        else:
            self.enabled = True
            print(f"✓ Overshoot client initialized with API key")
    
    def analyze_scene(self, image_base64: str, context: str = '') -> Optional[Dict[str, Any]]:
        """
        Analyze a scene from an image and provide interpretation
        
        Args:
            image_base64: Base64 encoded image
            context: Optional context about what to focus on (e.g., "TV show scene")
            
        Returns:
            Dict with scene description, interpretation, and detected elements
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Overshoot API not configured'
            }
        
        try:
            # Remove data URI prefix if present
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            prompt = "Analyze this image and provide: 1) A detailed description of the scene, 2) What's happening, 3) Notable elements or people, 4) The mood/atmosphere."
            if context:
                prompt = f"{prompt} Context: {context}"
            
            payload = {
                'image': image_base64,
                'prompt': prompt,
                'max_tokens': 500
            }
            
            response = requests.post(
                f'{self.base_url}/analyze',
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'scene_description': result.get('description', ''),
                    'interpretation': result.get('analysis', ''),
                    'elements': result.get('elements', []),
                    'mood': result.get('mood', ''),
                    'confidence': result.get('confidence', 0.0)
                }
            else:
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}',
                    'message': response.text
                }
                
        except Exception as e:
            print(f"Error calling Overshoot API: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def interpret_with_faces(
        self, 
        image_base64: str, 
        detected_faces: list,
        identified_people: list = None,
        context: str = ''
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze scene with knowledge of detected faces
        
        Args:
            image_base64: Base64 encoded image
            detected_faces: List of face detection results
            identified_people: List of identified person names
            context: Optional context (e.g., TV show name)
            
        Returns:
            Enhanced scene interpretation with face context
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Overshoot API not configured'
            }
        
        try:
            # Build context with face information
            face_context = f"Detected {len(detected_faces)} face(s) in the image."
            if identified_people:
                face_context += f" Identified people: {', '.join(identified_people)}."
            
            if context:
                face_context = f"{context}. {face_context}"
            
            # Remove data URI prefix if present
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            prompt = f"""Analyze this scene with the following context: {face_context}
            
Provide:
1. What's happening in the scene
2. The interaction between people (if multiple)
3. The setting and atmosphere
4. What this scene might be about (if it's from a show/movie)
"""
            
            payload = {
                'image': image_base64,
                'prompt': prompt,
                'max_tokens': 600
            }
            
            response = requests.post(
                f'{self.base_url}/analyze',
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'scene_interpretation': result.get('description', ''),
                    'interaction_analysis': result.get('analysis', ''),
                    'setting': result.get('setting', ''),
                    'story_context': result.get('context', ''),
                    'confidence': result.get('confidence', 0.0),
                    'detected_faces_count': len(detected_faces)
                }
            else:
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}',
                    'message': response.text
                }
                
        except Exception as e:
            print(f"Error calling Overshoot API: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Global client instance
_client = None

def get_overshoot_client() -> OvershootClient:
    """Get or create global Overshoot client instance"""
    global _client
    if _client is None:
        _client = OvershootClient()
    return _client
