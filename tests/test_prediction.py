import pytest

from src.prediction import (
    recommend_max_loan_amount,
    validate_loan_input,
)


def valid_input():
    return {
        "age": 28,
        "income": 50_000,
        "employment_years": 4,
        "home_ownership": "RENT",
        "loan_amount": 10_000,
        "loan_purpose": "EDUCATION",
        "credit_history_years": 6,
    }


def test_valid_loan_input_is_accepted():
    validate_loan_input(**valid_input())


def test_invalid_loan_input_reports_all_errors():
    values = valid_input()
    values.update(
        age=16,
        income=-1,
        home_ownership="UNKNOWN",
        loan_purpose="UNKNOWN",
    )

    with pytest.raises(ValueError, match="age.*income.*home_ownership.*loan_purpose"):
        validate_loan_input(**values)


def test_high_risk_and_short_employment_reduce_loan_limit():
    assert recommend_max_loan_amount(50_000, 4, "Low Risk") == 15_000
    assert recommend_max_loan_amount(50_000, 1, "Medium Risk") == 7_500
    assert recommend_max_loan_amount(50_000, 4, "High Risk") == 5_000
