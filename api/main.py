#!/usr/bin/env python3
"""
FastAPI endpoint to accept deep research requests via one-click email links.
"""
import os
import hmac
import hashlib
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
# Database imports for local SQLite
from database import SessionLocal, engine, Base
from models import ResearchRequest

# Load configuration from environment
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("Missing required env var: JWT_SECRET")

# Create database tables
Base.metadata.create_all(bind=engine)
app = FastAPI()

def verify_token(uid: str, area: str, token: str) -> bool:
    """Validate HMAC token to prevent unauthorized requests"""
    msg = f"{uid}:{area}".encode()
    expected = hmac.new(JWT_SECRET.encode(), msg, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, token)

@app.get("/research", response_class=HTMLResponse)
async def request_research(
    q: str = Query(..., alias="q"),
    uid: str = Query(..., alias="uid"),
    tk: str = Query(..., alias="tk")
):
    """Create a research request record and enqueue for processing"""
    # Verify HMAC token
    if not verify_token(uid, q, tk):
        raise HTTPException(status_code=403, detail="Invalid or expired link")

    # Insert a new research request into local SQLite
    req_id = str(uuid.uuid4())
    now = datetime.utcnow()
    db = SessionLocal()
    new_req = ResearchRequest(
        id=req_id,
        area_of_interest=q,
        requested_by=uid,
        status="pending",
        created_at=now,
        updated_at=now,
    )
    try:
        db.add(new_req)
        db.commit()
        print(f'Queued request {req_id} for area "{q}" by user "{uid}"')
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

    # Respond with confirmation
    return HTMLResponse(
        f"""
<html>
  <body>
    <h3>✅ Your deep research request for “{q}” is queued.</h3>
    <p>Request ID: {req_id}</p>
  </body>
</html>
""", status_code=200)
