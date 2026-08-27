from pydantic import BaseModel, Field


class TransactionInput(BaseModel):
  """Accepts features from the custom dataset."""
  amount: float = Field(..., examples=[120.50])
  distance_from_home: float = Field(..., examples=[5.2])
  merchant_category: str = Field(..., examples=["grocery"])
  transaction_type: str = Field(..., examples=["online_checkout"])
  card_type: str = Field(..., examples=["visa"])


class PredictionOutput(BaseModel):
  """Structured output returned after model evaluation."""
  final_decision: str  # "GENUINE" or "FRAUD"
  risk_score: float  # Combined weighted score (0.0 to 1.0)
  xgb_fraud_prob: float  # XGBoost score
  iso_forest_anomaly: bool  # Isolation Forest flag
  autoencoder_anomaly: bool  # Autoencoder flag
  autoencoder_mse: float  # Autoencoder loss
