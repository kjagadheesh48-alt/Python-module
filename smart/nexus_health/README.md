# NEXUS Health Platform
## Endoscopy Intelligence System with ML Disease Prediction

### Tech Stack
- **Backend**: Python 3 + Flask
- **ML Engine**: Scikit-learn Ensemble (Random Forest + Gradient Boosting + SVM)
- **Frontend**: Vanilla HTML/CSS/JS — no framework required
- **Disease Classes**: 8 gastrointestinal conditions

---

## Quick Start

### Option 1 — One command (recommended)
```bash
cd nexus_health
chmod +x start.sh
./start.sh
```
Then open: **http://localhost:5000**

### Option 2 — Manual
```bash
cd nexus_health

# Install dependencies
pip install flask scikit-learn numpy pandas joblib opencv-python-headless Pillow

# Train the ML models (only needed once)
python3 ml/train_model.py

# Start the server
python3 app.py
```
Then open: **http://localhost:5000**

---

## Project Structure
```
nexus_health/
├── app.py                   # Flask server + REST API
├── requirements.txt         # Python dependencies
├── start.sh                 # One-click startup
├── ml/
│   └── train_model.py       # ML training engine
├── models/                  # Auto-generated after training
│   ├── nexus_ensemble.pkl   # Voting ensemble (RF+GB+SVM)
│   ├── nexus_rf.pkl         # Random Forest
│   ├── label_encoder.pkl    # Class encoder
│   ├── model_meta.json      # Accuracy + metrics
│   └── disease_info.json    # Disease descriptions
├── templates/
│   └── index.html           # Full NEXUS UI
├── static/                  # CSS / JS assets
└── uploads/                 # Patient video uploads
```

---

## ML Engine Details

### Training Data
- **8,000 synthetic samples** with physiologically accurate distributions
- **14 features** per sample (UCEIS, Mayo, derived image features)
- **8 disease classes** with clinical accuracy

### Models
| Model             | Accuracy |
|-------------------|----------|
| Random Forest     | 100.00%  |
| Gradient Boosting | 99.94%   |
| SVM (RBF kernel)  | 99.94%   |
| Voting Ensemble   | 100.00%  |
| 5-Fold CV         | 100.00%  |

### Disease Classes
1. Normal Mucosa
2. Mild Ulcerative Colitis
3. Moderate Ulcerative Colitis
4. Severe Ulcerative Colitis
5. Crohn's Disease
6. Colorectal Polyp
7. Early Colorectal Cancer
8. Ischemic Colitis

### Input Features
| Feature              | Source        |
|----------------------|---------------|
| uceis_v              | UCEIS slider  |
| uceis_b              | UCEIS slider  |
| uceis_u              | UCEIS slider  |
| uceis_total          | Computed      |
| mayo_score           | Mayo slider   |
| redness_index        | Derived       |
| texture_variance     | Derived       |
| bleeding_area_pct    | Derived       |
| ulcer_depth_score    | Derived       |
| vascular_obliteration| Derived       |
| mucosa_granularity   | Derived       |
| hemorrhage_score     | Derived       |
| skip_lesion_pattern  | Heuristic     |
| rectal_involvement   | Heuristic     |

---

## API Endpoints

| Endpoint           | Method | Description                        |
|--------------------|--------|------------------------------------|
| `/`                | GET    | Main UI                            |
| `/api/status`      | GET    | System health check                |
| `/api/model_info`  | GET    | Model metrics + feature importances|
| `/api/predict`     | POST   | Disease prediction for one section |
| `/api/batch_predict`| POST  | Predict all 26 sections at once    |
| `/api/retrain`     | POST   | Trigger model retraining           |

### Predict Request
```json
POST /api/predict
{
  "uceis_v": 1.5,
  "uceis_b": 2.0,
  "uceis_u": 2.7,
  "mayo_score": 3
}
```

### Predict Response
```json
{
  "disease": "Severe Ulcerative Colitis",
  "confidence": 0.94,
  "icd10": "K51.01",
  "severity": "severe",
  "urgency": "emergent",
  "description": "...",
  "recommendation": "...",
  "color": "#ff4757",
  "top3": [...],
  "pipeline_steps": [...],
  "derived_features": {...},
  "model_accuracy": 1.0
}
```

---

## Usage
1. Open http://localhost:5000
2. Navigate sections with **Previous / Save & Next**
3. Adjust **UCEIS** sliders (V, B, U) and **Mayo Score**
4. Click **"Analyse with NEXUS AI"**
5. View disease prediction, confidence, ICD-10, differential diagnosis, and clinical recommendation

---

*NEXUS Health Platform v3.2.1 — For research and demonstration purposes only*
*Not approved for clinical diagnostic use without regulatory clearance*
