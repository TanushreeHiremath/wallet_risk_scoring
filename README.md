# 🔍 Compound Wallet Risk Analyzer

A Python + Streamlit-based application that analyzes Ethereum wallet interactions with the Compound Protocol (V2/V3) and assigns each wallet a **risk score (0–1000)** based on its transaction history.


## 📦 Features

- Supports **Compound V2** (V3 extensible)
- Fetches wallet transaction history using the **Covalent API**
- Computes **risk score (0–1000)** per wallet
- Classifies wallets as **Low, Medium, High, or Extreme** risk
- Offers a clean UI built with **Streamlit**
- Supports CSV export of risk analysis

##  Feature Normalization
Before applying weights, each feature is min-max normalized:

       normalized_value= (x-min(x))/(max(z)-min(x))
​
This scales each feature to a value between 0 and 1, making them comparable regardless of their original range.

## 🧠 Risk Scoring Logic

### 💡 Features Extracted:
For each wallet:
- `supply_tx_count`: Number of supply (collateral) transactions
- `repay_tx_count`: Number of repay transactions
- `borrow_tx_count`: Number of borrow transactions
- `liquidation_count`: Number of liquidation events
- `total_tx`: Total Compound-related transactions

### 📊 Scoring Formula:
Each feature is normalized using min-max scaling. The raw risk score is computed as:

score = (
    0.4 * supply_tx_norm +         # Positive impact: more supply = safer
    0.3 * repay_tx_norm -          # Positive impact: more repayments = safer
    0.1 * borrow_tx_norm -         # Negative impact: more borrowing = riskier
    0.2 * liquidation_count_norm   # Negative impact: more liquidations = riskier
)

| Component              | Weight | Meaning                                                            |
| ---------------------- | ------ | ------------------------------------------------------------------ |
| `0.4 * supply_tx_norm` | 0.4    | **Most important positive** factor. Supplying assets reduces risk. |
| `0.3 * repay_tx_norm`  | 0.3    | Repaying borrowed assets is good behavior → lowers risk.           |
| `0.1 * borrow_tx_norm` | 0.1    | Borrowing increases risk slightly → low negative weight.           |
| `0.2 * liquidation...` | 0.2    | Liquidation is a red flag → medium negative weight.                |



Then scaled to the range 0 to 1000:

scaled_score = (score - min_score) / (max_score - min_score) * 1000

## Risk Classification

Score Range	Risk Level	Color
800 - 1000	Low	      🟢 Green
600 - 799	Medium	      🟡 Gold
400 - 599	High	      🟠 Orange
0 - 399	Extreme      🔴 Red

## Streamlit UI
Launch the app locally:

streamlit run streamlit_app.py

UI Features:

- Paste wallet addresses (one per line)
- Choose Compound protocol version
- Optional checkboxes:
     - Include historical transactions
     - Weight recent activity higher (feature-ready)

View:
  - Risk scores
  - Borrow ratio (%)
  - Risk classification badges
  - Etherscan & Debank links

Export results to CSV

### 🛠️ Installation
1.Clone the repo
2.Install dependencies:
  - pip install -r requirements.txt
3.Add your Covalent API Key in the script or as an environment variable.
4.Run the main script (batch):
  - python main.py
Or launch UI:
  - streamlit run streamlit_app.py
    
## 📁 Project Structure

├── main.py                # CLI version to score wallets in bulk
├── streamlit_app.py       # Web app interface
├── utils.py               # Logic for fetching, processing, scoring
├── Wallet id.xlsx         # Input wallet list
├── wallet_risk_scores.csv # Output CSV
├── requirements.txt       # Dependencies
├── README.md              # Project documentation

## 📚 Justification for Features

Supply & Repay: Positive behaviors that reduce protocol risk
Borrow: Adds risk if uncollateralized or frequent
Liquidation: Major risk indicator for default or insolvency
Borrow Ratio: Indicates risky usage pattern
