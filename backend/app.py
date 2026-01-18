from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
import io
import json
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
        
        # Get context
        context = data.get('context', '')
        
        # Use LLM to identify voice actor (with transcription)
        voice_actor_info = identify_voice_actor_with_llm(features, context, audio_path)
        
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
            'features': features
        }), 200
    
    except Exception as e:
        # Clean up on error
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
        print("=== FACE ANALYSIS START ===", flush=True)
        data = request.json
        print(f"Received data keys: {data.keys() if data else 'None'}", flush=True)
        
        if 'image' not in data:
            print("ERROR: No image data provided", flush=True)
            return jsonify({'error': 'No image data provided'}), 400
        
        print("Decoding base64 image...", flush=True)
        # Decode base64 image
        image_data = base64.b64decode(data['image'].split(',')[1] if ',' in data['image'] else data['image'])
        print(f"Image data size: {len(image_data)} bytes", flush=True)
        
        image = Image.open(io.BytesIO(image_data))
        print(f"Image opened: {image.size} {image.mode}", flush=True)
        
        # Convert to numpy array for OpenCV
        image_array = np.array(image)
        print(f"Image array shape: {image_array.shape}", flush=True)
        
        if len(image_array.shape) == 2:  # Grayscale
            image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2BGR)
        elif image_array.shape[2] == 4:  # RGBA
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2BGR)
        elif image_array.shape[2] == 3:  # RGB
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        print("Image converted to BGR", flush=True)
        
        # Save temporary file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_path = os.path.join(UPLOAD_FOLDER, f'face_{timestamp}.jpg')
        print(f"Saving image to: {image_path}", flush=True)
        cv2.imwrite(image_path, image_array)
        print("Image saved", flush=True)
        
        # Detect faces using computer vision
        print("Getting face detector...", flush=True)
        try:
            detector = get_detector()
            print("Face detector obtained successfully", flush=True)
        except Exception as detector_error:
            print(f"ERROR getting detector: {type(detector_error).__name__}: {str(detector_error)}", flush=True)
            import traceback
            traceback.print_exc()
            raise
        
        print("Detecting faces...", flush=True)
        detected_faces = detector.detect_faces(image_array)
        print(f"Detected {len(detected_faces)} faces", flush=True)
        
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
        for idx, person in enumerate(identified_people):
            # Use the features from the identification
            person_info = identify_person_from_face_features(detected_faces[idx], image_array)
            if 'features' in person_info:
                database.cache_face_result(
                    person_info['features'],
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
            'annotated_image': f'data:image/jpeg;base64,{annotated_base64}'
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

def identify_voice_actor_with_llm(features, context='', audio_path=None):
    """
    Use LLM to identify voice actor based on audio features, transcription, and context
    """
    from openai import OpenAI
    import re
    
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
    
    # Normalize context - make case-insensitive and remove punctuation
    normalized_context = re.sub(r'[^\w\s]', '', context.lower().strip()) if context else ''
    
    # Try to get speech transcription for better identification
    transcription = ""
    if audio_path and os.path.exists(audio_path):
        try:
            with open(audio_path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
                transcription = transcript if isinstance(transcript, str) else transcript.text
                print(f"Transcription: {transcription}", flush=True)
        except Exception as e:
            print(f"Transcription failed: {e}", flush=True)
            transcription = ""
    
    # Determine voice characteristics from features
    pitch = features.get('mean_pitch', 0)
    if pitch > 200:
        pitch_desc = "very high-pitched (female or young voice)"
    elif pitch > 165:
        pitch_desc = "high-pitched (likely female)"
    elif pitch > 130:
        pitch_desc = "medium-high pitch (male or female)"
    elif pitch > 100:
        pitch_desc = "medium-low pitch (male)"
    else:
        pitch_desc = "very low-pitched (deep male voice)"
    
    energy_desc = "high energy/loud" if features.get('energy', 0) > 0.01 else "moderate energy"
    
    prompt = f"""You are analyzing an audio clip to identify the voice actors speaking. 

TRANSCRIPTION:
"{transcription if transcription else '[No clear speech detected]'}"

AUDIO FEATURES:
- Average Pitch: {pitch:.1f} Hz ({pitch_desc})
- Energy: {energy_desc}

SHOW/MOVIE CONTEXT: {context if context else 'Unknown'}

CRITICAL INSTRUCTIONS:
1. Analyze the transcription to determine HOW MANY distinct speakers are present
   - Look for dialogue patterns (questions and answers indicate different speakers)
   - A conversation with back-and-forth indicates 2 people
   - Single perspective/monologue is usually 1 person
   
2. Count conservatively - only report speakers you can CLEARLY distinguish
   - If unclear, prefer fewer speakers with higher confidence
   - Don't add extra speakers just because dialogue mentions other names
   
3. Match EACH speaker to their character (if context provided) and identify the voice actor

4. Quality over quantity: Better to correctly identify 2 speakers than incorrectly list 3

For voice recognition:
- Terry Crews: Powerful, booming deep voice (~100-120 Hz)
- Clancy Brown: Authoritative, menacing deep voice (~85-110 Hz)
- Fred Tatasciore: Versatile deep character voice (~90-115 Hz)
- Steven Yeun: Medium pitch, conversational Korean-American voice (~120-140 Hz)
- J.K. Simmons: Distinctive sharp, assertive voice (~110-130 Hz)

Return JSON with ALL speakers (but only ones you're confident about):
{{
    "actors": [
        {{
            "name": "Actor Full Name",
            "notable_projects": ["Show - Character (Role, Years)"],
            "confidence": 0.75,
            "voice_characteristics": "Brief description",
            "likely_lines": "Approximate lines this actor spoke"
        }}
    ],
    "total_speakers": 2,
    "reasoning": "How you determined the speaker count and identities"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """You are an expert at identifying voice actors from audio transcriptions and context.

KEY PRINCIPLES:
- Accuracy over quantity: Correctly identify the actual speakers present
- Count conservatively: Only report speakers you can clearly distinguish
- Use show context to match characters to voice actors
- Consider dialogue patterns: back-and-forth usually means 2 speakers, not 3+
- Don't invent extra speakers - if you hear 2, report 2

VOICE ACTOR DATABASE (with typical pitch ranges):
- Steven Yeun (Invincible): Medium, conversational (~120-140 Hz)
- J.K. Simmons (Omni-Man): Sharp, assertive, commanding (~110-130 Hz)
- Sandra Oh (Debbie): Female, expressive (~180-220 Hz)
- Zazie Beetz (Amber): Female, warm (~170-210 Hz)
- Clancy Brown: Deep, authoritative (~85-110 Hz) - often villains
- Terry Crews: Powerful, booming deep voice (~100-120 Hz)
- Fred Tatasciore: Versatile deep character voice (~90-115 Hz)
- Walton Goggins: Distinctive Southern drawl (~115-135 Hz)

Always return valid JSON. Be precise with speaker count."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
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
    Identify person from detected face features using OpenAI Vision API with caching
    
    Args:
        detected_face: face detection results with bbox and features
        image_array: original image array
        
    Returns:
        Person information with notable projects
    """
    face_features = detected_face['features']
    bbox = detected_face['bbox']
    
    # Combine detection features with additional image features for caching
    image_features = {
        'dimensions': f"{image_array.shape[1]}x{image_array.shape[0]}",
        'face_confidence': detected_face['confidence'],
        'mean_brightness': face_features.get('mean_brightness', 0),
        'contrast': face_features.get('contrast', 0),
        'sharpness': face_features.get('sharpness', 0),
        'face_size': f"{bbox['width']}x{bbox['height']}",
        'aspect_ratio': float(image_array.shape[1] / image_array.shape[0])
    }
    
    # Use OpenAI Vision API to identify person
    try:
        # Extract face region from image
        x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
        face_crop = image_array[y:y+h, x:x+w]
        
        # Convert to PIL Image and encode to base64
        from PIL import Image
        face_pil = Image.fromarray(cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB))
        
        import io
        buffered = io.BytesIO()
        face_pil.save(buffered, format="JPEG")
        import base64
        face_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Call OpenAI Vision API
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Identify this person. Provide their name and list their most notable TV shows and movies with character names and years. Format as: Name, then bullet points of 'Title - Character (Type, Years)'. Be specific and accurate."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{face_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        identification = response.choices[0].message.content
        
        # Parse response to extract name and projects
        lines = identification.strip().split('\n')
        name = lines[0].strip()
        projects = [line.strip('- •*').strip() for line in lines[1:] if line.strip() and line.strip().startswith(('-', '•', '*'))]
        
        # Clean up name (remove extra text like "This is...")
        if ':' in name:
            name = name.split(':')[-1].strip()
        if '.' in name and len(name.split('.')[0]) < 30:
            name = name.split('.')[0].strip()
        
        confidence = 0.85  # OpenAI Vision confidence estimate
        
        return {
            'name': name,
            'notable_projects': projects if projects else ['Information not available'],
            'confidence': confidence,
            'features': image_features
        }
        
    except Exception as e:
        print(f"Error identifying person with OpenAI Vision: {str(e)}", flush=True)
        return {
            'name': 'Unknown Person',
            'notable_projects': ['Unable to identify - API error'],
            'confidence': 0.0,
            'features': image_features,
            'error': str(e)
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
        print("=== MUSIC IDENTIFICATION START ===")
        data = request.json
        print(f"Received data keys: {data.keys()}")
        
        if 'audio' not in data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Get audio data (base64 encoded)
        audio_base64 = data['audio']
        print(f"Audio data size: {len(audio_base64)} chars")
        
        # Identify music with Shazam
        print("Calling Shazam API...")
        result = shazam_client.identify_music(audio_base64)
        print(f"Shazam result: {result}")
        
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
            # Check if it's a subscription error
            error_msg = result.get('error', 'Unknown error')
            message = result.get('message', '')
            
            if 'not subscribed' in message or '403' in error_msg:
                return jsonify({
                    'success': False,
                    'error': 'Music identification service unavailable',
                    'message': 'The Shazam API requires an active subscription. Please subscribe at https://rapidapi.com/apidojo/api/shazam',
                    'latency_ms': latency_ms
                }), 503
            
            return jsonify({
                'success': False,
                'error': error_msg,
                'message': message,
                'latency_ms': latency_ms
            }), 500
            
    except Exception as e:
        print(f"Exception in identify_music: {str(e)}")
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
