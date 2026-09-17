# Explainable AI Loan Default Prediction

An end-to-end machine-learning project for estimating loan default risk. It includes data cleaning, feature engineering, model training, SHAP explainability, input validation, risk-adjusted loan guidance, and a Streamlit dashboard.

## 🚀 Features

- **Explainable AI (XAI)**: Uses SHAP values to explain *why* a specific prediction was made, providing transparency for loan officers.
- **Enterprise-grade API**: A FastAPI backend featuring API key authentication, request validation, and database logging.
- **Interactive Dashboard**: A Streamlit application for users to input applicant details and view real-time risk assessments.
- **Data Security**: Implements a simulated encryption service to protect Personal Identifiable Information (PII).
- **External Integration Simulation**: Mocks enterprise external API calls (e.g., Credit Bureau) with retry logic and error handling.
- **Comprehensive ML Pipeline**: Scripts for preprocessing, feature engineering, model training, and evaluation.

## 📁 Project Structure

```text
AI-loan-default-prediction/
├── api/
│   └── main.py                    # FastAPI server & endpoints
├── app/
│   └── app.py                     # Streamlit dashboard
├── database/
│   └── schema.sql                 # SQL schema for the database
├── src/
│   ├── preprocessing.py           # Dataset cleaning
│   ├── feature_engineering.py     # Model dataset creation
│   ├── prediction.py              # Validation and prediction service
│   ├── credit_bureau_api.py       # Simulated credit bureau integration
│   ├── encryption.py              # PII encryption service
│   ├── fairness.py                # Model fairness evaluation
│   └── database.py                # Database setup and models
├── notebooks/                     # Jupyter notebooks for analysis and model development
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_exploratory_data_analysis.ipynb
│   ├── 04_feature_engineering.ipynb
│   ├── 05_model_training.ipynb
│   ├── 06_model_comparison.ipynb
│   └── 07_model_explainability.ipynb
├── data/                          # Raw and processed datasets
├── models/                        # Trained model artifacts (.pkl)
├── tests/                         # Automated tests (pytest)
│   └── test_prediction.py
├── .env                           # Environment variables
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

## 🛠️ Technologies Used

- **Machine Learning**: Scikit-Learn, XGBoost, SHAP, Pandas, NumPy
- **Backend/API**: FastAPI, Pydantic, SQLAlchemy, Uvicorn
- **Frontend/Dashboard**: Streamlit
- **Security**: Cryptography (Fernet)
- **Testing**: Pytest

## ⚙️ Setup and Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```powershell
   cd AI-loan-default-prediction
   ```

2. **Create and activate a virtual environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # On Windows
   # source .venv/bin/activate   # On Linux/Mac
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Ensure you have a `.env` file in the root directory with the necessary keys (like `API_KEY`, `ENCRYPTION_KEY`, etc.).

## 🏃‍♂️ Running the Pipeline

The scripts use project-root paths and can be run from any directory:

1. **Preprocess Data**:
   ```powershell
   python src\preprocessing.py
   ```
2. **Feature Engineering**:
   ```powershell
   python src\feature_engineering.py
   ```
3. **Train Models**:
   Open and run `notebooks/05_model_training.ipynb`, then create or refresh `models/best_model.pkl` from the model comparison notebook.

## 🌐 Running the Applications

### Start the API Server (FastAPI)
```powershell
# From the root directory
uvicorn api.main:app --reload
```
- Access the API documentation at: `http://localhost:8000/docs`

### Start the Dashboard (Streamlit)
```powershell
streamlit run app\app.py
```
The dashboard provides a risk prediction, default probability, screening estimate for a maximum loan amount, SHAP feature contributions, reason codes, and applicant guidance.

## 🧪 Testing

Run the automated test suite using pytest:
```powershell
pytest -q
```

## 📊 Model Evaluation

The model comparison workflow evaluates accuracy, precision, recall, F1 score, and ROC AUC. The explainability notebook also includes permutation importance and transformed feature importance.

## ⚠️ Responsible Use and Limitations

This is an educational and portfolio prototype, not a production lending decision system. The recommended loan amount is only a screening estimate and is not an approval limit. A qualified reviewer must make final decisions.

Before real banking use, the following strict requirements must be met:
- **Legal & Fairness Compliance**: You would need to mathematically prove to financial regulators (like the CFPB in the US) that your model doesn't accidentally discriminate against people based on age, gender, or race.
- **Live External APIs**: You would need to replace the mocked credit score pulls with real, secure integrations to Equifax, Experian, or TransUnion.
- **Data Encryption (PII)**: Real banking systems require deep encryption for data at rest (like encrypting National IDs and Phone Numbers in the database, not just passwords).
- **Robust MLOps & Security**: Add validated data governance, strict audit logs, model versioning, drift monitoring, human review, and regulatory approval. Do not use protected characteristics or proxy variables without an approved compliance process.
