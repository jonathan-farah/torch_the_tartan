import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from datetime import datetime
from typing import Dict, Any, Optional
import json

class PhoenixMonitor:
    """Arize Phoenix integration for ML model monitoring and observability"""
    
    def __init__(self):
        self.enabled = os.getenv('ENABLE_PHOENIX', 'true').lower() == 'true'
        
        if not self.enabled:
            print("Phoenix monitoring disabled")
            self.tracer = None
            return
        
        # Get Phoenix configuration
        self.collector_endpoint = os.getenv('PHOENIX_COLLECTOR_ENDPOINT', 'http://localhost:6006')
        self.project_name = os.getenv('PHOENIX_PROJECT_NAME', 'torch-tartan')
        
        try:
            # Set up OpenTelemetry with Phoenix
            resource = Resource.create({"service.name": self.project_name})
            
            tracer_provider = TracerProvider(resource=resource)
            
            # Configure OTLP exporter to send to Phoenix
            span_exporter = OTLPSpanExporter(
                endpoint=f"{self.collector_endpoint}/v1/traces"
            )
            
            span_processor = BatchSpanProcessor(span_exporter)
            tracer_provider.add_span_processor(span_processor)
            
            trace.set_tracer_provider(tracer_provider)
            
            self.tracer = trace.get_tracer(__name__)
            
            print(f"✓ Phoenix monitoring initialized")
            print(f"  Collector: {self.collector_endpoint}")
            print(f"  Project: {self.project_name}")
            print(f"  UI: {self.collector_endpoint}")
            print(f"  Note: Phoenix server must be running on port 6006")
            
        except Exception as e:
            print(f"Warning: Phoenix monitoring initialization failed: {e}")
            print(f"  Continuing without Phoenix monitoring...")
            self.enabled = False
            self.tracer = None
            print("Application will continue without monitoring")
            self.tracer = None
            self.enabled = False
    
    def log_voice_prediction(
        self, 
        features: Dict[str, Any],
        prediction: str,
        confidence: float,
        context: str = '',
        cached: bool = False,
        latency_ms: Optional[float] = None
    ) -> bool:
        """
        Log voice recognition prediction to Phoenix
        
        Args:
            features: Audio features extracted
            prediction: Predicted voice actor name
            confidence: Prediction confidence score
            context: TV show context if provided
            cached: Whether result came from cache
            latency_ms: Prediction latency in milliseconds
            
        Returns:
            True if logging successful, False otherwise
        """
        if not self.enabled or not self.tracer:
            return False
        
        try:
            with self.tracer.start_as_current_span("voice_recognition") as span:
                # Set span attributes
                span.set_attribute("model.name", "torch-tartan-voice-recognition")
                span.set_attribute("model.type", "classification")
                span.set_attribute("prediction.label", prediction)
                span.set_attribute("prediction.score", confidence)
                span.set_attribute("prediction.cached", cached)
                
                if context:
                    span.set_attribute("input.context", context)
                
                if latency_ms:
                    span.set_attribute("latency.ms", latency_ms)
                
                # Log audio features
                span.set_attribute("features.mean_pitch", features.get('mean_pitch', 0))
                span.set_attribute("features.pitch_std", features.get('pitch_std', 0))
                span.set_attribute("features.spectral_centroid", features.get('spectral_centroid_mean', 0))
                span.set_attribute("features.zcr", features.get('zcr_mean', 0))
                span.set_attribute("features.energy", features.get('energy', 0))
                span.set_attribute("features.tempo", features.get('tempo', 0))
                
                # Add as events for better visibility
                span.add_event("prediction_complete", {
                    "actor": prediction,
                    "confidence": confidence,
                    "cached": cached
                })
            
            return True
                
        except Exception as e:
            print(f"Error logging to Phoenix: {str(e)}")
            return False
    
    def log_face_prediction(
        self,
        features: Dict[str, Any],
        prediction: str,
        confidence: float,
        face_count: int = 1,
        cached: bool = False,
        latency_ms: Optional[float] = None
    ) -> bool:
        """
        Log face recognition prediction to Phoenix
        
        Args:
            features: Image and face features extracted
            prediction: Predicted person name
            confidence: Prediction confidence score
            face_count: Number of faces detected
            cached: Whether result came from cache
            latency_ms: Prediction latency in milliseconds
            
        Returns:
            True if logging successful, False otherwise
        """
        if not self.enabled or not self.tracer:
            return False
        
        try:
            with self.tracer.start_as_current_span("face_recognition") as span:
                # Set span attributes
                span.set_attribute("model.name", "torch-tartan-face-recognition")
                span.set_attribute("model.type", "classification")
                span.set_attribute("prediction.label", prediction)
                span.set_attribute("prediction.score", confidence)
                span.set_attribute("prediction.cached", cached)
                span.set_attribute("detection.face_count", face_count)
                
                if latency_ms:
                    span.set_attribute("latency.ms", latency_ms)
                
                # Log image features
                span.set_attribute("features.dimensions", str(features.get('dimensions', 'unknown')))
                span.set_attribute("features.face_confidence", features.get('face_confidence', 0))
                span.set_attribute("features.brightness", features.get('mean_brightness', 0))
                span.set_attribute("features.contrast", features.get('contrast', 0))
                span.set_attribute("features.sharpness", features.get('sharpness', 0))
                span.set_attribute("features.aspect_ratio", features.get('aspect_ratio', 1.0))
                
                # Add as events for better visibility
                span.add_event("prediction_complete", {
                    "person": prediction,
                    "confidence": confidence,
                    "cached": cached,
                    "face_count": face_count
                })
            
            return True
                
        except Exception as e:
            print(f"Error logging to Phoenix: {str(e)}")
            return False
    
    def log_error(self, model_type: str, error_message: str, features: Optional[Dict] = None):
        """
        Log errors and failures to Phoenix for debugging
        
        Args:
            model_type: 'voice' or 'face'
            error_message: Error description
            features: Optional features that caused the error
        """
        if not self.enabled or not self.tracer:
            return
        
        try:
            span_name = f"{model_type}_recognition_error"
            
            with self.tracer.start_as_current_span(span_name) as span:
                span.set_attribute("error", True)
                span.set_attribute("error.type", "prediction_failure")
                span.set_attribute("error.message", error_message)
                span.set_attribute("model.type", model_type)
                
                if features:
                    span.set_attribute("features", json.dumps(features))
                
                span.add_event("error_occurred", {
                    "message": error_message,
                    "model": model_type
                })
            
        except Exception as e:
            print(f"Error logging error to Phoenix: {str(e)}")

# Global monitor instance
_monitor = None

def get_monitor() -> PhoenixMonitor:
    """Get or create global Phoenix monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = PhoenixMonitor()
    return _monitor
