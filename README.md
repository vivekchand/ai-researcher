# AI Agent Researcher

This CLI tool helps you discover promising, untapped AI agent ideas that can deliver significant cost and time savings.
It uses the OpenAI API to generate a list of areas where AI-driven agents could provide high ROI and are currently under-served.

## Features
- Generates a customizable number of AI agent idea entries
- Each idea includes: area name, description, estimated savings, target customers, and reasons it's untapped
- Outputs results in JSON format for easy integration

## Requirements
- Python 3.7+
- `openai` Python package (see `requirements.txt`)

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
export OPENAI_API_KEY="your_api_key"
python ai_agent_researcher.py --num 8 --model gpt-4
```

Or provide the API key directly:
```bash
python ai_agent_researcher.py -n 5 -k your_api_key
```

The output will be a JSON array printed to stdout.

## Deep Research API Endpoint

This project includes a FastAPI endpoint to handle "Deep Research" requests via one-click email links.

1. Configure environment variables:
   - OPENAI_API_KEY: Your OpenAI API key
   - RESEND_API_KEY: Your Resend API key
   - RESEND_FROM_EMAIL: Sender email for Resend
   - JWT_SECRET: HMAC secret for request link tokens
   - DATABASE_URL: (optional) Database URL, default `sqlite:///./research.db`
   - RESEARCH_BASE_URL: Base URL for the `/research` endpoint (e.g. `http://localhost:8000/research`)

2. Deploy the API:
   - Locally: `uvicorn api.main:app --reload --port 8000`
   - Vercel: the included `.vercel.json` defines the build and route for `/research`

3. One-Click Links:
   Generate a link in your emails pointing to:
   `<RESEARCH_BASE_URL>?q=<URL-encoded-area>&uid=<user-id-or-email>&tk=<HMAC-token>`

4. Workflow:
   - User clicks the link → FastAPI records a `pending` request in Supabase → worker polls, processes, and emails the detailed report.

## Local Development & Setup

This setup uses a local SQLite database (`research.db` by default) and includes:
  - A FastAPI endpoint (`api/main.py`) to record research requests
  - A background worker (`worker.py`) to process pending requests and send emails
  - Database models and session in `database.py` and `models.py`

### Environment Variables
Create a `.env` file in the project root with:
```
OPENAI_API_KEY=your_openai_api_key
RESEND_API_KEY=your_resend_api_key
RESEND_FROM_EMAIL=your_sender_email
JWT_SECRET=your_hmac_secret
DATABASE_URL=sqlite:///./research.db  # optional, defaults to this
RESEARCH_BASE_URL=http://localhost:8000/research
```

Load the variables:
```bash
pip install -r requirements.txt
source .env
```

### Running the API
```bash
uvicorn api.main:app --reload --port 8000
```

### Running the Worker
```bash
python worker.py
```

### One‑Click Full Setup
Instead of running each component manually, you can use the `run_all.sh` helper script:
```bash
chmod +x run_all.sh
./run_all.sh
```
This will:
  1. Load your `.env` file
  2. Install Python dependencies
  3. Launch the FastAPI server (`uvicorn`) in the background
  4. Launch the background worker in the background
  5. Send an initial batch of AI Agent ideas emails (default 5)
  6. Tail the processes; press Ctrl+C to stop both server and worker

## License
This project is released under the MIT License.