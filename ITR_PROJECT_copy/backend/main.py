import joblib
import numpy as np
import pandas as pd
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
import torch
import torch.nn as nn

# Import data schemas from backend/schemas.py
from backend.schemas import PredictionOutput, TransactionInput


# --- Step 1: Define Autoencoder Network Structure (Must match training) ---
class Autoencoder(nn.Module):

  def __init__(self, input_dim):
    super(Autoencoder, self).__init__()
    self.encoder = nn.Sequential(
        nn.Linear(input_dim, 8), nn.ReLU(), nn.Linear(8, 4), nn.ReLU()
    )
    self.decoder = nn.Sequential(
        nn.Linear(4, 8), nn.ReLU(), nn.Linear(8, input_dim)
    )

  def forward(self, x):
    return self.decoder(self.encoder(x))


# Global variables to hold loaded models and transformers
preprocessor = None
xgb_model = None
iso_forest = None
autoencoder = None
ae_threshold = None


# --- Step 2: Load Model Artifacts at Server Startup ---
def load_artifacts():
  global preprocessor, xgb_model, iso_forest, autoencoder, ae_threshold
  try:
    # Our preprocess.py saved a single ColumnTransformer as scaler.pkl
    preprocessor = joblib.load("models/scaler.pkl")
    xgb_model = joblib.load("models/xgboost.pkl")
    iso_forest = joblib.load("models/iso_forest.pkl")
    ae_threshold = joblib.load("models/ae_threshold.pkl")

    # Load PyTorch Autoencoder
    input_dim = 10  # Total columns after preprocessing
    autoencoder = Autoencoder(input_dim)
    autoencoder.load_state_dict(torch.load("models/autoencoder.pth", weights_only=True))
    autoencoder.eval()

    print("All 3 ML Models & Preprocessing artifacts loaded successfully!")
  except Exception as e:
    print(f"Error loading model artifacts: {str(e)}")


@asynccontextmanager
async def lifespan(app):
  load_artifacts()
  yield


# Initialize FastAPI App
app = FastAPI(
    title="Hybrid Credit Fraud Detection API",
    description="Combines XGBoost, Isolation Forest, and PyTorch Autoencoder",
    version="2.0",
    lifespan=lifespan,
)

@app.get("/health")
def health_check():
    return {"status": "ok"}


# --- Step 3: Core Prediction API Endpoint ---
@app.post("/predict", response_model=PredictionOutput)
def predict_fraud(data: TransactionInput):
  if not all([preprocessor, xgb_model, iso_forest, autoencoder]):
    raise HTTPException(status_code=500, detail="Models are not loaded.")

  # A. Convert user input into DataFrame
  raw_data = pd.DataFrame([data.model_dump()])

  # B. Preprocess Input Features using the single ColumnTransformer
  processed_vector = preprocessor.transform(raw_data)

  # C. Score Model 1: XGBoost (Supervised Probability)
  xgb_prob = float(xgb_model.predict_proba(processed_vector)[0][1])

  # D. Score Model 2: Isolation Forest (Unsupervised Anomaly)
  iso_pred = iso_forest.predict(processed_vector)[0]
  iso_anomaly = bool(iso_pred == -1)  # -1 indicates an anomaly

  # E. Score Model 3: PyTorch Autoencoder (Reconstruction Loss)
  tensor_vector = torch.tensor(processed_vector, dtype=torch.float32)
  with torch.no_grad():
    reconstructed = autoencoder(tensor_vector)
    # Calculate Mean Squared Error (MSE) loss
    ae_mse = float(torch.mean((tensor_vector - reconstructed) ** 2).item())

  ae_anomaly = bool(ae_mse > ae_threshold)

  # F. Calculate Weighted Consensus Risk Score
  iso_score = 1.0 if iso_anomaly else 0.0
  ae_score = 1.0 if ae_anomaly else 0.0

  # Ensemble Weights: 50% XGBoost, 25% Isolation Forest, 25% Autoencoder
  risk_score = float((0.50 * xgb_prob) + (0.25 * iso_score) + (0.25 * ae_score))

  # Final Verdict Threshold
  final_decision = "FRAUD" if risk_score >= 0.50 else "GENUINE"

  # G. Return Clean Response
  return {
      "final_decision": final_decision,
      "risk_score": round(risk_score, 4),
      "xgb_fraud_prob": round(xgb_prob, 4),
      "iso_forest_anomaly": iso_anomaly,
      "autoencoder_anomaly": ae_anomaly,
      "autoencoder_mse": round(ae_mse, 4),
  }