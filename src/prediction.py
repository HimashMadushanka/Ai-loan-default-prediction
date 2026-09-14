import pandas as pd
import joblib
import shap
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "best_model.pkl"

VALID_HOME_OWNERSHIP = {
    "RENT",
    "OWN",
    "MORTGAGE",
    "OTHER"
}

VALID_LOAN_PURPOSES = {
    "PERSONAL",
    "EDUCATION",
    "MEDICAL",
    "VENTURE",
    "HOMEIMPROVEMENT",
    "DEBTCONSOLIDATION"
}


def validate_loan_input(
    age,
    income,
    employment_years,
    home_ownership,
    loan_amount,
    loan_purpose,
    credit_history_years
):
    """Reject missing, invalid, or implausible applicant values."""

    values = {
        "age": age,
        "income": income,
        "employment_years": employment_years,
        "home_ownership": home_ownership,
        "loan_amount": loan_amount,
        "loan_purpose": loan_purpose,
        "credit_history_years": credit_history_years
    }
    errors = []

    for name, value in values.items():
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"{name} is required")

    numeric_ranges = {
        "age": (18, 100),
        "income": (1, 10_000_000),
        "employment_years": (0, 80),
        "loan_amount": (1, 10_000_000),
        "credit_history_years": (0, 80)
    }

    for name, (minimum, maximum) in numeric_ranges.items():
        value = values[name]
        if value is None:
            continue
        try:
            numeric_value = float(value)
            if not pd.isna(numeric_value) and not minimum <= numeric_value <= maximum:
                errors.append(f"{name} must be between {minimum} and {maximum}")
            elif pd.isna(numeric_value):
                errors.append(f"{name} must be a valid number")
        except (TypeError, ValueError):
            errors.append(f"{name} must be a valid number")

    if home_ownership not in VALID_HOME_OWNERSHIP:
        errors.append(
            f"home_ownership must be one of: {sorted(VALID_HOME_OWNERSHIP)}"
        )

    if loan_purpose not in VALID_LOAN_PURPOSES:
        errors.append(
            f"loan_purpose must be one of: {sorted(VALID_LOAN_PURPOSES)}"
        )

    if not errors and float(loan_amount) / float(income) > 100:
        errors.append("loan_amount cannot be more than 100 times annual income")

    if errors:
        raise ValueError("Invalid loan input: " + "; ".join(errors))


def load_model(model_path=MODEL_PATH):
    """
    Load the trained machine learning model.
    """

    model = joblib.load(model_path)

    return model


def _shap_values_for_pipeline(model, input_data):
    """Return SHAP values aggregated from encoded columns to source features."""

    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]
    transformed_data = preprocessor.transform(input_data)
    feature_names = preprocessor.get_feature_names_out()
    explainer = shap.TreeExplainer(classifier)
    shap_values = explainer.shap_values(transformed_data)

    if isinstance(shap_values, list):
        shap_values = shap_values[-1]
    if hasattr(shap_values, "values"):
        shap_values = shap_values.values
    if len(shap_values.shape) == 3:
        shap_values = shap_values[:, :, -1]

    source_features = input_data.columns.tolist()
    aggregated_values = pd.DataFrame(0.0, index=input_data.index, columns=source_features)
    for index, encoded_name in enumerate(feature_names):
        source_name = encoded_name.split("__", 1)[-1]
        source_name = next(
            feature for feature in source_features
            if source_name == feature or source_name.startswith(feature + "_")
        )
        aggregated_values[source_name] += shap_values[:, index]

    return aggregated_values, explainer.expected_value


