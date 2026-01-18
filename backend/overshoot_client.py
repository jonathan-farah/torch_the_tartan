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
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = 'https://api.overshoot.io/v1'
        
        if not self.api_key:
            print("Warning: OVERSHOOT_API_KEY not set. Will use OpenAI fallback for scene interpretation.")
            self.enabled = False
        else:
            self.enabled = True
            print(f"✓ Overshoot client initialized with API key")
    
    def analyze_scene_with_openai(self, image_base64: str, context: str = '') -> Dict[str, Any]:
        """
        Fallback scene analysis using OpenAI GPT-4o Vision
        """
        if not self.openai_api_key:
            return {
                'success': False,
                'error': 'No API available for scene analysis (Overshoot unavailable, OpenAI not configured)'
            }
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            # Remove data URI prefix if present
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            prompt = f"""Analyze this scene image and provide a detailed interpretation.

Context: {context if context else 'General scene analysis'}

Please provide:
1. Scene Description: What is happening in this scene?
2. Visual Elements: What objects, people, or notable elements are present?
3. Mood/Atmosphere: What is the emotional tone or atmosphere?
4. Setting: Where does this appear to be taking place?

Return your analysis in a clear, structured format."""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            analysis = response.choices[0].message.content
            
            return {
                'success': True,
                'scene_description': analysis,
                'interpretation': analysis,
                'provider': 'OpenAI GPT-4o Vision',
                'confidence': 0.85
            }
            
        except Exception as e:
            print(f"OpenAI scene analysis error: {e}")
            return {
                'success': False,
                'error': f'Scene analysis failed: {str(e)}'
            }
    
    def analyze_scene(self, image_base64: str, context: str = '') -> Optional[Dict[str, Any]]:
        """
        Analyze a scene from an image and provide interpretation
        Tries Overshoot first, falls back to OpenAI if unavailable
        
        Args:
            image_base64: Base64 encoded image
            context: Optional context about what to focus on (e.g., "TV show scene")
            
        Returns:
            Dict with scene description, interpretation, and detected elements
        """
        # Try Overshoot API first if enabled
        if self.enabled:
            try:
                # Remove data URI prefix if present
                clean_image = image_base64.split(',')[1] if ',' in image_base64 else image_base64
                
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'image': clean_image,
                    'context': context
                }
                
                response = requests.post(
                    f'{self.base_url}/analyze',
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return {
                        'success': True,
                        'data': response.json(),
                        'provider': 'Overshoot'
                    }
                else:
                    print(f"Overshoot API error {response.status_code}, trying OpenAI fallback...")
                    
            except requests.exceptions.ConnectionError as e:
                print(f"Overshoot API unavailable (DNS/connection error), using OpenAI fallback...")
            except requests.exceptions.Timeout:
                print(f"Overshoot API timeout, using OpenAI fallback...")
            except Exception as e:
                print(f"Overshoot error: {e}, using OpenAI fallback...")
        
        # Fallback to OpenAI
        return self.analyze_scene_with_openai(image_base64, context)
    
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
