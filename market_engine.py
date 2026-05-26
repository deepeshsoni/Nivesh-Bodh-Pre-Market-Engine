import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px  # <-- NEW: Required for the Animated Treemap
import random
from datetime import datetime
import certifi
import os
import sys
import tempfile

# --- UI PAGE CONFIGURATION ---
st.set_page_config(page_title="Nivesh Bodh", page_icon="📊", layout="wide")

# --- GLOBAL DATA DICTIONARIES ---
WATCHLIST = {
    "RELIANCE.NS": {"sector": "Energy", "cap": "Large"}, "TCS.NS": {"sector": "IT", "cap": "Large"},
    "HDFCBANK.NS": {"sector": "Banking", "cap": "Large"}, "BHARTIARTL.NS": {"sector": "Telecom", "cap": "Large"},
    "ASIANPAINT.NS": {"sector": "Paints", "cap": "Large"}, "COCHINSHIP.NS": {"sector": "Defence", "cap": "Mid"},
    "POLYCAB.NS": {"sector": "Cables", "cap": "Mid"}, "MAXHEALTH.NS": {"sector": "Healthcare", "cap": "Mid"},
    "VOLTAS.NS": {"sector": "Durables", "cap": "Mid"}, "RITES.NS": {"sector": "Railways", "cap": "Small"},
    "CDSL.NS": {"sector": "Finance", "cap": "Small"}, "SJVN.NS": {"sector": "Power", "cap": "Small"},
    "EASEMYTRIP.NS": {"sector": "Travel", "cap": "Small"}
}

MACROS_AND_SECTORS = {
    "^NSEI": "Nifty 50", "^NSEBANK": "Bank Nifty", "^INDIAVIX": "India VIX", 
    "INR=X": "USD/INR", "DX-Y.NYB": "Dollar Index", "BZ=F": "Brent Crude", "GC=F": "Gold (Global)",
    "^CNXIT": "Nifty IT", "^CNXAUTO": "Nifty Auto", "^CNXPHARMA": "Nifty Pharma",
    "^CNXFMCG": "Nifty FMCG", "^CNXMETAL": "Nifty Metal", "^CNXENERGY": "Nifty Energy"
}

# --- NATIVE TECHNICAL INDICATORS ---
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- UNIVERSAL SSL CERTIFICATE FIX ---
@st.cache_resource
def setup_ssl_certificates():
    cache_dir = os.path.join(tempfile.gettempdir(), "nivesh_bodh")
    os.makedirs(cache_dir, exist_ok=True)
    combined_path = os.path.join(cache_dir, "ca_bundle.pem")
    with open(certifi.where(), "rb") as src: bundle = src.read()
    with open(combined_path, "wb") as dst: dst.write(bundle)
    os.environ["CURL_CA_BUNDLE"] = combined_path
    os.environ["SSL_CERT_FILE"] = combined_path
    os.environ["REQUESTS_CA_BUNDLE"] = combined_path
    return combined_path

setup_ssl_certificates()

# --- HEADER ---
st.title("📊 Nivesh Bodh: Pre-Market Engine")
st.markdown("A top-down algorithmic market scanner by **Nivesh Gyanam**")

if st.sidebar.button("🔄 Force Live Refresh"):
    st.cache_data.clear()
    st.rerun()

st.divider()

# --- 1. PREMIUM MACRO MARKET SNAPSHOT (LIGHTWEIGHT TICKER VIEW) ---
st.subheader("1. Macro Market Snapshot")

@st.cache_data(ttl=60)
def get_macro_data_batch():
    macros = ["^NSEI", "^NSEBANK", "^INDIAVIX", "INR=X", "DX-Y.NYB", "BZ=F", "GC=F"]
    data = []
    try:
        group = yf.download(macros, period="5d", group_by='ticker', progress=False)
        for ticker in macros:
            if ticker in group.columns.levels[0]:
                df = group[ticker].dropna()
                if not df.empty and len(df) >= 2:
                    last_close = df['Close'].iloc[-1]
                    prev_close = df['Close'].iloc[-2]
                    change_pct = ((last_close - prev_close) / prev_close) * 100
                    unit = "$" if "F" in ticker else "₹" if "INR" in ticker or "NSE" in ticker else ""
                    
                    data.append({
                        "Asset Index": MACROS_AND_SECTORS[ticker], 
                        "Current Value": f"{unit}{last_close:,.2f}", 
                        "RawChange": change_pct, 
                        "Daily Change": f"{change_pct:+.2f}%"
                    })
    except:
        pass
    return data

macro_list = get_macro_data_batch()

if macro_list:
    macro_matrix_df = pd.DataFrame(macro_list)
    
    def style_macro_ticker(row):
        colors = []
        text_color = "#48bb78" if row["RawChange"] >= 0 else "#f56565"
        colors.append("") 
        colors.append(f"color: {text_color}; font-weight: bold;") 
        colors.append("") 
        colors.append(f"color: {text_color}; font-weight: bold;") 
        return colors

    cleaned_render_df = macro_matrix_df.drop(columns=["RawChange"])
    styled_ticker_df = macro_matrix_df.style.apply(style_macro_ticker, axis=1)

    st.dataframe(
        styled_ticker_df, 
        use_container_width=True, 
        hide_index=True,
        column_order=["Asset Index", "Current Value", "Daily Change"]
    )
else:
    st.info("🔄 Refreshing Macro Market feeds...")

st.divider()

# --- 2. [UPGRADED] INTERACTIVE SECTOR HEATMAP (ANIMATED TREEMAP) ---
st.subheader("2. Sector Index Heatmap")

@st.cache_data(ttl
