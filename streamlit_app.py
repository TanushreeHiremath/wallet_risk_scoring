import streamlit as st
import pandas as pd
import numpy as np
from utils import fetch_compound_transactions, extract_features, compute_scores

st.set_page_config(layout="wide")
st.title("🔍 Compound Wallet Risk Analyzer")
st.caption("V2/V3 Protocol Analysis")

# Sidebar / Inputs
protocol = st.selectbox("Protocol Version", ["Compound V2", "Compound V3"])
include_history = st.checkbox("Include historical transactions", value=True)
weight_recent = st.checkbox("Weight recent activity higher", value=True)

wallet_input = st.text_area("Enter Wallet Addresses (one per line)", height=150)

if st.button("Analyze Wallets"):
    wallet_list = [w.strip() for w in wallet_input.splitlines() if w.strip()]
    
    if not wallet_list:
        st.warning("Please enter at least one wallet address.")
    else:
        results = []

        for wallet in wallet_list:
            with st.spinner(f"Processing wallet: {wallet}"):
                tx_data = fetch_compound_transactions(wallet, api_key="cqt_rQqbVxGgC8dXvRhxGjVgJCHjj8rM", chain_id=1)
                features = extract_features(wallet, tx_data)
                results.append(features)

        df = pd.DataFrame(results)
        df["score"] = compute_scores(df)

        # Risk Category
        def classify_risk(score):
            if score >= 800:
                return "Low"
            elif score >= 600:
                return "Medium"
            elif score >= 400:
                return "High"
            else:
                return "Extreme"

        df["risk"] = df["score"].apply(classify_risk)
        df["borrow_ratio"] = np.where(df["borrow_tx_count"] > 0,
                                      (df["borrow_tx_count"] / df["total_tx"] * 100).round(2),
                                      0.0)

        # Risk badge function
        def risk_badge(risk):
            color = {
                "Low": "green",
                "Medium": "gold",
                "High": "orange",
                "Extreme": "red"
            }.get(risk, "gray")
            return f'<span style="background-color:{color};padding:4px 8px;border-radius:5px;color:white">{risk}</span>'

        # Display table
        st.subheader("📊 Risk Analysis Results")
        df_display = df.copy()
        df_display["WALLET"] = df_display["wallet_id"].apply(lambda x: f"[{x}](https://etherscan.io/address/{x})")
        df_display["RISK"] = df_display["risk"].apply(lambda x: risk_badge(x))
        df_display["DETAILS"] = df_display["wallet_id"].apply(lambda x: f"[View details](https://debank.com/profile/{x})")

        st.markdown(
            df_display[["WALLET", "score", "RISK", "total_tx", "borrow_ratio", "DETAILS"]]
            .rename(columns={
                "score": "SCORE",
                "total_tx": "TRANSACTIONS",
                "borrow_ratio": "BORROW RATIO"
            })
            .to_html(escape=False, index=False),
            unsafe_allow_html=True
        )

        # Export
        csv = df[["wallet_id", "score", "risk", "total_tx", "borrow_ratio"]].to_csv(index=False).encode("utf-8")
        st.download_button("📥 Export to CSV", csv, "wallet_risk_analyze.csv", "text/csv")
