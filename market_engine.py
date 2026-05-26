import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import random
from datetime import datetime
import certifi
import os
import sys
import tempfile

# --- UI PAGE CONFIGURATION ---
st.set_page_config(page_title="Nivesh Bodh", page_icon="📊", layout="wide")

# --- MOBILE COMPACT CARD STYLE INJECTION ---
st.markdown("""
<style>
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 10px;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #1e2430;
        border: 1px solid #2d3748;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-title {
        font-size: 0.8rem;
        color: #a0aec0;
        font-weight: 600;
        margin-bottom: 4px;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.1rem;
        color: #ffffff;
        font-weight: bold;
    }
    .metric-delta-pos {
        font-size: 0.8rem;
        color: #48bb78;
        margin-top: 2px;
    }
    .metric-delta-neg {
        font-size: 0.8rem;
        color: #f56565;
        margin-top: 2px;
    }
</style>
""", unsafe_with_html=True)

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
    "INR=X": "USD/INR", "DX-Y.NYB": "Dollar Index", "BZ=F": "Brent Crude", "GC=F": "Gold (Global)"
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

# --- MARKET SENTIMENT TRACKER SIDEBAR ---
st.sidebar.markdown("### 🧭 Market Sentiment Hub")
st.sidebar.info("**GIFT Nifty Premium:** Integrating Live Feeds...\n\n**FII / DII Flows:** Integrating Daily Data Ingestion...")

# --- 1. MACRO MARKET SNAPSHOT (FIXED GRID SYSTEM) ---
st.subheader("1. Macro Market Snapshot")

@st.cache_data(ttl=60)
def get_macro_data_batch():
    macros = list(MACROS_AND_SECTORS.keys())
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
                        "Name": MACROS_AND_SECTORS[ticker], 
                        "Price": f"{unit}{last_close:,.2f}", 
                        "Delta": f"{change_pct:+.2f}%",
                        "IsPositive": change_pct >= 0
                    })
    except:
        pass
    return data

macro_data = get_macro_data_batch()

if macro_data:
    # Safely construct the raw responsive boxes HTML
    cards_html = ""
    for item in macro_data:
        delta_class = "metric-delta-pos" if item["IsPositive"] else "metric-delta-neg"
        cards_html += f'<div class="metric-card"><div class="metric-title">{item["Name"]}</div><div class="metric-value">{item["Price"]}</div><div class="{delta_class}">{item["Delta"]}</div></div>'
    
    full_grid_html = f'<div class="metric-container">{cards_html}</div>'
    st.markdown(full_grid_html, unsafe_with_html=True)
else:
    st.info("🔄 Refreshing Macro Market feeds...")

st.divider()

# --- 2. CROSS-SECTOR MULTI-CAP VIEW (WITH GYANAM SCORE) ---
st.subheader("2. Cross-Sector Multi-Cap View")

def calculate_gyanam_score(latest_data):
    score = 0
    if latest_data['Close'] > latest_data.get('EMA_20', 0): score += 20
    if latest_data['Close'] > latest_data.get('EMA_50', 0): score += 20
    if latest_data.get('MACD', 0) > latest_data.get('Signal', 0): score += 25
    rsi = latest_data.get('RSI_14', 50)
    if 40 <= rsi <= 60: score += 15
    elif 30 <= rsi < 40: score += 35
    elif rsi > 70: score -= 10
    if latest_data.get('Volume', 0) > latest_data.get('Vol_MA_20', 0): score += 20
    return min(max(score, 0), 100)

@st.cache_data(ttl=60)
def get_stock_data_batch():
    tickers = list(WATCHLIST.keys())
    results = []
    try:
        group = yf.download(tickers, period="6mo", group_by='ticker', progress=False)
        for ticker in tickers:
            if ticker in group.columns.levels[0]:
                df = group[ticker].dropna()
                if not df.empty and len(df) > 50:
                    df['RSI_14'] = compute_rsi(df['Close'])
                    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
                    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
                    
                    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
                    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
                    df['MACD'] = exp1 - exp2
                    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
                    df["Vol_MA_20"] = df["Volume"].rolling(window=20).mean()
                    
                    latest = df.iloc[-1]
                    signals = []
                    if latest['RSI_14'] > 70: signals.append("⚠️ OVERBOUGHT")
                    elif latest['RSI_14'] < 30: signals.append("🟢 OVERSOLD")
                    if latest['Volume'] > (1.5 * latest['Vol_MA_20']): signals.append("🔥 VOL BREAKOUT")
                    signal_text = " + ".join(signals) if signals else "⚪ NEUTRAL"
                    
                    g_score = calculate_gyanam_score(latest)
                    results.append({
                        "Ticker": ticker.replace(".NS", ""), "Sector": WATCHLIST[ticker]["sector"],
                        "Close (₹)": round(latest['Close'], 2), 
                        "Gyanam Score": f"{int(g_score)} / 100",
                        "RSI (14)": round(latest['RSI_14'], 2) if not pd.isna(latest['RSI_14']) else 50.0,
                        "Actionable Signal": signal_text
                    })
    except:
        pass
    if results:
        return pd.DataFrame(results)
    return pd.DataFrame(columns=["Ticker", "Sector", "Close (₹)", "Gyanam Score", "RSI (14)", "Actionable Signal"])

stock_df = get_stock_data_batch()
if not stock_df.empty:
    st.dataframe(stock_df, use_container_width=True)
else:
    st.info("🔄 Running multi-cap scan...")

st.divider()

# --- 3. DAILY LEARNING ---
st.subheader("3. Nivesh Gyanam: Daily Learning")
topics = [
    {"topic": "MACD Crossovers", "lesson": "When the MACD line crosses above the Signal line, it indicates shifting bullish momentum. When paired with an RSI crossing 50, probability of a sustained rally increases."},
    {"topic": "The 50-EMA Baseline", "lesson": "The 50-Day Exponential Moving Average is the institutional baseline. Assets trading above it are in uptrends; assets below it are in downtrends. Buy the bounces, sell the breakdowns."},
    {"topic": "Volume Validation", "lesson": "A breakout is only trustworthy if the daily volume significantly exceeds the 20-day Volume MA. Low volume breakouts are often traps."}
]
day_of_year = datetime.now().timetuple().tm_yday
random.seed(day_of_year)
daily_lesson = random.choice(topics)
st.info(f"**💡 {daily_lesson['topic']}**: {daily_lesson['lesson']}")
random.seed()
