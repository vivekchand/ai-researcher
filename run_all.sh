#!/usr/bin/env bash
set -e

# Ensure .env is loaded
if [ -f .env ]; then
  set -o allexport
  source .env
  set +o allexport
else
  echo "Error: .env file not found" >&2
  exit 1
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Start the FastAPI server in the background
echo "Starting FastAPI server on port 8000..."
uvicorn api.main:app --reload --port 8000 > server.log 2>&1 &
API_PID=$!

# Start the background worker in the background
echo "Starting background worker..."
python worker.py > worker.log 2>&1 &
WORKER_PID=$!

# Cleanup function to stop background processes on Ctrl+C
cleanup() {
    echo "Stopping background processes..."
    kill "${API_PID}" "${WORKER_PID}"
    exit 0
}
trap cleanup INT TERM

# Run the email sender (this will run in the foreground)
echo "Sending initial batch of AI Agent ideas emails..."
python ai_agent_researcher.py \
  --num "${NUM_IDEAS:-5}" \
  --resend-api-key "$RESEND_API_KEY" \
  --from-email "$RESEND_FROM_EMAIL" \
  --research-base-url "$RESEARCH_BASE_URL" \
  --jwt-secret "$JWT_SECRET"

echo "AI Agent emails sent. Press Ctrl+C to stop."

# Tail server and worker logs until interrupted
echo "Tailing logs (server.log and worker.log)..."
tail -F server.log worker.log
