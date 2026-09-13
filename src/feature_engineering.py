import pandas as pd


FEATURES = [
    "age",
    "income",
    "employment_years",
    "home_ownership",
    "loan_amount",
    "loan_purpose",
    "credit_history_years"
]

TARGET = "default"


def create_model_data(df):
    """
    Select features and target for machine learning.
    """

    model_df = df[FEATURES + [TARGET]].copy()

    return model_df


def save_model_data(
    model_df,
    file_path="../data/processed/model_data.csv"
):
    """
    Save model-ready dataset.
    """

    model_df.to_csv(
        file_path,
        index=False
    )

    print(f"Model data saved to: {file_path}")


if __name__ == "__main__":

    cleaned_data_path = (
        "../data/processed/cleaned_data.csv"
    )

    df = pd.read_csv(cleaned_data_path)

    model_df = create_model_data(df)

    print("Model data shape:", model_df.shape)

    print("\nFeatures:")
    print(FEATURES)

    print("\nTarget:")
    print(TARGET)

    save_model_data(model_df)