def explain_prediction(
    model,
    age,
    income,
    employment_years,
    home_ownership,
    loan_amount,
    loan_purpose,
    credit_history_years,
    top_n=5
):
    """Explain one prediction with SHAP values and plain-language reason codes."""

    validate_loan_input(
        age=age,
        income=income,
        employment_years=employment_years,
        home_ownership=home_ownership,
        loan_amount=loan_amount,
        loan_purpose=loan_purpose,
        credit_history_years=credit_history_years
    )

    input_data = pd.DataFrame({
        "age": [age],
        "income": [income],
        "employment_years": [employment_years],
        "home_ownership": [home_ownership],
        "loan_amount": [loan_amount],
        "loan_purpose": [loan_purpose],
        "credit_history_years": [credit_history_years]
    })
    shap_values, expected_value = _shap_values_for_pipeline(model, input_data)
    explanation = pd.DataFrame({
        "feature": shap_values.columns,
        "value": input_data.iloc[0].values,
        "shap_value": shap_values.iloc[0].values
    })
    explanation["impact"] = explanation["shap_value"].apply(
        lambda value: "increases default risk" if value > 0 else "decreases default risk"
    )
    explanation = explanation.sort_values(
        "shap_value", key=lambda values: values.abs(), ascending=False
    ).head(top_n)

    reason_codes = []
    if float(loan_amount) / float(income) >= 0.5:
        reason_codes.append("high loan amount relative to income")
    if float(income) < 30_000:
        reason_codes.append("low income")
    if float(employment_years) < 2:
        reason_codes.append("short employment history")
    if float(credit_history_years) < 3:
        reason_codes.append("short credit history")
    if home_ownership == "RENT":
        reason_codes.append("rents home")

    return {
        "base_value": float(expected_value[-1] if hasattr(expected_value, "__len__") else expected_value),
        "default_probability": float(model.predict_proba(input_data)[0, 1]),
        "feature_explanations": explanation.reset_index(drop=True),
        "reason_codes": reason_codes,
        "recommendations": build_recommendations(
            income=income,
            employment_years=employment_years,
            loan_amount=loan_amount,
            credit_history_years=credit_history_years,
            reason_codes=reason_codes
        )
    }


def global_shap_importance(model, reference_data):
    """Return mean absolute SHAP importance for each original input feature."""

    shap_values, _ = _shap_values_for_pipeline(model, reference_data)
    return (
        shap_values.abs()
        .mean()
        .sort_values(ascending=False)
        .rename("mean_absolute_shap")
        .reset_index()
        .rename(columns={"index": "feature"})
    )


def build_recommendations(
    income,
    employment_years,
    loan_amount,
    credit_history_years,
    reason_codes
):
    """Create applicant guidance from validated values and reason codes."""

    reason_to_recommendation = {
        "high loan amount relative to income":
            "Consider applying for a smaller loan amount.",
        "low income":
            "Submit verified additional income information if available.",
        "short employment history":
            "A longer employment history may improve future applications.",
        "short credit history":
            "Building a longer repayment history may improve future applications.",
        "rents home":
            "Provide complete, verified financial information for manual review."
    }
    recommendations = [
        reason_to_recommendation[reason]
        for reason in reason_codes
        if reason in reason_to_recommendation
    ]

    if float(loan_amount) / float(income) >= 0.5 and not recommendations:
        recommendations.append("Consider applying for a smaller loan amount.")
    if float(employment_years) < 2 and "short employment history" not in reason_codes:
        recommendations.append("Provide verified employment information for review.")
    if float(credit_history_years) < 3 and "short credit history" not in reason_codes:
        recommendations.append("Provide complete repayment history if available.")

    if not recommendations:
        recommendations.append(
            "Maintain accurate financial information and review the result with a loan officer."
        )

    return list(dict.fromkeys(recommendations))


def recommend_max_loan_amount(income, employment_years, risk_level):
    """Estimate a conservative maximum loan amount for screening purposes."""

    annual_income = float(income)
    years_employed = float(employment_years)

    income_multiplier = {
        "Low Risk": 0.30,
        "Medium Risk": 0.20,
        "High Risk": 0.10
    }[risk_level]

    employment_factor = 0.75 if years_employed < 2 else 1.0
    recommended_amount = annual_income * income_multiplier * employment_factor

    return round(max(recommended_amount, 0), 2)


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

    validate_loan_input(
        age=age,
        income=income,
        employment_years=employment_years,
        home_ownership=home_ownership,
        loan_amount=loan_amount,
        loan_purpose=loan_purpose,
        credit_history_years=credit_history_years
    )

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
        "risk_level": risk_level,
        "recommended_max_loan_amount": recommend_max_loan_amount(
            income=income,
            employment_years=employment_years,
            risk_level=risk_level
        )
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