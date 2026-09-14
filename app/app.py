import streamlit as st
import sys
import os

# --------------------------------------------------
# Add project root to Python path
# --------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.insert(0, PROJECT_ROOT)


# --------------------------------------------------
# Import prediction functions
# --------------------------------------------------

from src.prediction import (
    load_model,
    predict_loan_risk,
    explain_prediction
)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AI Loan Default Prediction",
    page_icon="💳",
    layout="centered"
)

if "workflow_step" not in st.session_state:
    st.session_state.workflow_step = "prediction"
if "loan_result" not in st.session_state:
    st.session_state.loan_result = None
if "loan_explanation" not in st.session_state:
    st.session_state.loan_explanation = None
if "approved_currency" not in st.session_state:
    st.session_state.approved_currency = "USD"


# --------------------------------------------------
# Load trained model
# --------------------------------------------------

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "models",
    "best_model.pkl"
)

model = load_model(MODEL_PATH)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("💳 AI Loan Default Prediction")

st.write(
    """
    This system uses machine learning to estimate the
    probability of loan default based on applicant and
    loan information.
    """
)

st.divider()


# --------------------------------------------------
# Applicant Information
# --------------------------------------------------

st.subheader("👤 Applicant Information")

currency_code = st.selectbox(
    "Currency",
    options=[
        "USD",
        "EUR",
        "GBP",
        "INR",
        "LKR"
    ]
)

age = st.number_input(
    "Age",
    min_value=18,
    max_value=100,
    value=28,
    step=1
)

income = st.number_input(
    f"Annual Income ({currency_code})",
    min_value=0.0,
    value=50000.0,
    step=1000.0
)

employment_years = st.number_input(
    "Employment Years",
    min_value=0.0,
    max_value=60.0,
    value=4.0,
    step=1.0
)

home_ownership = st.selectbox(
    "Home Ownership",
    options=[
        "RENT",
        "OWN",
        "MORTGAGE",
        "OTHER"
    ]
)


# --------------------------------------------------
# Loan Information
# --------------------------------------------------

st.subheader("🏦 Loan Information")

loan_amount = st.number_input(
    f"Loan Amount ({currency_code})",
    min_value=0.0,
    value=10000.0,
    step=500.0
)

loan_purpose = st.selectbox(
    "Loan Purpose",
    options=[
        "PERSONAL",
        "EDUCATION",
        "MEDICAL",
        "VENTURE",
        "HOMEIMPROVEMENT",
        "DEBTCONSOLIDATION"
    ]
)

credit_history_years = st.number_input(
    "Credit History Years",
    min_value=0.0,
    max_value=50.0,
    value=6.0,
    step=1.0
)


# --------------------------------------------------
# Prediction button
# --------------------------------------------------

st.divider()

predict_button = st.button(
    "🔍 Predict Loan Risk",
    use_container_width=True
)


# --------------------------------------------------
# Make prediction
# --------------------------------------------------

