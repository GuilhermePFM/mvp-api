#!/bin/bash
set -e

echo "🚀 Starting Controle Financeiro API..."

# Create necessary directories if they don't exist
echo "📁 Creating necessary directories..."
mkdir -p /app/database
mkdir -p /app/log

# Check if required environment variables are set
echo "🔍 Checking environment variables..."

if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  WARNING: GEMINI_API_KEY is not set. ML classification may not work properly."
fi

if [ -z "$ENC_KEY" ]; then
    echo "⚠️  WARNING: ENC_KEY is not set. Encryption features may not work properly."
fi

# Check if ML models exist
echo "🤖 Checking ML models..."
MODEL_PATH="${MODEL_PATH:-/app/machine_learning}"

if [ -f "$MODEL_PATH/classification_model.pkl" ]; then
    echo "✅ ML model found at $MODEL_PATH/classification_model.pkl"
else
    echo "⚠️  WARNING: ML model not found at $MODEL_PATH/classification_model.pkl"
    echo "   Classification features may not work properly."
fi

# Check if preprocessor exists
PREPROCESSOR_PATH="/app/machine_learning/transactions_classification/pipelines/classification_preprocessor.pkl"
if [ -f "$PREPROCESSOR_PATH" ]; then
    echo "✅ Preprocessor found at $PREPROCESSOR_PATH"
else
    echo "⚠️  WARNING: Preprocessor not found at $PREPROCESSOR_PATH"
fi

echo "✅ Pre-flight checks completed!"
echo "🌐 Starting application..."
echo ""

# Execute the command passed to the entrypoint
exec "$@"

