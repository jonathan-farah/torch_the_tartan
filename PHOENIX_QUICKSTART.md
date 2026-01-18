# Arize Phoenix Integration - Quick Start

## ✅ Integration Complete

Your Torch the Tartan application now uses **Arize Phoenix** - an open-source ML observability platform that runs locally!

## What is Phoenix?

Phoenix is a lightweight, open-source alternative to cloud-based ML monitoring. It:
- Runs locally on your machine (no API keys needed!)
- Provides a beautiful web UI for viewing traces
- Uses OpenTelemetry standard for instrumentation
- Perfect for development and debugging

## Quick Start

### 1. Install Phoenix (Separate Terminal)

```powershell
# Option A: Install via pip
pip install arize-phoenix

# Option B: Run via Docker
docker run -p 6006:6006 arizephoenix/phoenix:latest
```

### 2. Start Phoenix Server

```powershell
# Start Phoenix
python -m phoenix.server.main serve

# Or with Docker
docker run -p 6006:6006 arizephoenix/phoenix:latest
```

Phoenix UI will be available at: **http://localhost:6006**

### 3. Start Your Application

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python app.py
```

### 4. Use the App

Make some predictions (voice or face recognition). Traces will automatically flow to Phoenix!

### 5. View in Phoenix

Open **http://localhost:6006** to see:
- Real-time prediction traces
- Latency measurements
- Feature values
- Error tracking
- Performance metrics

## Configuration

Phoenix settings in `.env`:

```bash
# Phoenix Configuration
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006
PHOENIX_PROJECT_NAME=torch-tartan
ENABLE_PHOENIX=true
```

### Options:

- **PHOENIX_COLLECTOR_ENDPOINT**: Where Phoenix is running (default: http://localhost:6006)
- **PHOENIX_PROJECT_NAME**: Project identifier in Phoenix UI (default: torch-tartan)
- **ENABLE_PHOENIX**: Enable/disable monitoring (default: true)

## What Gets Traced

### Voice Recognition
- Model: `torch-tartan-voice-recognition`
- Features: pitch, spectral_centroid, zcr, energy, tempo
- Prediction: actor name, confidence
- Metadata: latency, cache status, TV show context

### Face Recognition
- Model: `torch-tartan-face-recognition`
- Features: brightness, contrast, sharpness, dimensions
- Prediction: person name, confidence
- Metadata: latency, cache status, face count, detection confidence

## Phoenix UI Features

### Traces View
- See each prediction as a trace
- Click to view details (features, prediction, timing)
- Filter by model, time range, or attributes

### Performance Analysis
- Latency distributions (p50, p95, p99)
- Throughput over time
- Cache hit rates

### Debugging
- View errors and stack traces
- Low-confidence predictions
- Unusual feature values

## Disable Phoenix

To turn off monitoring:

```bash
# Option 1: Set in .env
ENABLE_PHOENIX=false

# Option 2: Stop Phoenix server (app continues working)
```

The app works perfectly fine without Phoenix running - traces just won't be collected.

## Troubleshooting

### "Phoenix monitoring initialization failed"
- Phoenix server isn't running
- Start Phoenix: `python -m phoenix.server.main serve`
- Or disable: `ENABLE_PHOENIX=false`

### Can't access http://localhost:6006
- Check Phoenix is running: `ps aux | grep phoenix`
- Try different port in `.env`: `PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6007`
- Check firewall settings

### No traces appearing
- Make predictions in the app (voice/face recognition)
- Check console logs for "Phoenix monitoring initialized"
- Verify Phoenix server is running on correct port
- Refresh Phoenix UI

## Phoenix vs Arize Cloud

| Feature | Phoenix (OSS) | Arize Cloud |
|---------|---------------|-------------|
| **Deployment** | Local | Cloud SaaS |
| **Cost** | Free | Paid (free tier available) |
| **Setup** | Run server locally | API keys required |
| **Data** | Stays on your machine | Sent to Arize servers |
| **UI** | Web UI (localhost:6006) | Web dashboard |
| **Features** | Traces, metrics | Advanced drift detection, alerts, model monitoring |
| **Best For** | Development, debugging | Production monitoring |

## Advanced: Running Phoenix in Production

For production deployments:

1. **Run Phoenix on dedicated server:**
   ```bash
   # On server (e.g., AWS EC2, Azure VM)
   python -m phoenix.server.main serve --host 0.0.0.0 --port 6006
   ```

2. **Update `.env` with server URL:**
   ```bash
   PHOENIX_COLLECTOR_ENDPOINT=http://your-phoenix-server:6006
   ```

3. **Secure with authentication** (Phoenix Pro feature or reverse proxy)

4. **Consider Arize Cloud** for enterprise features

## Resources

- **Phoenix Docs**: https://docs.arize.com/phoenix
- **GitHub**: https://github.com/Arize-ai/phoenix
- **Discord**: Join Arize Discord for support

---

**Status**: Phoenix integration complete and tested ✅

**Next**: Start Phoenix server and make some predictions!
