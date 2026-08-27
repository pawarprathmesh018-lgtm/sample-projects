"""
Standalone inference module for Streamlit Cloud deployment.

Loads all ML model artifacts once (cached via @st.cache_resource) and
provides a predict_fraud() function that replicates the FastAPI /predict
endpoint — no backend server required.
"""

import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st
import torch
import torch.nn as nn


# ---------------------------------------------------------------------------
# Autoencoder architecture (must match training)
# ---------------------------------------------------------------------------
class Autoencoder(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 8), nn.ReLU(), nn.Linear(8, 4), nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(4, 8), nn.ReLU(), nn.Linear(8, input_dim)
        )

    def forward(self, x):
        return self.decoder(self.encoder(x))


# ---------------------------------------------------------------------------
# Resolve the models/ directory relative to this file
# ---------------------------------------------------------------------------
_THIS_DIR = Path(__file__).resolve().parent          # frontend/
_PROJECT_DIR = _THIS_DIR.parent                       # ITR_PROJECT_copy/
_MODELS_DIR = _PROJECT_DIR / "models"


# ---------------------------------------------------------------------------
# Cached model loading — runs only once per Streamlit session
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Loading ML models …")
def _load_models():
    """Load all model artifacts from disk and return them as a dict."""
    preprocessor = joblib.load(_MODELS_DIR / "scaler.pkl")
    xgb_model = joblib.load(_MODELS_DIR / "xgboost.pkl")
    iso_forest = joblib.load(_MODELS_DIR / "iso_forest.pkl")
    ae_threshold = joblib.load(_MODELS_DIR / "ae_threshold.pkl")

    input_dim = 10  # total columns after preprocessing
    autoencoder = Autoencoder(input_dim)
    autoencoder.load_state_dict(
        torch.load(_MODELS_DIR / "autoencoder.pth", weights_only=True, map_location="cpu")
    )
    autoencoder.eval()

    return {
        "preprocessor": preprocessor,
        "xgb_model": xgb_model,
        "iso_forest": iso_forest,
        "autoencoder": autoencoder,
        "ae_threshold": ae_threshold,
    }


def models_loaded() -> bool:
    """Return True if the models have been successfully cached."""
    try:
        _load_models()
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Core prediction function
# ---------------------------------------------------------------------------
def predict_fraud(
    amount: float,
    distance_from_home: float,
    merchant_category: str,
    transaction_type: str,
    card_type: str,
) -> dict:
    """
    Score a single transaction using the three-model ensemble.

    Returns the same dict structure that the FastAPI /predict endpoint returned:
        final_decision, risk_score, xgb_fraud_prob,
        iso_forest_anomaly, autoencoder_anomaly, autoencoder_mse
    """
    models = _load_models()
    preprocessor = models["preprocessor"]
    xgb_model = models["xgb_model"]
    iso_forest = models["iso_forest"]
    autoencoder = models["autoencoder"]
    ae_threshold = models["ae_threshold"]

    # A. Build a single-row DataFrame
    raw_data = pd.DataFrame([{
        "amount": amount,
        "distance_from_home": distance_from_home,
        "merchant_category": merchant_category,
        "transaction_type": transaction_type,
        "card_type": card_type,
    }])

    # B. Preprocess
    processed_vector = preprocessor.transform(raw_data)

    # C. XGBoost (supervised probability)
    xgb_prob = float(xgb_model.predict_proba(processed_vector)[0][1])

    # D. Isolation Forest (unsupervised anomaly)
    iso_pred = iso_forest.predict(processed_vector)[0]
    iso_anomaly = bool(iso_pred == -1)

    # E. Autoencoder (reconstruction loss)
    tensor_vector = torch.tensor(processed_vector, dtype=torch.float32)
    with torch.no_grad():
        reconstructed = autoencoder(tensor_vector)
        ae_mse = float(torch.mean((tensor_vector - reconstructed) ** 2).item())
    ae_anomaly = bool(ae_mse > ae_threshold)

    # F. Weighted ensemble risk score
    iso_score = 1.0 if iso_anomaly else 0.0
    ae_score = 1.0 if ae_anomaly else 0.0
    risk_score = float((0.50 * xgb_prob) + (0.25 * iso_score) + (0.25 * ae_score))

    # G. Final verdict
    final_decision = "FRAUD" if risk_score >= 0.50 else "GENUINE"

    return {
        "final_decision": final_decision,
        "risk_score": round(risk_score, 4),
        "xgb_fraud_prob": round(xgb_prob, 4),
        "iso_forest_anomaly": iso_anomaly,
        "autoencoder_anomaly": ae_anomaly,
        "autoencoder_mse": round(ae_mse, 4),
    }
