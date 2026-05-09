
# main.py
# FastAPI backend for the Planet Ganges Leadership Assessment

import base64
import os
import logging
import smtplib

from contextlib import asynccontextmanager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, field_validator
from fastapi.exceptions import RequestValidationError as RVE

from scorer import compute_scores
from email_template import build_email_html
from pdf_report import build_pdf

# ──────────────────────────────────────────────────────────────────────────────
# Environment Setup
# ──────────────────────────────────────────────────────────────────────────────

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_PASS = os.environ.get("GMAIL_PASS", "")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "*")

if not GMAIL_USER or not GMAIL_PASS:
    logger.warning("Gmail credentials not set — emails will fail")

# ──────────────────────────────────────────────────────────────────────────────
# FastAPI App
# ──────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Leadership Assessment API starting up")
    yield
    logger.info("Leadership Assessment API shutting down")


app = FastAPI(
    title="Leadership Assessment API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────────────────────────────────────
# Request Schema
# ──────────────────────────────────────────────────────────────────────────────

class AssessmentPayload(BaseModel):
    name: str
    email: EmailStr

    q1: int
    q2: int
    q3: int
    q4: int
    q5: int
    q6: int
    q7: int
    q8: int
    q9: int

    @field_validator(
        "q1", "q2", "q3",
        "q4", "q5", "q6",
        "q7", "q8", "q9",
        mode="before"
    )
    @classmethod
    def validate_answer(cls, v):
        v = int(v)

        if not 1 <= v <= 5:
            raise ValueError("Each answer must be between 1 and 5")

        return v

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v):
        v = str(v).strip()

        if not v:
            raise ValueError("Name cannot be empty")

        return v

# ──────────────────────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/submit")
async def submit_assessment(payload: AssessmentPayload):

    # 1. Collect raw answers
    answers = {
        f"q{i}": getattr(payload, f"q{i}")
        for i in range(1, 10)
    }

    # 2. Compute scores
    scores = compute_scores(answers)

    # 3. Generate PDF
    try:
        pdf_bytes = build_pdf(payload.name, scores)

    except Exception as exc:
        logger.error(f"PDF generation failed: {exc}", exc_info=True)

        raise HTTPException(
            status_code=500,
            detail="Failed to generate PDF report."
        )

    # 4. Generate HTML email
    html_body = build_email_html(payload.name, scores)

    # 5. Send Email using Gmail SMTP
    try:
        msg = MIMEMultipart()

        msg["Subject"] = (
            f"Your Leadership Assessment Report — {payload.name}"
        )

        msg["From"] = f"Planet Ganges Consulting <{GMAIL_USER}>"
        msg["To"] = payload.email

        # HTML email body
        msg.attach(MIMEText(html_body, "html"))

        # PDF attachment
        pdf_attachment = MIMEApplication(
            pdf_bytes,
            _subtype="pdf"
        )

        pdf_attachment.add_header(
            "Content-Disposition",
            "attachment",
            filename="leadership-report.pdf"
        )

        msg.attach(pdf_attachment)

        # SMTP connection
        server = smtplib.SMTP("smtp.gmail.com", 587)

        server.starttls()

        server.login(GMAIL_USER, GMAIL_PASS)

        server.send_message(msg)

        server.quit()

        email_sent = True
        email_error = None

    except Exception as exc:
        logger.error(
            f"Email send failed for {payload.email}: {exc}",
            exc_info=True
        )

        email_sent = False
        email_error = str(exc)

    # 6. Return frontend response
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "email_sent": email_sent,
            "email_error": email_error,
            "name": payload.name,
            "email": payload.email,
            "scores": scores,
        }
    )

# ──────────────────────────────────────────────────────────────────────────────
# Validation Error Handler
# ──────────────────────────────────────────────────────────────────────────────

@app.exception_handler(RVE)
async def validation_exception_handler(
    request: Request,
    exc: RVE
):
    errors = exc.errors()

    messages = [
        f"{e['loc'][-1]}: {e['msg']}"
        for e in errors
    ]

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "detail": messages
        }
    )

