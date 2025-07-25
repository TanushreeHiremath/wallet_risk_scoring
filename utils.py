# utils.py
import requests
import pandas as pd
import numpy as np

def fetch_compound_transactions(wallet, api_key, chain_id):
    base_url = f"https://api.covalenthq.com/v1/{chain_id}/address/{wallet}/transactions_v2/"
    params = {
        "key": api_key,
        "page-size": 10000
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if data.get("error") or not data.get("data"):
        return []
    
    txs = data["data"].get("items", [])
    compound_txs = [tx for tx in txs if "compound" in str(tx).lower()]
    return compound_txs

def extract_features(wallet, tx_data):
    feature = {
        "wallet_id": wallet,
        "supply_tx_count": 0,
        "borrow_tx_count": 0,
        "repay_tx_count": 0,
        "liquidation_count": 0,
        "total_tx": len(tx_data)
    }
    
    for tx in tx_data:
        log = str(tx).lower()
        if "borrow" in log:
            feature["borrow_tx_count"] += 1
        elif "repay" in log:
            feature["repay_tx_count"] += 1
        elif "liquidat" in log:
            feature["liquidation_count"] += 1
        elif "supply" in log or "mint" in log:
            feature["supply_tx_count"] += 1
    return feature

def compute_scores(df):
    # Normalize all columns
    df_norm = df.copy()
    for col in ["supply_tx_count", "borrow_tx_count", "repay_tx_count", "liquidation_count"]:
        if df[col].max() != df[col].min():
            df_norm[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
        else:
            df_norm[col] = 0.5  # Avoid divide-by-zero

    # Scoring logic
    score = (
        df_norm["supply_tx_count"] * 0.4 +
        df_norm["repay_tx_count"] * 0.3 -
        df_norm["borrow_tx_count"] * 0.1 -
        df_norm["liquidation_count"] * 0.2
    )
    # Scale to 0–1000
    score = (score - score.min()) / (score.max() - score.min()) * 1000
    return score.round(0)
