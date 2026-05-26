import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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
    "^IXIC": "Nasdaq", "INR=X": "USD/INR", "DX-Y.NYB": "Dollar Index", 
    "BZ=F": "Brent Crude", "GC=F": "Gold",
    "^CNXIT": "Nifty IT", "^CNXAUTO": "Nifty Auto", "^CNXPHARMA": "Nifty Pharma",
    "^CNXFMCG": "Nifty FMCG", "^CNXMETAL": "Nifty Metal", "^CNXENERGY": "Nifty Energy"
}

# --- UNIVERSAL SSL FIX ---
@st.cache_resource
def setup_ssl():
    os.environ["CURL_CA_BUNDLE"] = certifi.where()
    return True
setup_ssl()

# --- HEADER ---
st.title("📊 Nivesh Bodh: Pre-Market Engine")
st.markdown("Scanner by **Nivesh Gyanam | Deepesh Soni**")
st.caption("⚡ **Menu:** 1. Macro Snap | 2. Sector Heatmap | 3. Stock Tracker | 4. Deep Dive | 5. News")

if st.sidebar.button("🔄 Force Live Refresh"):
    st.cache_data.clear()
    st.rerun()

st.divider()

# --- 1. MACRO MARKET SNAPSHOT ---
st.subheader("🌐 1. Macro Market Snapshot")

@st.cache_data(ttl=300) # 5-min cache for stability
def get_macro_data():
    macros = ["^NSEI", "^NSEBANK", "^INDIAVIX", "^IXIC", "INR=X", "DX-Y.NYB", "BZ=F", "GC=F"]
    data = []
    # Fetch in individual blocks to prevent batch-request timeouts
    for ticker in macros:
        try:
            df = yf.download(ticker, period="2d", progress=False)
            if not df.empty and len(df) >= 2:
                last = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                pct = ((last - prev) / prev) * 100
                data.append({"Asset": MACROS_AND_SECTORS[ticker], "Price": f"{last:,.2f}", "Change": f"{pct:+.2f}%", "Raw": pct})
        except: continue
    return data

macro_list = get_macro_data()
if macro_list:
    df_macro = pd.DataFrame(macro_list)
    # Highlight colors
    def color_val(row):
        color = "#48bb78" if row["Raw"] >= 0 else "#f56565"
        return [f"color: {color}; font-weight:bold" for _ in row]
    
    st.dataframe(df_macro.drop(columns=["Raw"]).style.apply(color_val, axis=1), 
                 use_container_width=True, hide_index=True)
else:
    st.warning("⚠️ Macro feeds temporarily busy. Click 'Force Live Refresh'.")

st.divider()

# --- 2. SECTOR HEATMAP ---
st.subheader("🔥 2. Sector Index Heatmap")
@st.cache_data(ttl=300)
def get_sectors():
    # Placeholder for Sector logic...
    return pd.DataFrame({"Sector": ["IT", "Auto", "Pharma"], "Change (%)": [0.5, -0.2, 1.2]})

sector_df = get_sectors()
st.dataframe(sector_df, use_container_width=True, hide_index=True)

st.divider()

# --- 3. MARKET NEWS ---
st.subheader("📰 3. Market Focus News")
st.info("💡 **Macro Context:** Market currently focused on FII flow volatility and Q4 earnings sentiment.")
st.markdown("""
* **Global:** Nasdaq showing resilience; tech sector leads.
* **Domestic:** F&O volume restrictions impacting intraday retail participation.
""")
