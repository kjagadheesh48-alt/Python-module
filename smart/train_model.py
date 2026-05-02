"""
NEXUS Health - Endoscopy Disease Prediction ML Engine
Trains multiple classifiers on simulated endoscopic scoring data
Disease classes: Normal, Mild UC, Moderate UC, Severe UC, Crohn's Disease,
                 Colorectal Polyp, Colorectal Cancer, Ischemic Colitis
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline
import joblib
import json
import os
import warnings
warnings.filterwarnings('ignore')

# ── Disease Labels ──
DISEASES = [
    "Normal Mucosa",
    "Mild Ulcerative Colitis",
    "Moderate Ulcerative Colitis",
    "Severe Ulcerative Colitis",
    "Crohn's Disease",
    "Colorectal Polyp",
    "Early Colorectal Cancer",
    "Ischemic Colitis"
]

DISEASE_INFO = {
    "Normal Mucosa": {
        "icd10": "K63.89",
        "severity": "none",
        "urgency": "routine",
        "description": "No pathological findings. Mucosa appears healthy with normal vascular pattern.",
        "recommendation": "Continue routine surveillance. No immediate intervention required.",
        "color": "#00ff9d"
    },
    "Mild Ulcerative Colitis": {
        "icd10": "K51.00",
        "severity": "mild",
        "urgency": "outpatient",
        "description": "Mild mucosal inflammation with slight erythema and preserved vascular pattern.",
        "recommendation": "5-ASA therapy initiation. Follow-up colonoscopy in 3 months.",
        "color": "#ffb830"
    },
    "Moderate Ulcerative Colitis": {
        "icd10": "K51.01",
        "severity": "moderate",
        "urgency": "urgent",
        "description": "Moderate inflammation with erosions, contact bleeding and distorted vascular pattern.",
        "recommendation": "Oral/IV corticosteroids. Gastroenterology consult within 48 hours.",
        "color": "#ff7c45"
    },
    "Severe Ulcerative Colitis": {
        "icd10": "K51.01",
        "severity": "severe",
        "urgency": "emergent",
        "description": "Severe mucosal ulceration, spontaneous bleeding and complete vascular obliteration.",
        "recommendation": "Immediate hospitalization. IV steroids + biologic therapy consideration.",
        "color": "#ff4757"
    },
    "Crohn's Disease": {
        "icd10": "K50.10",
        "severity": "moderate",
        "urgency": "urgent",
        "description": "Skip lesions with cobblestone mucosa, deep linear ulcers and rectal sparing.",
        "recommendation": "Immunomodulator therapy. MR enterography for full bowel assessment.",
        "color": "#a55eea"
    },
    "Colorectal Polyp": {
        "icd10": "K63.5",
        "severity": "low",
        "urgency": "semi-urgent",
        "description": "Mucosal protrusion detected. Pattern analysis suggests adenomatous morphology.",
        "recommendation": "Endoscopic polypectomy during current or next session. Histology required.",
        "color": "#00d4ff"
    },
    "Early Colorectal Cancer": {
        "icd10": "C18.9",
        "severity": "high",
        "urgency": "emergent",
        "description": "Irregular mucosal mass with disrupted pit pattern. High suspicion of malignancy.",
        "recommendation": "Urgent oncology referral. CT staging required within 72 hours.",
        "color": "#ff2d55"
    },
    "Ischemic Colitis": {
        "icd10": "K55.9",
        "severity": "moderate",
        "urgency": "urgent",
        "description": "Segmental mucosal pallor with submucosal hemorrhage. Classic watershed distribution.",
        "recommendation": "IV fluids, bowel rest, cardiology assessment for underlying vascular cause.",
        "color": "#fd9644"
    }
}

def generate_training_data(n_samples=5000, random_state=42):
    """
    Generate realistic synthetic endoscopy scoring data
    Features: uceis_v, uceis_b, uceis_u, uceis_total, mayo_score,
              redness_index, texture_variance, bleeding_area_pct,
              ulcer_depth_score, vascular_obliteration, mucosa_granularity,
              hemorrhage_score, skip_lesion_pattern, rectal_involvement
    """
    np.random.seed(random_state)
    data = []

    samples_per_class = n_samples // len(DISEASES)

    # Normal Mucosa
    for _ in range(samples_per_class):
        v = np.random.uniform(0, 0.3)
        b = np.random.uniform(0, 0.2)
        u = np.random.uniform(0, 0.2)
        data.append([v, b, u, v+b+u,
                     np.random.randint(0,1),
                     np.random.uniform(0.1,0.25), np.random.uniform(0.02,0.08),
                     np.random.uniform(0,0.02), np.random.uniform(0,0.1),
                     np.random.uniform(0,0.05), np.random.uniform(0.05,0.15),
                     np.random.uniform(0,0.02), 0, 1,
                     "Normal Mucosa"])

    # Mild UC
    for _ in range(samples_per_class):
        v = np.random.uniform(0.3, 0.8)
        b = np.random.uniform(0.2, 0.8)
        u = np.random.uniform(0.2, 0.6)
        data.append([v, b, u, v+b+u,
                     np.random.randint(0,2),
                     np.random.uniform(0.3,0.5), np.random.uniform(0.1,0.2),
                     np.random.uniform(0.02,0.08), np.random.uniform(0.1,0.3),
                     np.random.uniform(0.05,0.2), np.random.uniform(0.15,0.3),
                     np.random.uniform(0.02,0.1), 0, 1,
                     "Mild Ulcerative Colitis"])

    # Moderate UC
    for _ in range(samples_per_class):
        v = np.random.uniform(0.8, 1.5)
        b = np.random.uniform(0.8, 1.8)
        u = np.random.uniform(0.8, 1.8)
        data.append([v, b, u, v+b+u,
                     np.random.randint(1,3),
                     np.random.uniform(0.5,0.7), np.random.uniform(0.2,0.35),
                     np.random.uniform(0.08,0.2), np.random.uniform(0.3,0.6),
                     np.random.uniform(0.2,0.4), np.random.uniform(0.3,0.5),
                     np.random.uniform(0.1,0.25), 0, 1,
                     "Moderate Ulcerative Colitis"])

    # Severe UC
    for _ in range(samples_per_class):
        v = np.random.uniform(1.5, 2.0)
        b = np.random.uniform(1.8, 3.0)
        u = np.random.uniform(1.8, 3.0)
        data.append([v, b, u, v+b+u,
                     np.random.randint(2,4),
                     np.random.uniform(0.7,0.95), np.random.uniform(0.35,0.55),
                     np.random.uniform(0.2,0.45), np.random.uniform(0.6,0.95),
                     np.random.uniform(0.4,0.8), np.random.uniform(0.5,0.85),
                     np.random.uniform(0.25,0.6), 0, 1,
                     "Severe Ulcerative Colitis"])

    # Crohn's Disease - skip lesions, rectal sparing
    for _ in range(samples_per_class):
        v = np.random.uniform(0.5, 1.8)
        b = np.random.uniform(0.3, 2.0)
        u = np.random.uniform(1.0, 3.0)
        data.append([v, b, u, v+b+u,
                     np.random.randint(1,4),
                     np.random.uniform(0.35,0.65), np.random.uniform(0.25,0.5),
                     np.random.uniform(0.05,0.3), np.random.uniform(0.5,0.9),
                     np.random.uniform(0.1,0.4), np.random.uniform(0.4,0.75),
                     np.random.uniform(0.05,0.3), 1, 0,  # skip=1, rectal_sparing=0
                     "Crohn's Disease"])

    # Colorectal Polyp - focal, low bleeding
    for _ in range(samples_per_class):
        v = np.random.uniform(0.1, 0.6)
        b = np.random.uniform(0.0, 0.4)
        u = np.random.uniform(0.0, 0.3)
        data.append([v, b, u, v+b+u,
                     np.random.randint(0,2),
                     np.random.uniform(0.15,0.35), np.random.uniform(0.3,0.6),
                     np.random.uniform(0.0,0.05), np.random.uniform(0.05,0.2),
                     np.random.uniform(0.0,0.1), np.random.uniform(0.2,0.45),
                     np.random.uniform(0.0,0.05), 0, 1,
                     "Colorectal Polyp"])

    # Early Colorectal Cancer - high texture, irregular
    for _ in range(samples_per_class):
        v = np.random.uniform(0.8, 2.0)
        b = np.random.uniform(0.5, 2.5)
        u = np.random.uniform(1.0, 3.0)
        data.append([v, b, u, v+b+u,
                     np.random.randint(2,4),
                     np.random.uniform(0.5,0.85), np.random.uniform(0.55,0.85),
                     np.random.uniform(0.1,0.35), np.random.uniform(0.5,0.9),
                     np.random.uniform(0.3,0.7), np.random.uniform(0.55,0.9),
                     np.random.uniform(0.15,0.4), 0, 1,
                     "Early Colorectal Cancer"])

    # Ischemic Colitis - pallor, low ulceration, segmental
    for _ in range(samples_per_class):
        v = np.random.uniform(0.3, 1.2)
        b = np.random.uniform(0.5, 2.0)
        u = np.random.uniform(0.2, 1.5)
        data.append([v, b, u, v+b+u,
                     np.random.randint(1,3),
                     np.random.uniform(0.15,0.4), np.random.uniform(0.15,0.35),
                     np.random.uniform(0.05,0.25), np.random.uniform(0.2,0.55),
                     np.random.uniform(0.1,0.35), np.random.uniform(0.25,0.5),
                     np.random.uniform(0.15,0.45), 0, 1,
                     "Ischemic Colitis"])

    cols = ['uceis_v', 'uceis_b', 'uceis_u', 'uceis_total', 'mayo_score',
            'redness_index', 'texture_variance', 'bleeding_area_pct',
            'ulcer_depth_score', 'vascular_obliteration', 'mucosa_granularity',
            'hemorrhage_score', 'skip_lesion_pattern', 'rectal_involvement', 'disease']

    return pd.DataFrame(data, columns=cols)


def train_and_save(model_dir='models'):
    os.makedirs(model_dir, exist_ok=True)
    print("🔬 NEXUS ML Engine — Generating training data...")
    df = generate_training_data(n_samples=8000)

    X = df.drop('disease', axis=1)
    y = df['disease']

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc)

    print(f"   Training samples: {len(X_train)}, Test samples: {len(X_test)}")
    print(f"   Feature count: {X.shape[1]}")
    print(f"   Classes: {len(le.classes_)}")

    # ── Build ensemble ──
    rf = RandomForestClassifier(n_estimators=200, max_depth=12, min_samples_split=4,
                                 class_weight='balanced', random_state=42, n_jobs=-1)
    gb = GradientBoostingClassifier(n_estimators=150, learning_rate=0.08,
                                     max_depth=5, random_state=42)
    svm = Pipeline([
        ('scaler', StandardScaler()),
        ('svc', SVC(kernel='rbf', C=10, gamma='scale',
                    probability=True, random_state=42, class_weight='balanced'))
    ])

    print("\n🧠 Training Random Forest...")
    rf.fit(X_train, y_train)
    rf_acc = accuracy_score(y_test, rf.predict(X_test))
    print(f"   RF Accuracy: {rf_acc*100:.2f}%")

    print("🧠 Training Gradient Boosting...")
    gb.fit(X_train, y_train)
    gb_acc = accuracy_score(y_test, gb.predict(X_test))
    print(f"   GB Accuracy: {gb_acc*100:.2f}%")

    print("🧠 Training SVM...")
    svm.fit(X_train, y_train)
    svm_acc = accuracy_score(y_test, svm.predict(X_test))
    print(f"   SVM Accuracy: {svm_acc*100:.2f}%")

    # ── Voting ensemble ──
    print("🧠 Building Voting Ensemble...")
    ensemble = VotingClassifier(
        estimators=[('rf', rf), ('gb', gb), ('svm', svm)],
        voting='soft',
        weights=[3, 2, 1]
    )
    ensemble.fit(X_train, y_train)
    ens_acc = accuracy_score(y_test, ensemble.predict(X_test))
    print(f"   Ensemble Accuracy: {ens_acc*100:.2f}%")

    # ── Detailed report ──
    y_pred = ensemble.predict(X_test)
    report = classification_report(y_test, y_pred,
                                   target_names=le.classes_, output_dict=True)

    print("\n📊 Classification Report:")
    for cls, metrics in report.items():
        if isinstance(metrics, dict) and 'f1-score' in metrics:
            print(f"   {cls[:30]:30s} F1={metrics['f1-score']:.3f}  Prec={metrics['precision']:.3f}  Rec={metrics['recall']:.3f}")

    # ── Cross-validation ──
    cv_scores = cross_val_score(rf, X, y_enc, cv=5, scoring='accuracy')
    print(f"\n✅ 5-Fold CV Accuracy: {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%")

    # ── Feature importance ──
    feat_imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
    print("\n🔍 Top Feature Importances:")
    for feat, imp in feat_imp.head(8).items():
        print(f"   {feat:30s} {imp:.4f}")

    # ── Save artifacts ──
    joblib.dump(ensemble, os.path.join(model_dir, 'nexus_ensemble.pkl'))
    joblib.dump(rf, os.path.join(model_dir, 'nexus_rf.pkl'))
    joblib.dump(le, os.path.join(model_dir, 'label_encoder.pkl'))

    meta = {
        'accuracy': float(ens_acc),
        'rf_accuracy': float(rf_acc),
        'gb_accuracy': float(gb_acc),
        'svm_accuracy': float(svm_acc),
        'cv_mean': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std()),
        'n_classes': int(len(le.classes_)),
        'n_features': int(X.shape[1]),
        'n_training_samples': int(len(X_train)),
        'classes': le.classes_.tolist(),
        'feature_names': X.columns.tolist(),
        'feature_importances': feat_imp.to_dict(),
        'classification_report': report
    }
    with open(os.path.join(model_dir, 'model_meta.json'), 'w') as f:
        json.dump(meta, f, indent=2)

    with open(os.path.join(model_dir, 'disease_info.json'), 'w') as f:
        json.dump(DISEASE_INFO, f, indent=2)

    print(f"\n💾 Models saved to '{model_dir}/'")
    print("   ✅ nexus_ensemble.pkl")
    print("   ✅ nexus_rf.pkl")
    print("   ✅ label_encoder.pkl")
    print("   ✅ model_meta.json")
    print("   ✅ disease_info.json")
    return meta


if __name__ == '__main__':
    meta = train_and_save()
    print(f"\n🎯 Final Ensemble Accuracy: {meta['accuracy']*100:.2f}%")
