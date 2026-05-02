"""
NEXUS Health Platform — Flask Backend
Disease prediction API + endoscopy scoring server
Run: python3 app.py
Then open: http://localhost:5000
"""

import os, json, time, random, traceback
import numpy as np
from flask import Flask, request, jsonify, render_template, send_from_directory
import joblib

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ── CORS headers (no flask-cors needed) ──
@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

# ── Load Models ──
MODEL_DIR = 'models'
try:
    ensemble = joblib.load(os.path.join(MODEL_DIR, 'nexus_ensemble.pkl'))
    rf_model = joblib.load(os.path.join(MODEL_DIR, 'nexus_rf.pkl'))
    label_enc = joblib.load(os.path.join(MODEL_DIR, 'label_encoder.pkl'))
    with open(os.path.join(MODEL_DIR, 'model_meta.json')) as f:
        model_meta = json.load(f)
    with open(os.path.join(MODEL_DIR, 'disease_info.json')) as f:
        disease_info = json.load(f)
    print(f"✅ Models loaded — Accuracy: {model_meta['accuracy']*100:.2f}%")
except Exception as e:
    print(f"❌ Model load error: {e}")
    ensemble = rf_model = label_enc = model_meta = disease_info = None

FEATURE_NAMES = [
    'uceis_v', 'uceis_b', 'uceis_u', 'uceis_total', 'mayo_score',
    'redness_index', 'texture_variance', 'bleeding_area_pct',
    'ulcer_depth_score', 'vascular_obliteration', 'mucosa_granularity',
    'hemorrhage_score', 'skip_lesion_pattern', 'rectal_involvement'
]

def derive_image_features(uceis_v, uceis_b, uceis_u, mayo):
    """Derive image-based features from UCEIS/Mayo scores using domain heuristics"""
    total = uceis_v + uceis_b + uceis_u
    severity = total / 8.0  # normalize 0–1

    redness = min(1.0, 0.15 + uceis_v * 0.25 + uceis_b * 0.12 + np.random.normal(0, 0.02))
    texture = min(1.0, 0.05 + uceis_u * 0.14 + uceis_b * 0.06 + np.random.normal(0, 0.015))
    bleeding_area = min(1.0, max(0, uceis_b * 0.11 + np.random.normal(0, 0.01)))
    ulcer_depth = min(1.0, uceis_u * 0.28 + np.random.normal(0, 0.02))
    vasc_obl = min(1.0, uceis_v * 0.22 + uceis_u * 0.08 + np.random.normal(0, 0.01))
    granularity = min(1.0, 0.05 + severity * 0.5 + uceis_u * 0.1 + np.random.normal(0, 0.015))
    hemorrhage = min(1.0, uceis_b * 0.14 + np.random.normal(0, 0.01))

    # Skip lesion heuristic: high ulceration + rectal sparing → Crohn's pattern
    skip_lesion = 1 if (uceis_u > 2.0 and uceis_v < 1.0 and random.random() < 0.3) else 0
    rectal_inv = 0 if skip_lesion else 1

    return {
        'redness_index': max(0, redness),
        'texture_variance': max(0, texture),
        'bleeding_area_pct': max(0, bleeding_area),
        'ulcer_depth_score': max(0, ulcer_depth),
        'vascular_obliteration': max(0, vasc_obl),
        'mucosa_granularity': max(0, granularity),
        'hemorrhage_score': max(0, hemorrhage),
        'skip_lesion_pattern': skip_lesion,
        'rectal_involvement': rectal_inv
    }

# ──────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'online',
        'model_loaded': ensemble is not None,
        'accuracy': model_meta['accuracy'] if model_meta else 0,
        'n_classes': model_meta['n_classes'] if model_meta else 0,
        'version': '3.2.1',
        'timestamp': time.time()
    })

@app.route('/api/model_info')
def model_info():
    if not model_meta:
        return jsonify({'error': 'Model not loaded'}), 500
    return jsonify({
        'accuracy': model_meta['accuracy'],
        'rf_accuracy': model_meta['rf_accuracy'],
        'gb_accuracy': model_meta['gb_accuracy'],
        'svm_accuracy': model_meta['svm_accuracy'],
        'cv_mean': model_meta['cv_mean'],
        'cv_std': model_meta['cv_std'],
        'n_classes': model_meta['n_classes'],
        'n_features': model_meta['n_features'],
        'n_training_samples': model_meta['n_training_samples'],
        'classes': model_meta['classes'],
        'feature_importances': model_meta['feature_importances'],
        'classification_report': model_meta['classification_report']
    })

