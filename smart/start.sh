#!/bin/bash
# NEXUS Health Platform — Startup Script
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         NEXUS HEALTH PLATFORM — STARTUP                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")"

# Install dependencies
echo "📦 Installing dependencies..."
pip install flask scikit-learn numpy pandas joblib opencv-python-headless Pillow --break-system-packages -q 2>/dev/null || \
pip3 install flask scikit-learn numpy pandas joblib opencv-python-headless Pillow -q 2>/dev/null

# Train model if not exists
if [ ! -f "models/nexus_ensemble.pkl" ]; then
    echo "🧠 Training ML models (first run — takes ~30 seconds)..."
    python3 ml/train_model.py
else
    echo "✅ ML models already trained"
fi

echo ""
echo "🚀 Starting NEXUS Health Platform..."
echo "   → http://localhost:5000"
echo ""

python3 app.py
