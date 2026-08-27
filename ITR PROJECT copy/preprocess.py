# Preprocessing & scaler generation
import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

def load_and_preprocess_data(csv_name="custom_ds.csv"):
    """Loads dataset, preprocesses features, saves the preprocessor,
    and returns stratified train/test splits.
    """
    print("Loading dataset for preprocessing...")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, csv_name)
    df = pd.read_csv(csv_path)

    # Separate features (X) and target class (y)
    X = df.drop(columns=["is_fraud"])
    y = df["is_fraud"]

    # Define numerical and categorical columns
    numerical_cols = ["amount", "distance_from_home"]
    categorical_cols = ["merchant_category", "transaction_type", "card_type"]

    # Create ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
            ('cat', OneHotEncoder(drop='first', sparse_output=False), categorical_cols)
        ])

    print("Standardizing and encoding features...")
    X_scaled = preprocessor.fit_transform(X)

    # Ensure 'models' folder exists and export saved preprocessor artifact
    models_dir = os.path.join(BASE_DIR, "models")
    os.makedirs(models_dir, exist_ok=True)
    scaler_path = os.path.join(models_dir, "scaler.pkl")
    joblib.dump(preprocessor, scaler_path)
    print(f"Preprocessor fitted and saved to '{scaler_path}'")

    # Save X and y to data folder for train.py
    data_dir = os.path.join(BASE_DIR, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Save as CSVs without headers to maintain compatibility with some loaders, or with headers.
    # We'll use default pd.DataFrame to_csv which writes headers by default.
    pd.DataFrame(X_scaled).to_csv(os.path.join(data_dir, "X_processed.csv"), index=False)
    pd.DataFrame(y).to_csv(os.path.join(data_dir, "y_processed.csv"), index=False)
    print("Saved 'data/X_processed.csv' and 'data/y_processed.csv'")

    # Stratified split ensures exact ratio in both sets
    print("Splitting dataset into train (80%) and test (20%) sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training set shape: {X_train.shape}")
    print(f"Testing set shape : {X_test.shape}")

    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    X_train, X_test, y_train, y_test = load_and_preprocess_data()
    print("\nPreprocessing pipeline executed successfully!")