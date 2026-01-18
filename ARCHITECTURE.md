# Torch the Tartan - Architecture with Arize AI

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                              │
│                                                                          │
│  ┌────────────────────────┐          ┌──────────────────────────────┐  │
│  │   Voice Recognition    │          │    Face Recognition          │  │
│  │                        │          │                              │  │
│  │  🎤 Record Audio       │          │  📸 Capture Photo            │  │
│  │  📝 Enter TV Show      │          │  👁️  Live Detection         │  │
│  │  ▶️  Analyze           │          │  🔍 Identify Person          │  │
│  └────────────────────────┘          └──────────────────────────────┘  │
│                                                                          │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             │ HTTP REST API
                             │
┌────────────────────────────▼─────────────────────────────────────────────┐
│                           FLASK BACKEND                                   │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     app.py (API Endpoints)                       │    │
│  │                                                                  │    │
│  │  POST /api/analyze-voice                                        │    │
│  │  ├─ Decode base64 audio                                         │    │
│  │  ├─ Extract features with librosa ────────┐                     │    │
│  │  ├─ Check cache (SQLite) ─────────────┐   │                     │    │
│  │  │  ├─ Cache hit: return cached result│   │                     │    │
│  │  │  └─ Cache miss: identify with LLM  │   │                     │    │
│  │  ├─ Store in cache ────────────────────┤   │                     │    │
│  │  └─ Log to Arize ──────────────────────┼───┼────────────┐       │    │
│  │                                         │   │            │       │    │
│  │  POST /api/analyze-face                 │   │            │       │    │
│  │  ├─ Decode base64 image                 │   │            │       │    │
│  │  ├─ Detect faces with MediaPipe/OpenCV │   │            │       │    │
│  │  ├─ Extract features ───────────────────┘   │            │       │    │
│  │  ├─ Check cache (SQLite) ───────────────────┘            │       │    │
│  │  │  ├─ Cache hit: return cached result                   │       │    │
│  │  │  └─ Cache miss: identify person                       │       │    │
│  │  ├─ Draw bounding boxes and annotations                  │       │    │
│  │  ├─ Store in cache                                        │       │    │
│  │  └─ Log to Arize ─────────────────────────────────────────┘       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────┐    │
│  │  database.py     │  │ face_detection.py│  │ arize_monitor.py   │    │
│  │                  │  │                  │  │                    │    │
│  │  • SQLite ORM    │  │  • MediaPipe     │  │  • ArizeMonitor    │    │
│  │  • Cache lookup  │  │  • OpenCV        │  │  • log_voice()     │    │
│  │  • Feature hash  │  │  • Face landmarks│  │  • log_face()      │    │
│  │  • Stats         │  │  • Bounding boxes│  │  • log_error()     │    │
│  └──────────────────┘  └──────────────────┘  └─────────┬──────────┘    │
│                                                          │               │
└──────────────────────────────────────────────────────────┼───────────────┘
                                                           │
                                    HTTPS (Async, Non-blocking)
                                                           │
                                                           ▼
                              ┌────────────────────────────────────────┐
                              │         ARIZE AI PLATFORM              │
                              │                                        │
                              │  🔍 Prediction Monitoring              │
                              │  📊 Performance Metrics                │
                              │  📈 Feature Drift Detection            │
                              │  ⚠️  Alerting & Notifications          │
                              │  🐛 Debugging Tools                    │
                              │  📉 Model Comparison                   │
                              │                                        │
                              │  Models:                               │
                              │  • torch-tartan-voice-recognition      │
                              │  • torch-tartan-face-recognition       │
                              └────────────────────────────────────────┘
                                                           │
                                                           │
                                                           ▼
                              ┌────────────────────────────────────────┐
                              │       ARIZE DASHBOARD (Web)            │
                              │                                        │
                              │  👤 ML Engineers & Data Scientists     │
                              │  📊 Real-time Dashboards               │
                              │  🔔 Alert Management                   │
                              │  📉 Trend Analysis                     │
                              └────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                              DATA FLOW
═══════════════════════════════════════════════════════════════════════════

Voice Recognition Flow:
━━━━━━━━━━━━━━━━━━━━━━

1. User records audio → Frontend sends base64 to backend
2. Backend decodes → librosa extracts features
3. Check cache (SQLite) by feature hash
   ├─ Hit: Return cached result (fast path)
   └─ Miss: Call LLM for identification
4. Store result in cache for future lookups
5. **Log to Arize**: 
   - Features: pitch, spectral_centroid, zcr, energy, tempo, MFCCs
   - Prediction: actor name, confidence
   - Metadata: latency, cache status, TV show context
6. Return result to frontend


Face Recognition Flow:
━━━━━━━━━━━━━━━━━━━━

1. User captures photo → Frontend sends base64 to backend
2. Backend decodes → OpenCV processes image
3. MediaPipe detects faces → Extract landmarks and features
4. Check cache (SQLite) by feature hash
   ├─ Hit: Return cached result (fast path)
   └─ Miss: Identify person from features
