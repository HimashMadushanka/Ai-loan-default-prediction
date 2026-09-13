import pandas as pd
import joblib


MODEL_PATH = "../models/best_model.pkl"


def load_model(model_path=MODEL_PATH):
    """
    Load the trained machine learning model.
    """

    model = joblib.load(model_path)

    return model


def predict_loan_risk(
    model,
    age,
    income,
    employment_years,
    home_ownership,
    loan_amount,
    loan_purpose,
    credit_history_years
):
    """
    Predict loan default risk for a single applicant.
    """

    # Create input dataframe
    input_data = pd.DataFrame({
        "age": [age],
        "income": [income],
        "employment_years": [employment_years],
        "home_ownership": [home_ownership],
        "loan_amount": [loan_amount],
        "loan_purpose": [loan_purpose],
        "credit_history_years": [credit_history_years]
    })

    # Prediction
    prediction = model.predict(input_data)[0]

    # Default probability
    probability = model.predict_proba(
        input_data
    )[0][1]

    # Convert prediction
    if prediction == 1:
        result = "Default"
    else:
        result = "Non-Default"

    # Risk level
    if probability < 0.30:
        risk_level = "Low Risk"

    elif probability < 0.60:
        risk_level = "Medium Risk"

    else:
        risk_level = "High Risk"

    return {
        "prediction": result,
        "default_probability": probability,
        "risk_level": risk_level
    }


if __name__ == "__main__":

    # Load model
    model = load_model()

    # Example applicant
    result = predict_loan_risk(
        model=model,
        age=28,
        income=50000,
        employment_years=4,
        home_ownership="RENT",
        loan_amount=10000,
        loan_purpose="EDUCATION",
        credit_history_years=6
    )

    print("\nLoan Risk Prediction")
    print("--------------------")

    print(
        "Prediction:",
        result["prediction"]
    )

    print(
        "Default Probability:",
        f"{result['default_probability']:.2%}"
    )

    print(
        "Risk Level:",
        result["risk_level"]
    )