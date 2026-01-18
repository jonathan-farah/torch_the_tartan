from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
import io
from datetime import datetime
import time
import numpy as np
from PIL import Image
import librosa
import soundfile as sf
import database
import cv2
from face_detection import get_detector
from phoenix_monitor import get_monitor
from overshoot_client import get_overshoot_client
from shazam_client import get_shazam_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Phoenix monitor
phoenix_monitor = get_monitor()

# Initialize Overshoot client
overshoot_client = get_overshoot_client()

# Initialize Shazam client
shazam_client = get_shazam_client()

# Create uploads directory
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'Server is running'}), 200

@app.route('/api/cache-stats', methods=['GET'])
def cache_stats():
    """
    Get cache statistics
    """
    stats = database.get_cache_stats()
    return jsonify(stats), 200

@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """
    Clear all cache entries
    """
    try:
        database.clear_cache()
        return jsonify({'success': True, 'message': 'Cache cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-voice', methods=['POST'])
def analyze_voice():
    """
    Analyze audio and identify voice actor using LLM
    """
    start_time = time.time()
    
    try:
        data = request.json
        
        if 'audio' not in data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Decode base64 audio
        audio_data = base64.b64decode(data['audio'].split(',')[1] if ',' in data['audio'] else data['audio'])
        
        # Save temporary file with appropriate extension
        # Try to detect format from base64 header
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if 'data:audio/webm' in data['audio']:
            audio_path = os.path.join(UPLOAD_FOLDER, f'voice_{timestamp}.webm')
        elif 'data:audio/wav' in data['audio']:
            audio_path = os.path.join(UPLOAD_FOLDER, f'voice_{timestamp}.wav')
        else:
            # Default to webm as most browsers use this
            audio_path = os.path.join(UPLOAD_FOLDER, f'voice_{timestamp}.webm')
        
        with open(audio_path, 'wb') as f:
            f.write(audio_data)
        
        # Load and analyze audio
        y, sr = librosa.load(audio_path, sr=None)
        
        # Extract audio features
        features = extract_voice_features(y, sr)
        
        # Check cache first
        context = data.get('context', '')
        cached_result = database.get_cached_voice_result(features, context)
        
        if cached_result:
            # Return cached result - convert to new multi-actor format
            actors = [{
                'name': cached_result['actor_name'],
                'notable_projects': cached_result['notable_projects'],
                'confidence': cached_result['confidence']
            }]
            
            os.remove(audio_path)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Log to Phoenix
            phoenix_monitor.log_voice_prediction(
                features=features,
                prediction=cached_result['actor_name'],
                confidence=cached_result['confidence'],
                context=context,
                cached=True,
                latency_ms=latency_ms
            )
            
            return jsonify({
                'success': True,
                'actors': actors,
                'total_speakers': 1,
                'features': features,
                'cached': True,
                'cache_hits': cached_result['cache_hits']
            }), 200
        
        # Use LLM to identify voice actor (placeholder for now)
        voice_actor_info = identify_voice_actor_with_llm(features, context)
        
        # Handle multiple actors response
        actors = voice_actor_info.get('actors', [])
        
        if not actors:
            # Fallback for backward compatibility
            actors = [{
                'name': voice_actor_info.get('name', 'Unknown'),
                'notable_projects': voice_actor_info.get('notable_projects', []),
                'confidence': voice_actor_info.get('confidence', 0.5)
            }]
        
        # Cache each actor result
        for actor in actors:
            database.cache_voice_result(
                features,
                actor['name'],
                actor['notable_projects'],
                actor['confidence'],
                context
            )
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Log primary actor to Phoenix
        if actors:
            phoenix_monitor.log_voice_prediction(
                features=features,
                prediction=actors[0]['name'],
                confidence=actors[0]['confidence'],
                context=context,
                cached=False,
                latency_ms=latency_ms
            )
        
        # Clean up
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return jsonify({
            'success': True,
            'actors': actors,
            'total_speakers': len(actors),
            'features': features,
            'cached': False
        }), 200
        
    except Exception as e:
        # Clean up audio file if it exists
        if 'audio_path' in locals() and os.path.exists(audio_path):
            os.remove(audio_path)
        
        # Log error to Phoenix
        phoenix_monitor.log_error('voice', str(e), features if 'features' in locals() else None)
        print(f"Voice analysis error: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-face', methods=['POST'])
def analyze_face():
    """
    Analyze image and identify person using facial recognition
    """
    start_time = time.time()
    
    try:
        data = request.json
        
        if 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = base64.b64decode(data['image'].split(',')[1] if ',' in data['image'] else data['image'])
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to numpy array for OpenCV
        image_array = np.array(image)
        if len(image_array.shape) == 2:  # Grayscale
            image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2BGR)
        elif image_array.shape[2] == 4:  # RGBA
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2BGR)
        elif image_array.shape[2] == 3:  # RGB
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Save temporary file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_path = os.path.join(UPLOAD_FOLDER, f'face_{timestamp}.jpg')
        cv2.imwrite(image_path, image_array)
        
        # Detect faces using computer vision
        detector = get_detector()
        detected_faces = detector.detect_faces(image_array)
        
        if not detected_faces:
            os.remove(image_path)
            return jsonify({
                'success': False,
                'error': 'No faces detected in the image',
                'face_count': 0
            }), 200
        
        # Get landmarks for first face
        landmarks_data = detector.detect_landmarks(image_array)
        
        # Identify all detected people
        identified_people = []
        for face in detected_faces:
            person_info = identify_person_from_face_features(face, image_array)
            identified_people.append({
                'name': person_info['name'],
                'notable_projects': person_info['notable_projects'],
                'confidence': person_info['confidence'],
                'bbox': face['bbox'],
                'face_confidence': face['confidence']
            })
        
        # Draw detections on image
        annotated_image = detector.draw_detections(image_array, detected_faces)
        annotated_base64 = detector.encode_image_to_base64(annotated_image)
        
        # Cache all identified people
        for person in identified_people:
            # Create simple features dict for caching
            cache_features = {
                'bbox': str(person['bbox']),
                'face_confidence': person['face_confidence']
            }
            database.cache_face_result(
                cache_features,
                person['name'],
                person['notable_projects'],
                person['confidence']
            )
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Log primary person to Phoenix
        if identified_people:
            phoenix_monitor.log_face_prediction(
                features={'face_count': len(detected_faces)},
                prediction=identified_people[0]['name'],
                confidence=identified_people[0]['confidence'],
                face_count=len(detected_faces),
                cached=False,
                latency_ms=latency_ms
            )
        
        os.remove(image_path)
        
        return jsonify({
            'success': True,
            'people': identified_people,
            'total_people': len(identified_people),
            'face_count': len(detected_faces),
            'faces': detected_faces,
            'landmarks': landmarks_data,
            'annotated_image': f'data:image/jpeg;base64,{annotated_base64}',
            'cached': False
        }), 200
        
    except Exception as e:
        # Log error to Phoenix
        phoenix_monitor.log_error('face', str(e), image_features if 'image_features' in locals() else None)
        return jsonify({'error': str(e)}), 500

