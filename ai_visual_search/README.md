# AI Visual Search

Minimal backend for fashion visual search using GroundingDINO + CLIP embeddings.

## Features

- **Object Detection**: GroundingDINO with optimized fashion prompts (0.18 confidence threshold)
- **Embedding Generation**: OpenCLIP ViT-L/14 (768-dim embeddings)
- **Preprocessing**: 224x224 square padding with quality checks
- **CPU Optimized**: 2-thread limit for thermal management

## Architecture

```
ai_visual_search/
├── detector/                    # GroundingDINO detection
│   ├── grounding_dino_sam2_detector.py
│   └── prompts.py              # Fashion-optimized prompts
├── embedder/                    # CLIP embeddings
│   ├── clip_embedder.py        # ViT-L/14 model
│   └── preprocess.py           # 224x224 preprocessing
├── utils/                       # Utilities
│   ├── image_utils.py
│   ├── logger.py
│   └── timer.py
├── api/                         # FastAPI routes
│   └── visual_routes.py        # 2 endpoints
├── config.py                    # Configuration
├── app.py                       # FastAPI application
└── requirements.txt             # Dependencies
```

## API Endpoints

### 1. Detect Objects
```bash
POST /api/visual/detect-objects
```

**Parameters:**
- `file`: Image file
- `confidence`: Confidence threshold (default: 0.18)
- `max_detections`: Max detections (default: 25)

**Response:**
```json
{
  "detections": [
    {
      "bbox": [x1, y1, x2, y2],
      "label": "shirt",
      "confidence": 0.85,
      "class_id": 0
    }
  ],
  "image_size": [width, height]
}
```

### 2. Generate Embedding
```bash
POST /api/visual/embed
```

**Parameters:**
- `file`: Image file
- `bbox`: Optional crop coordinates as "x1,y1,x2,y2"

**Response:**
```json
{
  "embedding": [768-dim array],
  "dimension": 768,
  "cropped": true/false,
  "bbox": [x1, y1, x2, y2]
}
```

## Installation

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Start Server
```bash
python app.py
```

Server runs on `http://localhost:5000`

### Test Pipeline
```bash
python test_pipeline.py
```

Tests complete flow: Detect → Crop → Preprocess → Embed

## Configuration

Edit `config.py` or use environment variables:

```bash
# Detection
DINO_BOX_THRESHOLD=0.18
DINO_TEXT_THRESHOLD=0.18
DINO_MAX_DETECTIONS=25

# API
API_HOST=0.0.0.0
API_PORT=5000

# Logging
LOG_LEVEL=INFO
```

## Fashion Prompts

Multi-phrase descriptive prompts with visual cues (color, style, gender):

```python
"men shirt . long sleeve shirt . brown shirt . collar shirt . "
"pants . black pants . formal pants . men's trousers . "
"watch . wrist watch . men's watch . analog watch . "
"sunglasses . eyeglasses . men's sunglasses . "
```

## Performance

- **Detection**: ~8-12 seconds (first call), ~2-3 seconds (subsequent)
- **Embedding**: ~0.5-1 second
- **Memory**: <3GB RAM
- **CPU**: 2 threads (thermal optimized)

## Requirements

- Python 3.11+
- CPU-only PyTorch
- 16GB RAM recommended
- Windows 10/11

## License

Internal project - HypeLens AI
