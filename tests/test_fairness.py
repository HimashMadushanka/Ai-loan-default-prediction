import pytest
from src.fairness import FairnessEvaluator


def test_fairness_evaluator_age_bias():
    evaluator = FairnessEvaluator()
    result = evaluator.check_age_bias(age_threshold=30)

    assert result["status"] == "success"
    assert "young_approval_rate" in result
    assert "old_approval_rate" in result
    assert "disparate_impact_ratio" in result
    assert "four_fifths_rule_passed" in result
    assert isinstance(result["four_fifths_rule_passed"], bool)
    assert 0.0 <= result["disparate_impact_ratio"] <= 2.0


def test_fairness_evaluator_missing_files():
    evaluator = FairnessEvaluator(model_path="nonexistent_model.pkl", data_path="nonexistent_data.csv")
    result = evaluator.check_age_bias()
    assert result["status"] == "error"
