import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Create folder for saving exported EDA plots
os.makedirs("reports/figures", exist_ok=True)

# --- Step 1: Load the Custom Dataset ---
DATA_PATH = "/Users/vinit/Documents/ITR PROJECT/custom_ds.csv"
df = pd.read_csv(DATA_PATH)

print("=" * 50)
print("EXPLORATORY DATA ANALYSIS (EDA) REPORT")
print("=" * 50)

# --- Step 2: Dataset Overview & Sanity Checks ---
print("\n1. Dataset Health Summary:")
print(f"   • Total Transactions : {len(df)}")
print(f"   • Missing Values     : {df.isnull().sum().sum()}")
print(f"   • Duplicate Rows     : {df.duplicated().sum()}")

# --- Step 3: Target Class Breakdown ---
fraud_counts = df["is_fraud"].value_counts()
total_records = len(df)

genuine_count = fraud_counts.get(0, 0)
fraud_count = fraud_counts.get(1, 0)

print("\n2. Class Distribution (Target Label):")
print(
    f"   • Genuine Transactions (0) : {genuine_count} "
    f"({(genuine_count / total_records) * 100:.1f}%)"
)
print(
    f"   • Fraud Transactions   (1) : {fraud_count} "
    f"({(fraud_count / total_records) * 100:.1f}%)"
)

# --- Step 4: Key Feature Averages ---
print("\n3. Feature Comparison (Averages):")
averages = df.groupby("is_fraud")[["amount", "distance_from_home"]].mean()
print(f"   • Avg Amount ($)   -> Genuine: ${averages.loc[0, 'amount']:.2f} | Fraud: ${averages.loc[1, 'amount']:.2f}")
print(f"   • Avg Distance(km) -> Genuine: {averages.loc[0, 'distance_from_home']:.1f} km | Fraud: {averages.loc[1, 'distance_from_home']:.1f} km")

# --- Step 5: Visual Exploratory Charts ---
print("\nGenerating charts and saving to 'reports/figures/eda_summary.png'...")

sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# Plot 1: Target Class Count
sns.countplot(
    data=df, x="is_fraud", ax=axes[0, 0], palette=["#2ecc71", "#e74c3c"], hue="is_fraud", legend=False
)
axes[0, 0].set_title("1. Fraud vs. Genuine Counts")
axes[0, 0].set_xticks([0, 1])
axes[0, 0].set_xticklabels(["Genuine (0)", "Fraud (1)"])
axes[0, 0].set_ylabel("Count")

# Plot 2: Transaction Amount Comparison
sns.boxplot(
    data=df, x="is_fraud", y="amount", ax=axes[0, 1], palette=["#2ecc71", "#e74c3c"], hue="is_fraud", legend=False
)
axes[0, 1].set_title("2. Transaction Amount ($) Distribution")
axes[0, 1].set_xticks([0, 1])
axes[0, 1].set_xticklabels(["Genuine (0)", "Fraud (1)"])

# Plot 3: Distance from Home Comparison
sns.boxplot(
    data=df, x="is_fraud", y="distance_from_home", ax=axes[1, 0], palette=["#2ecc71", "#e74c3c"], hue="is_fraud", legend=False
)
axes[1, 0].set_title("3. Distance from Home (km) Distribution")
axes[1, 0].set_xticks([0, 1])
axes[1, 0].set_xticklabels(["Genuine (0)", "Fraud (1)"])

# Plot 4: Payment Channel Risk Analysis
sns.countplot(
    data=df, x="transaction_type", hue="is_fraud", ax=axes[1, 1], palette=["#2ecc71", "#e74c3c"]
)
axes[1, 1].set_title("4. Fraud across Payment Channels")
axes[1, 1].set_xlabel("Payment Channel")
axes[1, 1].legend(["Genuine", "Fraud"])

plt.tight_layout()
plt.savefig("reports/figures/eda_summary.png", dpi=300)

print("Visualization export successful!")
print("=" * 50)