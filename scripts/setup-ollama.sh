#!/bin/bash

# Ollama Setup Script for ChatGroq & Llama Conversational Chatbot
# This script pulls the required Llama model and ensures Ollama is ready

set -e

OLLAMA_HOST=${OLLAMA_HOST:-http://ollama:11434}
MODEL_NAME=${OLLAMA_MODEL_NAME:-llama3.2:1b}

echo "🦙 Setting up Ollama with model: $MODEL_NAME"
echo "📡 Ollama host: $OLLAMA_HOST"

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
for i in {1..30}; do
  if curl -s "$OLLAMA_HOST/api/tags" > /dev/null; then
    echo "✅ Ollama is ready!"
    break
  fi
  echo "⏳ Attempt $i/30: Ollama not ready, waiting 10 seconds..."
  sleep 10
done

# Check if Ollama is responding
if ! curl -s "$OLLAMA_HOST/api/tags" > /dev/null; then
  echo "❌ Error: Ollama is not responding after 5 minutes"
  exit 1
fi

# Check if model already exists
echo "🔍 Checking if model $MODEL_NAME is already available..."
if curl -s "$OLLAMA_HOST/api/tags" | grep -q "\"name\":\"$MODEL_NAME\""; then
  echo "✅ Model $MODEL_NAME is already available!"
else
  echo "📥 Pulling model $MODEL_NAME..."
  
  # Pull the model
  curl -X POST "$OLLAMA_HOST/api/pull" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$MODEL_NAME\"}" &
  
  PULL_PID=$!
  
  # Monitor the pull progress
  echo "⏳ Model pull initiated (PID: $PULL_PID)"
  echo "📊 You can monitor progress in the ollama container logs:"
  echo "   docker logs -f chatbot-ollama"
  
  # Wait for the pull to complete (this might take a while)
  wait $PULL_PID
  
  # Verify the model was pulled successfully
  sleep 5
  if curl -s "$OLLAMA_HOST/api/tags" | grep -q "\"name\":\"$MODEL_NAME\""; then
    echo "✅ Model $MODEL_NAME pulled successfully!"
  else
    echo "⚠️  Model pull completed, but verification failed. Check ollama logs."
  fi
fi

# Test the model with a simple request
echo "🧪 Testing model with a simple request..."
TEST_RESPONSE=$(curl -s -X POST "$OLLAMA_HOST/api/generate" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL_NAME\",\"prompt\":\"Hello\",\"stream\":false}" \
  || echo "")

if echo "$TEST_RESPONSE" | grep -q "\"response\""; then
  echo "✅ Model test successful!"
else
  echo "⚠️  Model test failed. Response: $TEST_RESPONSE"
fi

echo "🎉 Ollama setup completed!"
echo "📋 Available models:"
curl -s "$OLLAMA_HOST/api/tags" | grep -o '"name":"[^"]*"' | sed 's/"name":"//g' | sed 's/"//g' | sort

echo ""
echo "🚀 Ready to use Ollama with the chatbot API!"
echo "   - Ollama API: $OLLAMA_HOST"
echo "   - Default model: $MODEL_NAME"
echo "   - Chatbot API: http://localhost:8000"