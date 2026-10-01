# Explainable AI Loan Default Prediction

An educational full stack project for exploring loan default risk prediction. It combines a scikit-learn/XGBoost modeling workflow with a FastAPI prediction API and a Streamlit interface. SHAP explainability, fairness analysis, and data handling utilities are included in the project.

> **Notice:** This is a portfolio prototype, not a lending or credit decision system. Predictions and explanations should not be used to make real financial decisions.

## Features

- Data preprocessing and feature engineering scripts, plus notebooks for analysis, training, model comparison, and explainability.
- FastAPI backend with interactive API documentation and API key authentication.
- Streamlit dashboard for loan officer registration, login, and risk assessment.
- Model interpretation and fairness utilities.
- MySQL-backed application and prediction data access.
- A launcher that starts the API and dashboard together.

## Technology

Python, pandas, NumPy, scikit-learn, XGBoost, SHAP, FastAPI, Streamlit, SQLAlchemy, MySQL Connector, Plotly, and pytest.

## Repository layout

```text
AI-loan-default-prediction/
├── .streamlit/
│   └── config.toml                    # Streamlit configuration
├── api/
│   └── main.py                        # FastAPI application and endpoints
├── app/
│   └── app.py                         # Streamlit dashboard
├── assets/
│   └── report_figures/                # Project diagrams and analysis figures
├── data/
│   ├── row/
│   │   └── credit_risk_dataset.csv     # Raw credit risk dataset
│   ├── processed/
│   │   ├── cleaned_data.csv            # Cleaned dataset
│   │   ├── featured_data.csv           # Feature-engineered dataset
│   │   └── model_data.csv              # Model-ready dataset
│   └── mlops.db                        # Local SQLite database file
├── database/
│   └── schema.sql                      # Database schema
├── Docker/
│   ├── Dockerfile                      # Container image definition
│   └── docker-compose.yml              # Compose service configuration
├── models/
│   ├── best_model.pkl                  # Model loaded by the API
│   ├── logistic_regression.pkl
│   ├── random_forest.pkl
│   └── xgboost.pkl
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_exploratory_data_analysis.ipynb
│   ├── 04_feature_engineering.ipynb
│   ├── 05_model_training.ipynb
│   ├── 06_model_comparison.ipynb
│   └── 07_model_explainability.ipynb
├── src/
│   ├── credit_bureau_api.py            # Mock credit bureau integration
│   ├── database.py                     # Database connection and ORM models
│   ├── encryption.py                   # Encryption utilities
│   ├── fairness.py                     # Fairness analysis utilities
│   ├── feature_engineering.py          # Feature preparation
│   ├── prediction.py                   # Model loading and prediction logic
│   └── preprocessing.py                # Data cleaning and preprocessing
├── tests/
│   └── test_prediction.py              # Prediction tests
├── .env                                # Local environment variables (not committed)
├── .gitignore                          # Git ignore rules
├── README.md                           # Project documentation
├── requirements.txt                    # Python dependencies
├── run.bat                             # Windows launcher
└── run.py                              # Cross-platform combined launcher
```

## Requirements

- Python 3.9 or newer (the Docker image uses Python 3.11).
- MySQL server and a database configured for the application.
- A trained model artifact at `models/best_model.pkl`. Model files are excluded from Git, so obtain or generate the artifact before starting the API.

## Setup

Clone the repository and enter its directory:

```bash
git clone https://github.com/HimashMadushanka/Ai-loan-default-prediction.git
cd AI-loan-default-prediction
```

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

```bash
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root and set values appropriate for your local MySQL installation:

```env
API_KEY=replace-with-a-secret-key
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=replace-with-your-database-password
DB_NAME=loan_system
```

Create the `loan_system` database before running the application. Never commit `.env` or use development credentials in a deployed environment. The API has a development API key fallback; configure your own `API_KEY` before use.

## Run the application

The combined launcher starts the API at `127.0.0.1:8000` and Streamlit at port `8501`:

```bash
python run.py
```

On Windows, you can also run:

```bat
run.bat
```

Use `Ctrl+C` in the launcher terminal to stop the services. The launcher opens the dashboard in a browser when it is ready.

To start services separately, use two terminals with the virtual environment activated:

```bash
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

```bash
python -m streamlit run app/app.py --server.port 8501
```

The Streamlit app connects to the API at `http://127.0.0.1:8000`.

## API endpoints and authentication

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`

Protected API requests require the `X-API-Key` header, set to the value of `API_KEY` in `.env`.

## Data preparation and model training

The preprocessing and feature engineering scripts are available here:

```bash
python src/preprocessing.py
python src/feature_engineering.py
```

The notebooks contain the exploratory analysis and model training workflow. Training a model artifact is required if `models/best_model.pkl` is not already available. The API loads that file during startup.

## Docker

The Docker files are in `Docker/`. From the repository root, build and start the Compose service with:

```bash
docker compose -f Docker/docker-compose.yml up --build
```

The Compose configuration expects a MySQL server reachable from the container and defines development database/API settings. Review and replace those values before using it outside a local environment. The model artifact must also be available in the build context.

## Tests

Run the test suite from the project root:

```bash
pytest tests/ -v
```

## Limitations

This project demonstrates software and machine learning techniques; it does not establish that the model is accurate, fair, secure, or legally compliant for real lending. Real use would require appropriate data governance, independent validation, privacy and security controls, fairness and compliance review, monitoring, and qualified human oversight.

## Author

**Himash Madushanka**