if predict_button:

    # Basic validation
    if income <= 0:

        st.error(
            "Please enter a valid annual income."
        )

    elif loan_amount <= 0:

        st.error(
            "Please enter a valid loan amount."
        )

    else:

        result = predict_loan_risk(
            model=model,
            age=age,
            income=income,
            employment_years=employment_years,
            home_ownership=home_ownership,
            loan_amount=loan_amount,
            loan_purpose=loan_purpose,
            credit_history_years=credit_history_years
        )

        prediction = result["prediction"]
        probability = result["default_probability"]
        risk_level = result["risk_level"]

        explanation = explain_prediction(
            model=model,
            age=age,
            income=income,
            employment_years=employment_years,
            home_ownership=home_ownership,
            loan_amount=loan_amount,
            loan_purpose=loan_purpose,
            credit_history_years=credit_history_years
        )

        st.session_state.loan_result = result
        st.session_state.loan_explanation = explanation
        st.session_state.approved_currency = currency_code

        if prediction != "Default":
            st.session_state.workflow_step = "documents"
        else:
            st.session_state.workflow_step = "prediction"


        # --------------------------------------------------
        # Display results
        # --------------------------------------------------

        st.subheader("📊 Prediction Result")

        if prediction == "Default":

            st.error(
                "⚠️ Prediction: Higher Default Risk"
            )

        else:

            st.success(
                "✅ Prediction: Lower Default Risk"
            )


        # Probability

        st.metric(
            label="Default Probability",
            value=f"{probability:.2%}"
        )

        st.metric(
            label="Recommended Maximum Loan Amount",
            value=f"{currency_code} {result['recommended_max_loan_amount']:,.2f}"
        )

        st.caption(
            "Screening estimate based on income, employment stability, and model risk. "
            "It is not a final lending limit. Amounts use the selected currency code."
        )


        # Risk level

        if risk_level == "Low Risk":

            st.success(
                f"Risk Level: {risk_level}"
            )

        elif risk_level == "Medium Risk":

            st.warning(
                f"Risk Level: {risk_level}"
            )

        else:

            st.error(
                f"Risk Level: {risk_level}"
            )


        # Progress bar

        st.write("Default Probability")

        st.progress(
            float(probability)
        )


        # --------------------------------------------------
        # Decision explanation and applicant guidance
        # --------------------------------------------------

        st.subheader("🧭 Decision Explanation")

        if explanation["reason_codes"]:
            st.write("**Main factors identified:**")
            for reason in explanation["reason_codes"]:
                st.write(f"- {reason.capitalize()}")
        else:
            st.write("No specific risk warning was identified from the guidance rules.")

        st.write("**Possible next steps:**")
        for recommendation in explanation["recommendations"]:
            st.write(f"- {recommendation}")

        st.caption(
            "These are guidance points, not a guarantee of approval. "
            "A qualified loan officer should review declined or borderline applications."
        )

        with st.expander("View model explanation"):
            st.dataframe(
                explanation["feature_explanations"],
                hide_index=True,
                use_container_width=True
            )


        # --------------------------------------------------
        # Applicant summary
        # --------------------------------------------------

        st.subheader("📋 Applicant Summary")

        col1, col2 = st.columns(2)

        with col1:

            st.write(f"**Age:** {age}")
            st.write(f"**Annual Income:** {currency_code} {income:,.2f}")
            st.write(
                f"**Employment Years:** "
                f"{employment_years}"
            )
            st.write(
                f"**Home Ownership:** "
                f"{home_ownership}"
            )

        with col2:

            st.write(
                f"**Loan Amount:** "
                f"{currency_code} {loan_amount:,.2f}"
            )

            st.write(
                f"**Loan Purpose:** "
                f"{loan_purpose}"
            )

            st.write(
                f"**Credit History:** "
                f"{credit_history_years} years"
            )


        # --------------------------------------------------
        # Disclaimer
        # --------------------------------------------------

        st.divider()

        st.caption(
            """
            ⚠️ This prediction is for educational and
            risk-assessment purposes only. It should not
            be used as the sole basis for making lending
            or financial decisions.
            """
        )


# --------------------------------------------------
# Loan approval and document workflow
# --------------------------------------------------

if st.session_state.loan_result is not None:
    st.divider()
    st.subheader("🛡️ Banker Workflow")

    if st.session_state.workflow_step == "prediction":
        st.info("Review the prediction and approve the loan to continue to document verification.")
        if st.button("✅ Approve Loan and Continue", use_container_width=True):
            st.session_state.workflow_step = "documents"
            st.rerun()

    elif st.session_state.workflow_step == "documents":
        st.success("Loan approved. Upload all required documents for verification.")
        st.write("Required documents")

        identity_document = st.file_uploader(
            "Identity document",
            type=["pdf", "png", "jpg", "jpeg"],
            key="identity_document"
        )
        income_document = st.file_uploader(
            "Income or employment proof",
            type=["pdf", "png", "jpg", "jpeg"],
            key="income_document"
        )
        bank_statement = st.file_uploader(
            "Bank statement",
            type=["pdf", "png", "jpg", "jpeg"],
            key="bank_statement"
        )

        documents = {
            "Identity document": identity_document,
            "Income or employment proof": income_document,
            "Bank statement": bank_statement
        }
        missing_documents = [
            name for name, document in documents.items()
            if document is None
        ]

        if missing_documents:
            st.warning(
                "Missing documents: " + ", ".join(missing_documents)
            )
        else:
            invalid_documents = [
                name for name, document in documents.items()
                if document.size <= 0
            ]

            if invalid_documents:
                st.error(
                    "These documents are empty: " + ", ".join(invalid_documents)
                )
            else:
                st.success("All required documents are uploaded and non-empty.")
                st.caption(
                    "This is a completeness check only. A qualified banker must "
                    "verify authenticity and whether the documents match the application."
                )
                if st.button("📤 Submit Documents", use_container_width=True):
                    st.session_state.workflow_step = "completed"
                    st.rerun()

    else:
        st.success("🎉 All steps completed.")
        st.write("Loan approval and document completeness checks are finished.")
        st.caption(
            "Final disbursement remains subject to the bank's approval, compliance, "
            "and document-authentication procedures."
        )