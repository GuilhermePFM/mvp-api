#!/bin/bash
set -e

WORKER_TYPE="${WORKER_TYPE:-api}"

echo "🚀 Starting Controle Financeiro ($WORKER_TYPE)..."

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

# Worker-specific checks
if [ "$WORKER_TYPE" != "api" ]; then
    echo "🔧 Worker mode: $WORKER_TYPE"
    
    if [ -z "$KAFKA_BROKER_ADDRESS" ]; then
        echo "❌ ERROR: KAFKA_BROKER_ADDRESS is required for workers"
        exit 1
    fi
    
    if [ -z "$EMBEDDING_API_URL" ]; then
        echo "⚠️  WARNING: EMBEDDING_API_URL not set (required for embeddings worker)"
    fi
    
    # Wait for Kafka to be ready
    echo "⏳ Waiting for Kafka at $KAFKA_BROKER_ADDRESS..."
    timeout 60 bash -c 'until echo > /dev/tcp/${KAFKA_BROKER_ADDRESS%%:*}/${KAFKA_BROKER_ADDRESS##*:} 2>/dev/null; do sleep 2; done' || {
    echo "⚠️  WARNING: Kafka may not be ready, continuing anyway..."
}
fi

# Check if ML models exist (for API and classification worker)
if [ "$WORKER_TYPE" = "api" ] || [ "$WORKER_TYPE" = "classification" ]; then
    echo "🤖 Checking ML models..."
    MODEL_PATH="${MODEL_PATH:-/app/machine_learning/transactions_classification/models/embedding_classification_model.pkl}"
    
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
fi

echo "✅ Pre-flight checks completed!"
echo "🌐 Starting $WORKER_TYPE..."
echo ""

# Execute the command passed to the entrypoint
exec "$@"