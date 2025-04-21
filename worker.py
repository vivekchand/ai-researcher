#!/usr/bin/env python3
"""
Background worker to process research requests from Supabase,
perform deep research via OpenAI, and send results via Resend API.
"""

import os
import sys
import time
from datetime import datetime
import requests
import openai
from database import SessionLocal, engine, Base
from models import ResearchRequest

"""
Background worker to process research requests from local SQLite DB,
perform deep research via OpenAI, and send results via Resend API.
"""
# Database setup
Base.metadata.create_all(bind=engine)
# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL")

if not all([OPENAI_API_KEY, RESEND_API_KEY, RESEND_FROM_EMAIL]):
    print(
        "Error: Missing one or more environment variables: \
        OPENAI_API_KEY, RESEND_API_KEY, RESEND_FROM_EMAIL",
        file=sys.stderr,
    )
    sys.exit(1)

openai.api_key = OPENAI_API_KEY

def deep_research(area: str) -> str:
    """Run a deep research query via OpenAI and return the formatted report."""
    prompt = (
        f"Deep research on \"{area}\":\n\n"
        "1) Executive summary\n"
        "2) Key insights\n"
        "3) Further reading\n"
    )
    resp = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a skilled research assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1500,
    )
    return resp.choices[0].message.content.strip()

def send_email(to_email: str, subject: str, html_content: str):
    """Send email via Resend API."""
    url = "https://api.resend.com/emails"
    payload = {
        "from": RESEND_FROM_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html_content,
    }
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

def process_pending():
    """Fetch pending requests, perform research, update DB, and notify user."""
    # Open a database session
    db = SessionLocal()
    # Fetch pending requests
    pending_requests = db.query(ResearchRequest).filter(ResearchRequest.status == "pending").all()
    if not pending_requests:
        print(f'{datetime.utcnow().isoformat()} - No pending research requests')
        db.close()
        return
    print(f'{datetime.utcnow().isoformat()} - Found {len(pending_requests)} pending research requests:')
    for req in pending_requests:
        print(f'  - Request {req.id}: area_of_interest="{req.area_of_interest}" requested_by="{req.requested_by}" created_at={req.created_at}')
    # Mark all as in_progress
    for req in pending_requests:
        req.status = "in_progress"
        req.updated_at = datetime.utcnow()
    db.commit()
    print(f'{datetime.utcnow().isoformat()} - Marked {len(pending_requests)} requests as in_progress')

    # Process each request
    for req in pending_requests:
        area = req.area_of_interest
        user_email = req.requested_by
        print(f'{datetime.utcnow().isoformat()} - Starting deep research for request {req.id}: area "{area}"')
        try:
            report = deep_research(area)
            print(f'{datetime.utcnow().isoformat()} - Completed deep research for request {req.id}')
            # Update with result
            req.status = "complete"
            req.result = report
            req.updated_at = datetime.utcnow()
            db.commit()
            # Send the report via email
            html = report.replace("\n", "<br>")
            send_email(
                to_email=user_email,
                subject=f'Your deep research on "{area}" is ready',
                html_content=html,
            )
        except Exception as err:
            # Mark as error on failure
            req.status = "error"
            req.updated_at = datetime.utcnow()
            db.commit()
            print(f'{datetime.utcnow().isoformat()} - Failed to process request {req.id}: {err}', file=sys.stderr)
    db.close()

if __name__ == "__main__":
    while True:
        process_pending()
        time.sleep(60)