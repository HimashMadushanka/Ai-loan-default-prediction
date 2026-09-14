from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import sys
import os

# Add project root to Python path so we can import from src
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from src.prediction import load_model, predict_loan_risk, explain_prediction
from src.database import init_db, get_db, PredictionLog

# Initialize database
init_db()

# Initialize FastAPI app
app = FastAPI(
    title="AI Loan Prediction API",
    description="Enterprise API for loan default prediction.",
    version="1.0.0"
)

# Load the model once at startup
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "best_model.pkl")
model = load_model(MODEL_PATH)

class LoanApplication(BaseModel):
    age: int
    income: float
    employment_years: float
    home_ownership: str
    loan_amount: float
    loan_purpose: str
    credit_history_years: float

@app.post("/predict")
def predict_loan(application: LoanApplication, db: Session = Depends(get_db)):
    """
    Predict loan risk and log the prediction to the database.
    """
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

    return {
        "result": result,
        "explanation": explanation,
        "log_id": db_log.id
    }
