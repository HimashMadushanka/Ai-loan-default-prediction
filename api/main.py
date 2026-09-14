from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import sys
import os
import logging

# ──────────────────────────────────────────────────────────
# Setup
# ──────────────────────────────────────────────────────────

load_dotenv()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from src.prediction import load_model, predict_loan_risk, explain_prediction
from src.database import init_db, get_db, PredictionLog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# ──────────────────────────────────────────────────────────
# FastAPI App
# ──────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Loan Prediction API",
    description="Enterprise API for loan default prediction with authentication and monitoring.",
    version=os.getenv("MODEL_VERSION", "1.0.0")
)

# Load the model once at startup
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "best_model.pkl")
model = load_model(MODEL_PATH)

# ──────────────────────────────────────────────────────────
# API Key Authentication
# ──────────────────────────────────────────────────────────

API_KEY = os.getenv("API_KEY", "loan-predict-dev-key-2026")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """Validate the API key from request header."""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Provide 'X-API-Key' header."
        )
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key."
        )
    return api_key


# ──────────────────────────────────────────────────────────
# Request / Response Models
# ──────────────────────────────────────────────────────────

class LoanApplication(BaseModel):
    age: int = Field(..., ge=18, le=100, description="Applicant age (18-100)")
    income: float = Field(..., gt=0, description="Annual income (positive)")
    employment_years: float = Field(..., ge=0, le=60, description="Years of employment")
    home_ownership: str = Field(..., description="RENT, OWN, MORTGAGE, or OTHER")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    loan_purpose: str = Field(..., description="Loan purpose category")
    credit_history_years: float = Field(..., ge=0, le=50, description="Credit history length")


class HealthResponse(BaseModel):
    status: str
    api_version: str
    model_loaded: bool


class ModelInfoResponse(BaseModel):
    model_version: str
    model_path: str
    model_type: str
    features: list


# ──────────────────────────────────────────────────────────
# Global Error Handler
# ──────────────────────────────────────────────────────────

from fastapi.responses import JSONResponse
from fastapi import Request


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions and return clean JSON (no stack trace leaks)."""
    logger.error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )


@app.exception_handler(ValueError)
async def validation_exception_handler(request: Request, exc: ValueError):
    """Handle validation errors from the prediction module."""
    logger.warning(f"Validation error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )


# ──────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint for monitoring — no authentication required."""
    return HealthResponse(
        status="healthy",
        api_version=os.getenv("MODEL_VERSION", "1.0.0"),
        model_loaded=model is not None
    )


@app.get("/model/info", response_model=ModelInfoResponse)
def model_info(api_key: str = Depends(verify_api_key)):
    """Return model metadata — requires authentication."""
    model_type = "unknown"
    if hasattr(model, "named_steps"):
        classifier = model.named_steps.get("classifier")
        if classifier:
            model_type = type(classifier).__name__

    return ModelInfoResponse(
        model_version=os.getenv("MODEL_VERSION", "1.0.0"),
        model_path=MODEL_PATH,
        model_type=model_type,
        features=["age", "income", "employment_years", "home_ownership",
                   "loan_amount", "loan_purpose", "credit_history_years"]
    )


@app.post("/predict")
def predict_loan(
    application: LoanApplication,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Predict loan risk and log the prediction to the database.
    Requires valid API key in X-API-Key header.
    """
    logger.info(
        f"Prediction request: age={application.age}, "
        f"income={application.income}, loan={application.loan_amount}"
    )

    result = predict_loan_risk(
        model=model,
        age=application.age,
        income=application.income,
        employment_years=application.employment_years,
        home_ownership=application.home_ownership,
        loan_amount=application.loan_amount,
        loan_purpose=application.loan_purpose,
        credit_history_years=application.credit_history_years
    )

    # Get explanation
    explanation = explain_prediction(
        model=model,
        age=application.age,
        income=application.income,
        employment_years=application.employment_years,
        home_ownership=application.home_ownership,
        loan_amount=application.loan_amount,
        loan_purpose=application.loan_purpose,
        credit_history_years=application.credit_history_years
    )

    import pandas as pd
    # Convert types for JSON serialization
    result["default_probability"] = float(result["default_probability"])
    result["recommended_max_loan_amount"] = float(result["recommended_max_loan_amount"])
    if isinstance(explanation.get("feature_explanations"), pd.DataFrame):
        explanation["feature_explanations"] = explanation["feature_explanations"].to_dict(orient="records")

    # Log to MLOps database
    db_log = PredictionLog(
        age=application.age,
        income=application.income,
        employment_years=application.employment_years,
        home_ownership=application.home_ownership,
        loan_amount=application.loan_amount,
        loan_purpose=application.loan_purpose,
        credit_history_years=application.credit_history_years,
        prediction=result["prediction"],
        default_probability=result["default_probability"],
        risk_level=result["risk_level"],
        recommended_max_loan_amount=result["recommended_max_loan_amount"]
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    logger.info(
        f"Prediction complete: id={db_log.id}, "
        f"result={result['prediction']}, risk={result['risk_level']}"
    )

    return {
        "result": result,
        "explanation": explanation,
        "log_id": db_log.id
    }
