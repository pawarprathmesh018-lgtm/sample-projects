import os
import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.ensemble import IsolationForest
from xgboost import XGBClassifier


# --- Define PyTorch Autoencoder Architecture ---
class SimpleAutoencoder(nn.Module):

  def __init__(self, input_dim):
    super(SimpleAutoencoder, self).__init__()
    # Encoder
    self.encoder = nn.Sequential(
        nn.Linear(input_dim, 8), nn.ReLU(), nn.Linear(8, 4), nn.ReLU()
    )
    # Decoder
    self.decoder = nn.Sequential(
        nn.Linear(4, 8), nn.ReLU(), nn.Linear(8, input_dim)
    )

  def forward(self, x):
    encoded = self.encoder(x)
    decoded = self.decoder(encoded)
    return decoded


# 1. Load preprocessed feature matrix and target labels
X = pd.read_csv("data/X_processed.csv")
y = pd.read_csv("data/y_processed.csv").values.ravel()

input_dim = X.shape[1]
print(f"Loaded feature matrix X with shape {X.shape}.")

# 2. Train XGBoost
print("\n[1/3] Training XGBoost Classifier...")
xgb_model = XGBClassifier(
    n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42
)
xgb_model.fit(X, y)

# 3. Train Isolation Forest
print("[2/3] Training Isolation Forest...")
iso_forest = IsolationForest(
    n_estimators=100, contamination=0.3, random_state=42
)
iso_forest.fit(X)

# 4. Train Autoencoder (Unsupervised Neural Network)
print("[3/3] Training PyTorch Autoencoder...")
X_tensor = torch.tensor(X.values, dtype=torch.float32)

autoencoder = SimpleAutoencoder(input_dim=X.shape[1])
criterion = nn.MSELoss()
optimizer = optim.Adam(autoencoder.parameters(), lr=0.01)

# Train on normal transactions (where y == 0) for better reconstruction learning
X_normal_tensor = torch.tensor(X[y == 0].values, dtype=torch.float32)

epochs = 100
for epoch in range(epochs):
  optimizer.zero_grad()
  outputs = autoencoder(X_normal_tensor)
  loss = criterion(outputs, X_normal_tensor)
  loss.backward()
  optimizer.step()

# Calculate reconstruction threshold on training data (95th percentile)
autoencoder.eval()
with torch.no_grad():
  reconstructions = autoencoder(X_tensor)
  mse_losses = torch.mean((X_tensor - reconstructions) ** 2, dim=1).numpy()
  ae_threshold = float(np.percentile(mse_losses, 85))

print(
    f"✅ Autoencoder trained successfully! Anomaly Threshold MSE:"
    f" {ae_threshold:.4f}"
)

# 5. Save all artifacts
os.makedirs("models", exist_ok=True)
joblib.dump(xgb_model, "models/xgboost.pkl")
joblib.dump(iso_forest, "models/iso_forest.pkl")
torch.save(autoencoder.state_dict(), "models/autoencoder.pth")
joblib.dump(ae_threshold, "models/ae_threshold.pkl")

print("\nSaved artifacts:")
print(" - 'models/xgboost.pkl'")
print(" - 'models/iso_forest.pkl'")
print(" - 'models/autoencoder.pth'")
print(" - 'models/ae_threshold.pkl'")