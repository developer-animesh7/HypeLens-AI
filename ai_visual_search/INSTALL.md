# Installation Guide - AI Visual Search

## Prerequisites

- **Python**: 3.11+
- **OS**: Windows 10/11
- **RAM**: 16GB recommended
- **CPU**: Multi-core processor (will use 2 threads)

## Step 1: Clone Repository

```bash
git clone https://github.com/developer-animesh7/HELLO-.git
cd HELLO-
git checkout visual-search
cd ai_visual_search
```

## Step 2: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: This will install:
- PyTorch (CPU version)
- FastAPI + Uvicorn
- GroundingDINO
- OpenCLIP
- Pillow & NumPy

Installation may take 5-10 minutes.

## Step 4: Download Models

### GroundingDINO Model

Download `groundingdino_swint_ogc.pth` to `models/` folder:
- **Source**: [GroundingDINO GitHub](https://github.com/IDEA-Research/GroundingDINO)
- **Size**: ~600MB

### GroundingDINO Config

Download `GroundingDINO_SwinT_OGC.py` to `models/` folder:
- **Source**: Same as above

**Model folder structure:**
```
models/
├── groundingdino_swint_ogc.pth
└── GroundingDINO_SwinT_OGC.py
```

## Step 5: Test Installation

```bash
cd ..
python test_pipeline.py
```

**Expected output:**
```
STEP 1: Object Detection → OK
STEP 2: Crop → OK
STEP 3: Preprocess → OK
STEP 4: CLIP Embedding (768-dim) → OK

✅ PIPELINE TEST COMPLETE
```

## Step 6: Start Server

```bash
cd ai_visual_search
python app.py
```

**Server will start on:** `http://localhost:5000`

## Step 7: Verify API

Open new terminal:

```bash
curl http://localhost:5000/health
```

**Expected response:**
```json
{"status": "healthy"}
```

## API Endpoints

### 1. Detect Objects

```bash
curl -X POST http://localhost:5000/api/visual/detect-objects \
  -F "file=@image.jpg" \
  -F "confidence=0.18" \
  -F "max_detections=25"
```

### 2. Generate Embedding

```bash
curl -X POST http://localhost:5000/api/visual/embed \
  -F "file=@image.jpg"
```

## Troubleshooting

### Issue: torch.set_num_threads error
**Solution**: This is handled automatically. Server runs with `reload=False`.

### Issue: Models not found
**Solution**: Ensure models are in `models/` folder relative to project root.

### Issue: CUDA error
**Solution**: This is CPU-only. Ensure you have CPU version of PyTorch.

### Issue: Port 5000 in use
**Solution**: Stop existing process or change port in `config.py`:
```python
API_PORT = 5001  # Change to available port
```

## Configuration

Edit `config.py` for settings:

```python
# Detection thresholds
DINO_BOX_THRESHOLD = 0.18
DINO_TEXT_THRESHOLD = 0.18
DINO_MAX_DETECTIONS = 25

# API settings
API_HOST = "0.0.0.0"
API_PORT = 5000

# Logging
LOG_LEVEL = "INFO"
```

## Performance Notes

- **First detection**: 8-12 seconds (model loading)
- **Subsequent detections**: 2-3 seconds
- **Embeddings**: 0.5-1 second
- **Memory usage**: <3GB RAM
- **CPU threads**: 2 (thermal optimized)

## Next Steps

- Test with your own fashion images
- Integrate with your frontend
- Adjust prompts in `detector/prompts.py` for your use case

## Support

For issues, check:
- `README.md` - Full documentation
- `DEPLOYMENT_SUMMARY.md` - Test results
- GitHub Issues: [HELLO- Repository](https://github.com/developer-animesh7/HELLO-)