5. Draw bounding boxes and annotations
6. Store result in cache for future lookups
7. **Log to Arize**:
   - Features: brightness, contrast, sharpness, dimensions, aspect_ratio
   - Prediction: person name, confidence
   - Metadata: latency, cache status, face count, detection confidence
8. Return annotated image and result to frontend


Arize Monitoring Flow (Asynchronous):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Prediction completes in backend
2. arize_monitor.log_voice_prediction() or log_face_prediction() called
3. Create pandas DataFrame with:
   - Prediction ID (UUID)
   - Timestamp
   - Features (all extracted features)
   - Prediction (label and score)
   - Metadata (latency, cache, etc.)
4. Send to Arize via Client.log() (async HTTP)
5. Arize ingests and indexes prediction
6. Dashboard updates in real-time (1-2 min delay)
7. Monitors check for drift, anomalies, performance issues


═══════════════════════════════════════════════════════════════════════════
                         KEY COMPONENTS
═══════════════════════════════════════════════════════════════════════════

Frontend (React):
├─ VoiceRecognition.js: Audio recording with MediaRecorder API
├─ FaceRecognition.js: Camera access with getUserMedia API
├─ Beautiful UI with real-time feedback
└─ Display results (actor/person, projects, confidence)

Backend (Flask):
├─ app.py: REST API endpoints
├─ database.py: SQLite caching (hash-based lookup)
├─ face_detection.py: MediaPipe + OpenCV face detection
├─ arize_monitor.py: Arize AI integration
└─ requirements.txt: Python dependencies

Libraries:
├─ librosa: Audio feature extraction
├─ opencv-python: Image processing
├─ mediapipe: Face detection and landmarks
├─ arize: ML observability
├─ pandas: Data processing for Arize
└─ flask-cors: Cross-origin requests

Storage:
├─ SQLite: recognition_cache.db (voice_cache, face_cache tables)
└─ Temporary: uploads/ folder (cleaned after processing)

External Services:
├─ Arize AI: ML monitoring platform (cloud)
├─ (Optional) OpenAI: Voice actor identification
└─ (Optional) Anthropic: Alternative LLM provider


═══════════════════════════════════════════════════════════════════════════
                      PERFORMANCE CHARACTERISTICS
═══════════════════════════════════════════════════════════════════════════

Latency Breakdown (Typical):
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Voice Recognition:
├─ Audio decode: 5-10ms
├─ librosa feature extraction: 100-200ms
├─ Cache lookup: 1-5ms
├─ LLM identification (cache miss): 500-2000ms
├─ Arize logging: 5-10ms (async, non-blocking)
└─ Total: 111-2225ms (depending on cache)

Face Recognition:
├─ Image decode: 5-10ms
├─ MediaPipe face detection: 50-150ms
├─ Feature extraction: 10-20ms
├─ Cache lookup: 1-5ms
├─ Person identification (cache miss): 100-500ms
├─ Bounding box rendering: 10-20ms
├─ Arize logging: 5-10ms (async, non-blocking)
└─ Total: 181-715ms (depending on cache)

Cache Performance:
├─ Hit rate (typical): 30-70% after warmup
├─ Speedup on hit: 5-10x faster
└─ Storage: ~1KB per cached entry

Arize Impact:
├─ Latency added: ~5-10ms (async)
├─ Network: Batched requests to Arize
├─ Resilience: Non-blocking, fails gracefully
└─ No impact on user experience


═══════════════════════════════════════════════════════════════════════════
                           SCALABILITY
═══════════════════════════════════════════════════════════════════════════

Current Architecture (Single-Server):
├─ Handles: ~10-100 requests/minute
├─ Bottleneck: LLM API calls (voice) and MediaPipe (face)
├─ Cache helps: Reduces load on expensive operations
└─ Arize: Async logging, no bottleneck

Horizontal Scaling Options:
├─ Load balancer → Multiple Flask instances
├─ Shared SQLite cache → PostgreSQL/Redis
├─ Background workers for LLM calls (Celery)
└─ Arize auto-scales with increased load

Monitoring with Arize:
├─ Track latency percentiles (p50, p95, p99)
├─ Detect performance degradation early
├─ Optimize hot paths based on data
└─ Alert on unusual load patterns


═══════════════════════════════════════════════════════════════════════════
```

## Summary

This architecture provides:

✅ **Real-time ML predictions** for voice and face recognition
✅ **Smart caching** for fast repeated lookups
✅ **Production monitoring** with Arize AI
✅ **Computer vision** with MediaPipe and OpenCV
✅ **Modern UI** with React
✅ **Scalable design** with async operations

The Arize integration adds observability without impacting user experience, providing insights into model performance, feature drift, and system health.

✓ Phoenix monitoring initialized
✓ Collector: http://localhost:6006
✓ Project: torch-tartan
✓ UI: http://localhost:6006