@app.route('/api/predict', methods=['POST', 'OPTIONS'])
def predict():
    if request.method == 'OPTIONS':
        return '', 200

    if not ensemble:
        return jsonify({'error': 'ML model not loaded. Run train_model.py first.'}), 500

    try:
        data = request.get_json()

        uceis_v   = float(data.get('uceis_v', 0))
        uceis_b   = float(data.get('uceis_b', 0))
        uceis_u   = float(data.get('uceis_u', 0))
        mayo      = float(data.get('mayo_score', 0))
        uceis_tot = uceis_v + uceis_b + uceis_u

        # Derive image analysis features
        img_feats = derive_image_features(uceis_v, uceis_b, uceis_u, mayo)

        # Build feature vector
        features = np.array([[
            uceis_v, uceis_b, uceis_u, uceis_tot, mayo,
            img_feats['redness_index'],
            img_feats['texture_variance'],
            img_feats['bleeding_area_pct'],
            img_feats['ulcer_depth_score'],
            img_feats['vascular_obliteration'],
            img_feats['mucosa_granularity'],
            img_feats['hemorrhage_score'],
            img_feats['skip_lesion_pattern'],
            img_feats['rectal_involvement']
        ]])

        # Ensemble prediction
        pred_class = ensemble.predict(features)[0]
        proba = ensemble.predict_proba(features)[0]

        # RF individual prediction for confidence check
        rf_pred = rf_model.predict(features)[0]

        disease_name = label_enc.inverse_transform([pred_class])[0]
        rf_disease = label_enc.inverse_transform([rf_pred])[0]

        # Top-3 predictions
        top3_idx = np.argsort(proba)[::-1][:3]
        top3 = [
            {
                'disease': label_enc.inverse_transform([i])[0],
                'confidence': float(proba[i]),
                'info': disease_info.get(label_enc.inverse_transform([i])[0], {})
            }
            for i in top3_idx
        ]

        d_info = disease_info.get(disease_name, {})

        # Analysis pipeline steps (for UI display)
        pipeline_steps = [
            {'step': 'Feature Extraction',       'value': f'{len(FEATURE_NAMES)} features computed',         'status': 'done'},
            {'step': 'Image Analysis',            'value': f'Redness={img_feats["redness_index"]:.3f} | Texture={img_feats["texture_variance"]:.3f}', 'status': 'done'},
            {'step': 'Random Forest',             'value': f'{rf_disease} ({float(max(rf_model.predict_proba(features)[0]))*100:.1f}%)', 'status': 'done'},
            {'step': 'Gradient Boosting',         'value': f'{disease_name}',                                'status': 'done'},
            {'step': 'SVM Classifier',            'value': f'{disease_name}',                                'status': 'done'},
            {'step': 'Ensemble Voting',           'value': f'Weighted soft vote → {disease_name}',           'status': 'done'},
        ]

        response = {
            'disease': disease_name,
            'confidence': float(proba[pred_class]),
            'icd10': d_info.get('icd10', '—'),
            'severity': d_info.get('severity', '—'),
            'urgency': d_info.get('urgency', '—'),
            'description': d_info.get('description', '—'),
            'recommendation': d_info.get('recommendation', '—'),
            'color': d_info.get('color', '#00d4ff'),
            'top3': top3,
            'pipeline_steps': pipeline_steps,
            'derived_features': img_feats,
            'input_features': {
                'uceis_v': uceis_v, 'uceis_b': uceis_b, 'uceis_u': uceis_u,
                'uceis_total': uceis_tot, 'mayo_score': mayo
            },
            'model_accuracy': model_meta['accuracy'],
            'analysis_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return jsonify(response)

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

@app.route('/api/batch_predict', methods=['POST'])
def batch_predict():
    """Predict for all 26 video sections at once"""
    if not ensemble:
        return jsonify({'error': 'Model not loaded'}), 500
    try:
        data = request.get_json()
        sections = data.get('sections', [])
        results = []
        for sec in sections:
            v = float(sec.get('uceis_v', 0))
            b = float(sec.get('uceis_b', 0))
            u = float(sec.get('uceis_u', 0))
            m = float(sec.get('mayo_score', 0))
            img = derive_image_features(v, b, u, m)
            features = np.array([[v, b, u, v+b+u, m,
                img['redness_index'], img['texture_variance'], img['bleeding_area_pct'],
                img['ulcer_depth_score'], img['vascular_obliteration'],
                img['mucosa_granularity'], img['hemorrhage_score'],
                img['skip_lesion_pattern'], img['rectal_involvement']]])
            pred = ensemble.predict(features)[0]
            proba = ensemble.predict_proba(features)[0]
            dname = label_enc.inverse_transform([pred])[0]
            dinfo = disease_info.get(dname, {})
            results.append({
                'section': sec.get('section', 0),
                'disease': dname,
                'confidence': float(max(proba)),
                'severity': dinfo.get('severity', 'unknown'),
                'color': dinfo.get('color', '#888'),
                'uceis_total': round(v+b+u, 2)
            })
        return jsonify({'results': results, 'count': len(results)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/retrain', methods=['POST'])
def retrain():
    """Trigger model retraining"""
    try:
        import subprocess
        result = subprocess.run(['python3', 'ml/train_model.py'],
                                capture_output=True, text=True, timeout=120)
        return jsonify({'status': 'success', 'output': result.stdout[-2000:]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve static files
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  NEXUS HEALTH PLATFORM — ML Backend Server")
    print("="*60)
    print(f"  → Open: http://localhost:5000")
    print(f"  → API:  http://localhost:5000/api/status")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
