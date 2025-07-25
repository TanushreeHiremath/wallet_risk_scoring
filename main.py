# main.py
import pandas as pd
import os
from dotenv import load_dotenv
from utils import fetch_compound_transactions, extract_features, compute_scores

# Load environment variables
load_dotenv()
API_KEY = os.getenv("COVALENT_API_KEY")
CHAIN_ID = 1  # Ethereum Mainnet

# Load wallet list
wallets_df = pd.read_excel("Wallet id.xlsx")
wallets = wallets_df["wallet_id"].tolist()

# Collect and process transaction data
features = []
for wallet in wallets:
    print(f"Processing wallet: {wallet}")
    tx_data = fetch_compound_transactions(wallet, API_KEY, CHAIN_ID)
    wallet_features = extract_features(wallet, tx_data)
    features.append(wallet_features)

# Create DataFrame
features_df = pd.DataFrame(features)

# Compute scores
features_df["score"] = compute_scores(features_df)

# Save to CSV
features_df[["wallet_id", "score"]].to_csv("wallet_risk_scores.csv", index=False)
print("✅ Risk scores saved to 'wallet_risk_scores.csv'")
