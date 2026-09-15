# Explainable AI Loan Default Prediction

An end-to-end machine-learning project for estimating loan default risk. It includes data cleaning, feature engineering, model training, SHAP explainability, input validation, risk-adjusted loan guidance, and a Streamlit dashboard.

## Project Structure

```text
app/app.py                         Streamlit dashboard
src/preprocessing.py               Dataset cleaning
src/feature_engineering.py         Model dataset creation
src/prediction.py                  Validation and prediction service
notebooks/                         Analysis and model development
data/                              Raw and processed datasets
models/                            Trained model artifacts
tests/test_prediction.py           Automated tests
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run the Pipeline

The scripts use project-root paths and can be run from any directory:

```powershell
python src\preprocessing.py
python src\feature_engineering.py
```

Train the models by running `notebooks/05_model_training.ipynb`, then create or refresh `models/best_model.pkl` from the model comparison notebook.

## Run the Dashboard

```powershell
streamlit run app\app.py
```

The dashboard provides a risk prediction, default probability, screening estimate for a maximum loan amount, SHAP feature contributions, reason codes, and applicant guidance.

## Test

```powershell
pytest -q
```

## Model Evaluation

The model comparison workflow evaluates accuracy, precision, recall, F1 score, and ROC AUC. The explainability notebook also includes permutation importance and transformed feature importance.

## Responsible Use and Limitations

This is an educational and portfolio prototype, not a production lending decision system. The recommended loan amount is only a screening estimate and is not an approval limit. A qualified reviewer must make final decisions.

Before real banking use, the following strict requirements must be met:
- **Legal & Fairness Compliance**: You would need to mathematically prove to financial regulators (like the CFPB in the US) that your model doesn't accidentally discriminate against people based on age, gender, or race.
- **Live External APIs**: You would need to replace the mocked credit score pulls with real, secure integrations to Equifax, Experian, or TransUnion.
- **Data Encryption (PII)**: Real banking systems require deep encryption for data at rest (like encrypting National IDs and Phone Numbers in the database, not just passwords).
- **Robust MLOps & Security**: Add validated data governance, strict audit logs, model versioning, drift monitoring, human review, and regulatory approval. Do not use protected characteristics or proxy variables without an approved compliance process.
