import cv2
import numpy as np
import mediapipe as mp
from typing import List, Dict, Any, Tuple
import base64

class FaceDetector:
    """Face detection and analysis using OpenCV Haar Cascade"""
    
    def __init__(self):
        # Use OpenCV's Haar Cascade for face detection (stable, no model file dependencies)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def detect_faces(self, image_array: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect faces in an image and return detailed information using OpenCV
        
        Args:
            image_array: numpy array of the image (BGR)
            
        Returns:
            List of detected faces with bounding boxes and features
        """
        height, width, _ = image_array.shape
        
        # Convert to grayscale for Haar Cascade
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        detected_faces_cv = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        
        faces = []
        for idx, (x, y, w, h) in enumerate(detected_faces_cv):
            # Ensure coordinates are within image bounds
            x = max(0, x)
            y = max(0, y)
            w = min(w, width - x)
            h = min(h, height - y)
            
            # Extract face region for analysis
            face_region = image_array[y:y+h, x:x+w] if h > 0 and w > 0 else image_array
            
            # Analyze face features
            features = self._analyze_face_features(face_region)
            
            faces.append({
                'id': idx,
                'bbox': {
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h)
                },
                'confidence': 0.9,  # Haar Cascade doesn't provide confidence
                'features': features
            })
        
        return faces
    
    def detect_landmarks(self, image_array: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect facial landmarks (simplified for compatibility)
        
        Args:
            image_array: numpy array of the image (BGR)
            
        Returns:
            List of faces with landmark coordinates (simplified)
        """
        # For now, just return face regions since MediaPipe API changed
        faces = self.detect_faces(image_array)
        faces_with_landmarks = []
        
        for face in faces:
            bbox = face['bbox']
            # Simple landmark approximation based on bounding box
            landmarks = {
                'left_eye': {'x': bbox['x'] + bbox['width'] * 0.3, 'y': bbox['y'] + bbox['height'] * 0.4},
                'right_eye': {'x': bbox['x'] + bbox['width'] * 0.7, 'y': bbox['y'] + bbox['height'] * 0.4},
                'nose': {'x': bbox['x'] + bbox['width'] * 0.5, 'y': bbox['y'] + bbox['height'] * 0.5},
                'mouth': {'x': bbox['x'] + bbox['width'] * 0.5, 'y': bbox['y'] + bbox['height'] * 0.7}
            }
            faces_with_landmarks.append({
                'id': face['id'],
                'bbox': bbox,
                'landmarks': landmarks
            })
        
        return faces_with_landmarks
    
    def draw_detections(self, image_array: np.ndarray, faces: List[Dict[str, Any]]) -> np.ndarray:
        """
        Draw bounding boxes and labels on image
        
        Args:
            image_array: numpy array of the image
            faces: list of detected faces
            
        Returns:
            Image with drawn detections
        """
        annotated_image = image_array.copy()
        
        for face in faces:
            bbox = face['bbox']
            confidence = face['confidence']
            
            # Draw bounding box
            cv2.rectangle(
                annotated_image,
                (bbox['x'], bbox['y']),
                (bbox['x'] + bbox['width'], bbox['y'] + bbox['height']),
                (0, 255, 0),
                2
            )
            
            # Draw label
            label = f"Face {face['id']} ({confidence:.2f})"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(
                annotated_image,
                (bbox['x'], bbox['y'] - label_size[1] - 10),
                (bbox['x'] + label_size[0], bbox['y']),
                (0, 255, 0),
                -1
            )
            cv2.putText(
                annotated_image,
                label,
                (bbox['x'], bbox['y'] - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                2
            )
        
        return annotated_image
    
    def _analyze_face_features(self, face_region: np.ndarray) -> Dict[str, Any]:
        """
        Analyze features of a detected face region
        
        Args:
            face_region: cropped face image
            
        Returns:
            Dictionary of facial features
        """
        if face_region.size == 0:
            return {}
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        
        # Calculate various features
        features = {
            'mean_brightness': float(np.mean(gray)),
            'brightness_std': float(np.std(gray)),
            'contrast': float(np.std(gray) / (np.mean(gray) + 1e-7)),
            'sharpness': float(cv2.Laplacian(gray, cv2.CV_64F).var()),
            'size': {
                'width': face_region.shape[1],
                'height': face_region.shape[0]
            }
        }
        
        # Color analysis
        if len(face_region.shape) == 3:
            features['color_mean'] = {
                'r': float(np.mean(face_region[:, :, 2])),
                'g': float(np.mean(face_region[:, :, 1])),
                'b': float(np.mean(face_region[:, :, 0]))
            }
        
        return features
    
    def _calculate_face_orientation(self, landmarks: List[Dict], width: int, height: int) -> Dict[str, str]:
        """
        Calculate approximate face orientation (frontal, profile, etc.)
        
        Args:
            landmarks: facial landmarks
            width, height: image dimensions
            
        Returns:
            Orientation information
        """
        # Simplified orientation detection based on landmark positions
        if len(landmarks) < 468:
            return {'pose': 'unknown'}
        
        # Use key points to determine orientation
        nose_tip = landmarks[1]
        left_eye = landmarks[33]
        right_eye = landmarks[263]
        
        # Calculate eye distance to determine if face is frontal
        eye_distance = abs(left_eye['x'] - right_eye['x'])
        
        if eye_distance > 0.15:
            return {'pose': 'frontal', 'quality': 'good'}
        elif eye_distance > 0.08:
            return {'pose': 'slight_angle', 'quality': 'fair'}
        else:
            return {'pose': 'profile', 'quality': 'poor'}
    
    def _extract_key_points(self, landmarks: List[Dict], width: int, height: int) -> Dict[str, Tuple[int, int]]:
        """
        Extract key facial points (eyes, nose, mouth)
        
        Args:
            landmarks: facial landmarks
            width, height: image dimensions
            
        Returns:
            Dictionary of key point coordinates
        """
        if len(landmarks) < 468:
            return {}
        
        key_points = {
            'left_eye': (int(landmarks[33]['x'] * width), int(landmarks[33]['y'] * height)),
            'right_eye': (int(landmarks[263]['x'] * width), int(landmarks[263]['y'] * height)),
            'nose_tip': (int(landmarks[1]['x'] * width), int(landmarks[1]['y'] * height)),
            'mouth_center': (int(landmarks[13]['x'] * width), int(landmarks[13]['y'] * height))
        }
        
        return key_points
    
    def encode_image_to_base64(self, image_array: np.ndarray) -> str:
        """
        Encode image to base64 string
        
        Args:
            image_array: numpy array of the image
            
        Returns:
            Base64 encoded string
        """
        _, buffer = cv2.imencode('.jpg', image_array)
        return base64.b64encode(buffer).decode('utf-8')

# Global detector instance
_detector = None

def get_detector() -> FaceDetector:
    """Get or create global face detector instance"""
    global _detector
    if _detector is None:
        _detector = FaceDetector()
    return _detector
