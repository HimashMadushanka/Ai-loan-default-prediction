"""
Enterprise AI Fairness Module

This script demonstrates compliance with financial fairness regulations.
It computes the 'Disparate Impact' metric to mathematically prove if the
loan model illegally discriminates against applicants based on age.
"""

import pandas as pd
import joblib
import os
import logging
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "best_model.pkl"
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "model_data.csv"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("FairnessCompliance")


class FairnessEvaluator:
    def __init__(
        self,
        model_path: str | Path | None = None,
        data_path: str | Path | None = None,
    ):
        self.model_path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
        if not self.model_path.is_absolute():
            self.model_path = PROJECT_ROOT / self.model_path

        self.data_path = Path(data_path) if data_path else DEFAULT_DATA_PATH
        if not self.data_path.is_absolute():
            self.data_path = PROJECT_ROOT / self.data_path

    def check_age_bias(self, age_threshold: int = 30) -> Dict[str, Any]:
        """
        Calculates Disparate Impact for Age groups (Young <= threshold, Older > threshold).
        A Disparate Impact ratio < 0.8 typically flags potential illegal discrimination (the "Four-Fifths Rule").
        """
        logger.info(
            "Initiating mandatory fairness and bias compliance check on model predictions."
        )

        if not self.model_path.exists() or not self.data_path.exists():
            logger.error("Required model or data files missing for fairness evaluation.")
            return {"status": "error", "message": "Model or Data missing"}

        try:
            df = pd.read_csv(self.data_path)
            model = joblib.load(self.model_path)

            X = df.drop(columns=["default"])
            predictions = model.predict(X)
            df["predicted_default"] = predictions

            young_mask = df["age"] <= age_threshold
            old_mask = df["age"] > age_threshold

            young_approval_rate = float(1.0 - df.loc[young_mask, "predicted_default"].mean())
            old_approval_rate = float(1.0 - df.loc[old_mask, "predicted_default"].mean())

            disparate_impact = (
                float(young_approval_rate / old_approval_rate)
                if old_approval_rate > 0
                else 0.0
            )

            passed = bool(disparate_impact >= 0.8)

            logger.info(
                f"Compliance Check Complete. Disparate Impact: {disparate_impact:.2f}"
            )

            return {
                "status": "success",
                "young_approval_rate": round(young_approval_rate, 4),
                "old_approval_rate": round(old_approval_rate, 4),
                "disparate_impact_ratio": round(disparate_impact, 4),
                "four_fifths_rule_passed": passed,
                "message": (
                    "Model meets disparate impact threshold"
                    if passed
                    else "WARNING: Model exhibits potential age bias"
                ),
            }
        except Exception as e:
            logger.error(f"Failed to run fairness evaluation: {e}")
            return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    evaluator = FairnessEvaluator()
    result = evaluator.check_age_bias()
    print("\n--- FAIRNESS COMPLIANCE REPORT ---")
    for k, v in result.items():
        print(f"{k}: {v}")