@app.route('/api/interpret-scene', methods=['POST'])
def interpret_scene():
    """
    Interpret a scene using Overshoot AI - understand what's happening
    """
    start_time = time.time()
    
    try:
        data = request.json
        
        if 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        image_data = data['image']
        context = data.get('context', '')
        
        # Get scene interpretation from Overshoot
        result = overshoot_client.analyze_scene(image_data, context)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'scene_description': result.get('scene_description', ''),
                'interpretation': result.get('interpretation', ''),
                'elements': result.get('elements', []),
                'mood': result.get('mood', ''),
                'confidence': result.get('confidence', 0.0),
                'latency_ms': latency_ms
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'message': result.get('message', '')
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-face-with-scene', methods=['POST'])
def analyze_face_with_scene():
    """
    Enhanced face analysis with scene interpretation using Overshoot
    """
    start_time = time.time()
    
    try:
        data = request.json
        
        if 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = base64.b64decode(data['image'].split(',')[1] if ',' in data['image'] else data['image'])
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to numpy array for OpenCV
        image_array = np.array(image)
        if len(image_array.shape) == 2:  # Grayscale
            image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2BGR)
        elif image_array.shape[2] == 4:  # RGBA
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2BGR)
        elif image_array.shape[2] == 3:  # RGB
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Detect faces
        detector = get_detector()
        detected_faces = detector.detect_faces(image_array)
        
        if not detected_faces:
            # Still try to interpret the scene even without faces
            result = overshoot_client.analyze_scene(data['image'], data.get('context', ''))
            latency_ms = (time.time() - start_time) * 1000
            
            return jsonify({
                'success': True,
                'face_count': 0,
                'scene_interpretation': result.get('scene_description', 'No interpretation available'),
                'interpretation': result.get('interpretation', ''),
                'latency_ms': latency_ms
            }), 200
        
        # Get primary face info
        primary_face = detected_faces[0]
        person_info = identify_person_from_face_features(primary_face, image_array)
        
        # Get identified people names
        identified_people = [person_info['name']]
        
        # Get scene interpretation with face context from Overshoot
        context = data.get('context', '')
        scene_result = overshoot_client.interpret_with_faces(
            data['image'],
            detected_faces,
            identified_people,
            context
        )
        
        # Draw detections
        annotated_image = detector.draw_detections(image_array, detected_faces)
        annotated_base64 = detector.encode_image_to_base64(annotated_image)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Log to Phoenix
        image_features = person_info['features']
        phoenix_monitor.log_face_prediction(
            features=image_features,
            prediction=person_info['name'],
            confidence=person_info['confidence'],
            face_count=len(detected_faces),
            cached=False,
            latency_ms=latency_ms
        )
        
        return jsonify({
            'success': True,
            'person_name': person_info['name'],
            'notable_projects': person_info['notable_projects'],
            'confidence': person_info['confidence'],
            'face_count': len(detected_faces),
            'faces': detected_faces,
            'annotated_image': f'data:image/jpeg;base64,{annotated_base64}',
            'scene_interpretation': scene_result.get('scene_interpretation', ''),
            'interaction_analysis': scene_result.get('interaction_analysis', ''),
            'setting': scene_result.get('setting', ''),
            'story_context': scene_result.get('story_context', ''),
            'overshoot_confidence': scene_result.get('confidence', 0.0),
            'latency_ms': latency_ms
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_voice_features(audio, sample_rate):
    """
    Extract acoustic features from audio for voice analysis
    """
    features = {}
    
    # Fundamental frequency (pitch)
    pitches, magnitudes = librosa.piptrack(y=audio, sr=sample_rate)
    pitch_values = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        if pitch > 0:
            pitch_values.append(pitch)
    
    if pitch_values:
        features['mean_pitch'] = float(np.mean(pitch_values))
        features['pitch_std'] = float(np.std(pitch_values))
    else:
        features['mean_pitch'] = 0.0
        features['pitch_std'] = 0.0
    
    # Spectral features
    spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)[0]
    features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
    
    # Zero crossing rate
    zcr = librosa.feature.zero_crossing_rate(audio)[0]
    features['zcr_mean'] = float(np.mean(zcr))
    
    # MFCCs
    mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
    for i, mfcc in enumerate(mfccs):
        features[f'mfcc_{i}_mean'] = float(np.mean(mfcc))
    
    # Energy
    features['energy'] = float(np.sum(audio ** 2) / len(audio))
    
    # Tempo
    tempo, _ = librosa.beat.beat_track(y=audio, sr=sample_rate)
    features['tempo'] = float(tempo.item() if hasattr(tempo, 'item') else tempo)
    
    return features

def identify_voice_actor_with_llm(features, context=''):
    """
    Use LLM to identify voice actor based on audio features and context
    """
    from openai import OpenAI
    
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        # Return placeholder if no API key
        return {
            'actors': [{
                'name': '⚠️ No OpenAI API Key',
                'notable_projects': ['Add OPENAI_API_KEY to .env file'],
                'confidence': 0.0,
                'voice_characteristics': 'API key not configured'
            }],
            'total_speakers': 1
        }
    
    client = OpenAI(api_key=openai_api_key)
    
    prompt = f"""Based on the following voice characteristics and context, identify the voice actor(s) speaking in this audio clip.

Audio Features:
- Mean Pitch: {features.get('mean_pitch', 0):.2f} Hz
- Pitch Variation: {features.get('pitch_std', 0):.2f} Hz
- Spectral Centroid: {features.get('spectral_centroid_mean', 0):.2f} Hz
- Energy Level: {features.get('energy', 0):.4f}
- Tempo: {features.get('tempo', 0):.2f} BPM

Additional Context: {context if context else 'No additional context provided'}

Please identify the voice actor(s) and return a JSON response with this exact format:
{{
    "actors": [
        {{
            "name": "Actor Full Name",
            "notable_projects": [
                "Show/Movie - Character Name (Main Character/Recurring, Years)",
                "Show/Movie - Character Name (Main Character/Recurring, Years)"
            ],
            "confidence": 0.85,
            "voice_characteristics": "Description of their voice in this clip"
        }}
    ],
    "total_speakers": 1
}}

If you detect multiple distinct speakers, include all of them in the actors array.
Only include real, verified information. If uncertain, indicate lower confidence."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert voice actor identification specialist. Analyze audio features and context to identify voice actors with high accuracy. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        error_message = str(e)
        print(f"OpenAI API error: {error_message}", flush=True)
        
        # Check if it's a quota error
        if 'insufficient_quota' in error_message or '429' in error_message:
            return {
                'actors': [{
                    'name': '💳 OpenAI Quota Exceeded',
                    'notable_projects': [
                        'Your OpenAI API key has run out of credits',
                        'Add credits at: https://platform.openai.com/account/billing',
                        'Or use a different API key with available quota'
                    ],
                    'confidence': 0.0,
                    'voice_characteristics': 'API quota exceeded - add credits to continue'
                }],
                'total_speakers': 1,
                'error': 'insufficient_quota'
            }
        
        # Return fallback response for other errors
        return {
            'actors': [{
                'name': 'Unknown Actor',
                'notable_projects': ['Voice identification failed - please try again'],
                'confidence': 0.0,
                'voice_characteristics': f'Error: {error_message}'
            }],
            'total_speakers': 1,
            'error': error_message
        }

def identify_person_from_face_features(detected_face: dict, image_array: np.ndarray) -> dict:
    """
    Identify person from detected face features
    This is a placeholder - integrate with actual face recognition database
    
    Args:
        detected_face: face detection results with bbox and features
        image_array: original image array
        
    Returns:
        Person information with notable projects
    """
    # TODO: Integrate with face_recognition library or facial recognition API
    # For now, return enhanced mock response with real CV features
    
    face_features = detected_face['features']
    bbox = detected_face['bbox']
    
    # Combine detection features with additional image features
    image_features = {
        'dimensions': f"{image_array.shape[1]}x{image_array.shape[0]}",
        'face_confidence': detected_face['confidence'],
        'mean_brightness': face_features.get('mean_brightness', 0),
        'contrast': face_features.get('contrast', 0),
        'sharpness': face_features.get('sharpness', 0),
        'face_size': f"{bbox['width']}x{bbox['height']}",
        'aspect_ratio': float(image_array.shape[1] / image_array.shape[0])
    }
    
    return {
        'name': 'Bryan Cranston',
        'notable_projects': [
            'Breaking Bad - Walter White (Main Character, 2008-2013)',
            'Malcolm in the Middle - Hal (Main Character, 2000-2006)',
            'Your Honor - Michael Desiato (Main Character, 2020-2023)',
            'Seinfeld - Tim Whatley (Recurring, 1995-1997)'
        ],
        'confidence': float(detected_face['confidence']),
        'features': image_features,
        'note': 'Real face detection active! To enable actor identification, integrate with face recognition database.'
    }

def identify_person_from_face(image):
    """
    Identify person from facial image using computer vision
    This is a placeholder - you'll need to integrate with face recognition library
    """
    # TODO: Integrate with face_recognition library or similar
    # For now, return a mock response with notable projects
    
    image_array = np.array(image)
    
    # Extract basic image features for caching
    image_features = {
        'dimensions': f'{image_array.shape[1]}x{image_array.shape[0]}',
        'mean_brightness': float(np.mean(image_array)),
        'aspect_ratio': float(image_array.shape[1] / image_array.shape[0])
    }
    
    return {
        'name': 'Sample Actor',
        'notable_projects': [
            'Breaking Bad (2008-2013)',
            'Malcolm in the Middle (2000-2006)',
            'Your Honor (2020-2023)',
            'Seinfeld (1989-1998)'
        ],
        'confidence': 0.80,
        'features': image_features,
        'note': 'To enable actual face recognition, integrate with face_recognition library or similar service.',
        'matches': []
    }

@app.route('/api/identify-music', methods=['POST'])
def identify_music():
    """
    Identify music playing in audio using Shazam API
    """
    start_time = time.time()
    
    try:
        data = request.json
        
        if 'audio' not in data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Get audio data (base64 encoded)
        audio_base64 = data['audio']
        
        # Identify music with Shazam
        result = shazam_client.identify_music(audio_base64)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        if result.get('success') and result.get('track_found'):
            # Log to Phoenix
            phoenix_monitor.log_voice_prediction(
                features={'audio_duration': data.get('duration', 0)},
                prediction=f"{result.get('title')} - {result.get('artist')}",
                confidence=result.get('confidence', 0.95),
                cached=False,
                latency_ms=latency_ms
            )
            
            return jsonify({
                'success': True,
                'track_found': True,
                'title': result.get('title'),
                'artist': result.get('artist'),
                'album': result.get('album'),
                'genres': result.get('genres'),
                'release_date': result.get('release_date'),
                'cover_art': result.get('cover_art'),
                'apple_music_url': result.get('apple_music_url'),
                'shazam_url': result.get('shazam_url'),
                'preview_url': result.get('preview_url'),
                'confidence': result.get('confidence'),
                'latency_ms': latency_ms
            }), 200
        elif result.get('success') and not result.get('track_found'):
            return jsonify({
                'success': True,
                'track_found': False,
                'message': 'No music match found',
                'latency_ms': latency_ms
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'message': result.get('message', ''),
                'latency_ms': latency_ms
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search-music', methods=['POST'])
def search_music():
    """
    Search for music by name, artist, or lyrics
    """
    try:
        data = request.json
        
        if 'query' not in data:
            return jsonify({'error': 'No search query provided'}), 400
        
        query = data['query']
        limit = data.get('limit', 5)
        
        result = shazam_client.search_track(query, limit)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
