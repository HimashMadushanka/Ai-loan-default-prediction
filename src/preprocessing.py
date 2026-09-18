import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "row" / "credit_risk_dataset.csv"
CLEANED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "cleaned_data.csv"


def load_data(file_path=RAW_DATA_PATH):
    """
    Load the raw loan dataset.
    """
    df = pd.read_csv(file_path)
    return df


def rename_columns(df):
    """
    Rename original dataset columns to simpler names.
    """

    column_mapping = {
        "person_age": "age",
        "person_income": "income",
        "person_home_ownership": "home_ownership",
        "person_emp_length": "employment_years",
        "loan_intent": "loan_purpose",
        "loan_grade": "loan_grade",
        "loan_amnt": "loan_amount",
        "loan_int_rate": "interest_rate",
        "loan_status": "default",
        "loan_percent_income": "loan_income_ratio",
        "cb_person_default_on_file": "previous_default",
        "cb_person_cred_hist_length": "credit_history_years"
    }

    df = df.rename(columns=column_mapping)

    return df


def clean_data(df):
    """
    Clean the dataset.
    """

    df = df.drop_duplicates()

    numerical_columns = [
        "age",
        "income",
        "employment_years",
        "loan_amount",
        "interest_rate",
        "loan_income_ratio",
        "credit_history_years"
    ]

  
    categorical_columns = [
        "home_ownership",
        "loan_purpose",
        "loan_grade",
        "previous_default"
    ]

    for column in numerical_columns:
        if column in df.columns:
            df[column] = df[column].fillna(
                df[column].median()
            )

    for column in categorical_columns:
        if column in df.columns:
            df[column] = df[column].fillna(
                df[column].mode()[0]
            )

    return df


def save_cleaned_data(
    df,
    file_path=CLEANED_DATA_PATH
):
    """
    Save cleaned dataset.
    """

    df.to_csv(
        file_path,
        index=False
    )

    print(f"Cleaned data saved to: {file_path}")


if __name__ == "__main__":

    df = load_data()

    print("Original shape:", df.shape)

    df = rename_columns(df)

    df = clean_data(df)

    print("Cleaned shape:", df.shape)

    save_cleaned_data(df)