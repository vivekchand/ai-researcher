#!/usr/bin/env python3
"""
AI Agent Researcher

Generates a list of untapped AI agent ideas with potential cost/time savings
and identifies target customers willing to pay for such solutions.
"""
import os
import sys
import json
import argparse
import time
import requests
from datetime import datetime
import openai

def generate_ideas(api_key, num_ideas=10, model="gpt-4"):
    """
    Call OpenAI to generate a list of promising AI agent research areas.
    Returns a list of dicts with fields: area, description, potential_savings,
    target_customer, reason_untapped.
    """
    openai.api_key = api_key
    prompt = (
        f"You are an AI research assistant. Please provide a JSON array of {num_ideas}"
        " objects, each describing a promising untapped area to build an AI agent."
        " Each object should have the following fields:\n"
        "- \"area\": the name of the area\n"
        "- \"description\": a brief description of the agent and its function\n"
        "- \"potential_savings\": estimation of cost or time savings\n"
        "- \"target_customer\": who would pay for this service\n"
        "- \"reason_untapped\": why this area is currently under-served\n\n"
        "Return only the JSON array."
    )
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful AI research assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1500,
    )
    content = response.choices[0].message.content.strip()
    try:
        ideas = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"Failed to parse JSON from OpenAI response:\n{content}")
    return ideas

def main():
    parser = argparse.ArgumentParser(description="AI Agent Idea Researcher")
    parser.add_argument("--num", "-n", type=int, default=10,
                        help="Number of ideas to generate")
    parser.add_argument("--model", "-m", default="gpt-4",
                        help="OpenAI model to use (e.g., gpt-4, gpt-3.5-turbo)")
    parser.add_argument("--apikey", "-k", default=None,
                        help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("-r", "--recipient", default="vivekchand19@gmail.com",
                        help="Email address to send the ideas to")
    parser.add_argument("-i", "--interval", type=float, default=6,
                        help="Interval in hours between emails")
    parser.add_argument("--resend-api-key", "-a", default=None,
                        help="Resend API key (or set RESEND_API_KEY env var)")
    parser.add_argument("--from-email", "-f", default=None,
                        help="Email address to send from (or set RESEND_FROM_EMAIL env var)")
    args = parser.parse_args()

    api_key = args.apikey or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key must be provided via --apikey or OPENAI_API_KEY env var.", file=sys.stderr)
        sys.exit(1)

    # Email configuration
    recipient = args.recipient
    interval_hours = args.interval
    resend_api_key = args.resend_api_key or os.getenv("RESEND_API_KEY")
    from_email = args.from_email or os.getenv("RESEND_FROM_EMAIL")

    if not all([resend_api_key, from_email]):
        print(
            "Error: Resend API key and sender email required. Provide --resend-api-key and --from-email, "
            "or set RESEND_API_KEY and RESEND_FROM_EMAIL env vars", file=sys.stderr)
        sys.exit(1)

    def format_body(ideas):
        lines = []
        for item in ideas:
            lines.append(f"Area: {item.get('area')}")
            lines.append(f"Description: {item.get('description')}")
            lines.append(f"Potential Savings: {item.get('potential_savings')}")
            lines.append(f"Target Customer: {item.get('target_customer')}")
            lines.append(f"Reason Untapped: {item.get('reason_untapped')}")
            lines.append("")
        return "\n".join(lines)

    def send_email(subject, body):
        """Send email via Resend API"""
        url = "https://api.resend.com/emails"
        payload = {
            "from": from_email,
            "to": [recipient],
            "subject": subject,
            "html": f"<pre>{body}</pre>",
        }
        headers = {
            "Authorization": f"Bearer {resend_api_key}",
            "Content-Type": "application/json",
        }
        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()

    # Periodically generate ideas and send email
    while True:
        try:
            ideas = generate_ideas(api_key, num_ideas=args.num, model=args.model)
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
            subject = f"AI Agent Ideas - {timestamp}"
            body = format_body(ideas)
            send_email(subject, body)
            print(f"Email sent to {recipient} at {timestamp}")
        except Exception as e:
            print(f"Error during generation or email send: {e}", file=sys.stderr)
        time.sleep(interval_hours * 3600)

if __name__ == "__main__":
    main()