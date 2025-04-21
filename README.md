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

## License
This project is released under the MIT License.