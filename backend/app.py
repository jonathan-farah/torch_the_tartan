from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
import io
from datetime import datetime
import numpy as np
from PIL import Image
import librosa
import soundfile as sf

app = Flask(__name__)
CORS(app)

# Create uploads directory
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'Server is running'}), 200

@app.route('/api/analyze-voice', methods=['POST'])
def analyze_voice():
    """
    Analyze audio and identify voice actor using LLM
    """
    try:
        data = request.json
        
        if 'audio' not in data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Decode base64 audio
        audio_data = base64.b64decode(data['audio'].split(',')[1] if ',' in data['audio'] else data['audio'])
        
        # Save temporary file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        audio_path = os.path.join(UPLOAD_FOLDER, f'voice_{timestamp}.wav')
        
        with open(audio_path, 'wb') as f:
            f.write(audio_data)
        
        # Load and analyze audio
        y, sr = librosa.load(audio_path, sr=None)
        
        # Extract audio features
        features = extract_voice_features(y, sr)
        
        # Use LLM to identify voice actor (placeholder for now)
        voice_actor = identify_voice_actor_with_llm(features, data.get('context', ''))
        
        # Clean up
        os.remove(audio_path)
        
        return jsonify({
            'success': True,
            'voice_actor': voice_actor,
            'features': features
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-face', methods=['POST'])
def analyze_face():
    """
    Analyze image and identify person using facial recognition
    """
    try:
        data = request.json
        
        if 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = base64.b64decode(data['image'].split(',')[1] if ',' in data['image'] else data['image'])
        image = Image.open(io.BytesIO(image_data))
        
        # Save temporary file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_path = os.path.join(UPLOAD_FOLDER, f'face_{timestamp}.jpg')
        image.save(image_path)
        
        # Analyze face
        person_info = identify_person_from_face(image)
        
        # Clean up
        os.remove(image_path)
        
        return jsonify({
            'success': True,
            'person': person_info
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
    features['tempo'] = float(tempo)
    
    return features

def identify_voice_actor_with_llm(features, context=''):
    """
    Use LLM to identify voice actor based on audio features and context
    This is a placeholder - you'll need to integrate with OpenAI, Anthropic, or similar
    """
    # TODO: Integrate with actual LLM API (OpenAI GPT-4, Anthropic Claude, etc.)
    # For now, return a mock response
    
    prompt = f"""Based on the following voice characteristics, identify the likely voice actor:
    
Audio Features:
- Mean Pitch: {features.get('mean_pitch', 0):.2f} Hz
- Pitch Variation: {features.get('pitch_std', 0):.2f} Hz
- Spectral Centroid: {features.get('spectral_centroid_mean', 0):.2f} Hz
- Energy Level: {features.get('energy', 0):.4f}
- Tempo: {features.get('tempo', 0):.2f} BPM

Additional Context: {context}

Please identify the voice actor and provide confidence level."""
    
    # Placeholder response
    return {
        'name': 'Voice Actor Name (Placeholder)',
        'confidence': 0.75,
        'reasoning': 'This is a placeholder. Integrate with an LLM API to get actual results.',
        'prompt_used': prompt,
        'note': 'To enable actual voice actor identification, add your LLM API key and integrate with OpenAI, Anthropic, or similar service.'
    }

def identify_person_from_face(image):
    """
    Identify person from facial image using computer vision
    This is a placeholder - you'll need to integrate with face recognition library
    """
    # TODO: Integrate with face_recognition library or similar
    # For now, return a mock response
    
    image_array = np.array(image)
    
    return {
        'name': 'Person Name (Placeholder)',
        'confidence': 0.80,
        'features_detected': {
            'face_found': True,
            'image_dimensions': f'{image_array.shape[1]}x{image_array.shape[0]}',
            'note': 'To enable actual face recognition, integrate with face_recognition library or similar service.'
        },
        'matches': []
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000)
