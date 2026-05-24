import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import random
from datetime import datetime
import certifi
import os
import subprocess
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
    "INR=X": "USD/INR", "DX-Y.NYB": "Dollar Index (DXY)", "BZ=F": "Brent Crude", "GC=F": "Gold (Global)",
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

# --- UNIVERSAL SSL CERTIFICATE FIX (Local & Cloud Support) ---
@st.cache_resource
def setup_ssl_certificates():
    cache_dir = os.path.join(tempfile.gettempdir(), "nivesh_bodh")
    os.makedirs(cache_dir, exist_ok=True)
    certifi_path = certifi.where()
    combined_path = os.path.join(cache_dir, "ca_bundle.pem")
    
    # Read base certifi certificates
    with open(certifi_path, "rb") as src: 
        bundle = src.read()
        
    # ONLY run PowerShell local extraction if executing on a Windows local machine
    if sys.platform == "win32":
        ps_script = """
        $patterns = @('Avast', 'Antivirus', 'SSL/TLS scanning', 'Web/Mail Shield')
        Get-ChildItem Cert:\\LocalMachine\\Root | Where-Object {
            $s = $_.Subject
            ($patterns | Where-Object { $s -like "*$_*" }).Count -gt 0
        } | ForEach-Object {
            $bytes = $_.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
            '-----BEGIN CERTIFICATE-----'
            [Convert]::ToBase64String($bytes, 'InsertLineBreaks')
            '-----END CERTIFICATE-----'
        }
        """
        result = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True, check=False)
        extra_roots = result.stdout.strip()
        if extra_roots: 
            bundle += b"\n" + extra_roots.encode("utf-8") + b"\n"
            
    # Write the verified bundle out and update environments globally
    with open(combined_path, "wb") as dst: 
        dst.write(bundle)
        
    os.environ["CURL_CA_BUNDLE"] = combined_path
    os.environ["SSL_CERT_FILE"] = combined_path
    os.environ["REQUESTS_CA_BUNDLE"] = combined_path
    return combined_path

setup_ssl_certificates()

# --- HEADER ---
st.title("📊 Nivesh Bodh: Pre-Market Engine")
st.markdown("A top-down algorithmic market scanner by **Nivesh Gyanam**")
st.divider()

# --- 1. MACRO MARKET SNAPSHOT ---
st.subheader("1. Macro Market Snapshot")
@st.cache_data(ttl=300)
def get_macro_data():
    macros = ["^NSEI", "^NSEBANK", "^INDIAVIX", "INR=X", "DX-Y.NYB", "BZ=F", "GC=F"]
    data = []
    for ticker in macros:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="5d")
            if not df.empty:
                last_close = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2]
                change_pct = ((last_close - prev_close) / prev_close) * 100
                unit = "$" if "F" in ticker else "₹" if "INR" in ticker or "NSE" in ticker else ""
                data.append({"Name": MACROS_AND_SECTORS[ticker], "Price": f"{unit}{last_close:,.2f}", "Delta": f"{change_pct:+.2f}%"})
        except:
            pass
    return data

macro_data = get_macro_data()
if macro_data:
    cols = st.columns(len(macro_data))
    for i, item in enumerate(macro_data):
        cols[i].metric(label=item["Name"], value=item["Price"], delta=item["Delta"])
else:
    st.error("Macro Market Snapshot data is currently blank or failed to sync via network.")
st.divider()

# --- 2. SECTOR INDEX HEATMAP ---
st.subheader("2. Sector Index Heatmap")
@st.cache_data(ttl=300)
def get_sector_data():
    sectors = ["^CNXIT", "^CNXAUTO", "^CNXPHARMA", "^CNXFMCG", "^CNXMETAL", "^CNXENERGY"]
    results = []
    for ticker in sectors:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="5d")
            if not df.empty and len(df) >= 2:
                last_close = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2]
                change = ((last_close - prev_close) / prev_close) * 100
                results.append({"Sector": MACROS_AND_SECTORS[ticker], "Close": round(last_close, 2), "Change (%)": round(change, 2)})
        except:
            pass
    if results:
        return pd.DataFrame(results).sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
    return pd.DataFrame(columns=["Sector", "Close", "Change (%)"])

sector_df = get_sector_data()
if not sector_df.empty:
    st.dataframe(sector_df, width='stretch')
else:
    st.error("Sector Index Heatmap data is currently unavailable.")
st.divider()

# --- 3. CROSS-SECTOR MULTI-CAP VIEW (WITH GYANAM SCORE) ---
st.subheader("3. Cross-Sector Multi-Cap View")

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

@st.cache_data(ttl=300)
def get_stock_data():
    results = []
    for ticker, info in WATCHLIST.items():
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="6mo")
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
                    "Ticker": ticker.replace(".NS", ""), "Sector": info["sector"],
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

stock_df = get_stock_data()
if not stock_df.empty:
    st.dataframe(stock_df, width='stretch')
else:
    st.error("Watchlist Stock matrix failed to generate.")
st.divider()

# --- 4. STOCK GYANAM: DEEP DIVE HUB ---
st.subheader("🔍 4. Stock Gyanam: Analysis & Charting Hub")

combined_options = list(WATCHLIST.keys()) + list(MACROS_AND_SECTORS.keys())
def format_dropdown(ticker):
    if ticker in WATCHLIST: return f"{ticker.replace('.NS', '')} [Stock]"
    return f"{MACROS_AND_SECTORS[ticker]} [Macro/Index]"

selected_asset = st.selectbox("Select Asset to Analyze:", combined_options, format_func=format_dropdown)

if selected_asset:
    with st.spinner(f"Loading Gyanam Diagnostics..."):
        try:
            gyanam_stock = yf.Ticker(selected_asset)
            tab_chart, tab_fundamentals = st.tabs(["📈 Technical Charting", "🏢 Functional/Fundamental Health"])
            
            with tab_chart:
                chart_df = gyanam_stock.history(period="6mo")
                if not chart_df.empty and len(chart_df) > 50:
                    chart_df['EMA_20'] = chart_df['Close'].ewm(span=20, adjust=False).mean()
                    chart_df['EMA_50'] = chart_df['Close'].ewm(span=50, adjust=False).mean()
                    
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(x=chart_df.index, open=chart_df['Open'], high=chart_df['High'],
                                    low=chart_df['Low'], close=chart_df['Close'], name='Price'))
                    fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['EMA_20'], line=dict(color='orange', width=2), name='20-Day EMA'))
                    fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['EMA_50'], line=dict(color='cyan', width=2), name='50-Day EMA'))
                    
                    fig.update_layout(height=500, margin=dict(l=0, r=0, t=20, b=0), xaxis_rangeslider_visible=False, template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Could not load sufficient chart data.")

            with tab_fundamentals:
                if selected_asset in MACROS_AND_SECTORS:
                    st.info("💡 **Macro Asset Selected:** Institutional fundamentals like P/E Ratio and ROE do not apply to global indices or commodities.")
                else:
                    try:
                        info = gyanam_stock.info
                        pe_ratio = round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else "N/A"
                        roe = round(info.get('returnOnEquity', 0) * 100, 2) if info.get('returnOnEquity') else "N/A"
                        debt_eq = round(info.get('debtToEquity', 0) / 100, 2) if info.get('debtToEquity') else "N/A"
                        margins = round(info.get('profitMargins', 0) * 100, 2) if info.get('profitMargins') else "N/A"
                        
                        st.markdown("### Core Financial Scorecard")
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("P/E Ratio", pe_ratio)
                        col2.metric("Return on Equity (ROE)", f"{roe}%" if roe != "N/A" else "N/A")
                        col3.metric("Debt-to-Equity", debt_eq)
                        col4.metric("Net Profit Margin", f"{margins}%" if margins != "N/A" else "N/A")
                    except:
                        st.warning("Fundamental data temporarily unavailable.")
        except:
            st.error("Error running deep dive diagnostics for this asset.")

st.divider()

# --- 5. DAILY LEARNING ---
st.subheader("5. Nivesh Gyanam: Daily Learning")
topics = [
    {"topic": "MACD Crossovers", "lesson": "When the MACD line crosses above the Signal line, it indicates shifting bullish momentum. When paired with an RSI crossing 50, probability of a sustained rally increases."},
    {"topic": "The 50-EMA Baseline", "lesson": "The 50-Day Exponential Moving Average is the institutional baseline. Assets trading above it are in uptrends; assets below it are in downtrends. Buy the bounces, sell the breakdowns."},
    {"topic": "Volume Validation", "lesson": "A breakout is only trustworthy if the daily volume significantly exceeds the 20-day Volume MA. Low volume breakouts are often traps."},
    {"topic": "Position Sizing", "lesson": "Never risk more than 1-2% of your total capital on a single trade. If your stop loss is hit, the portfolio should barely feel it."}
]
day_of_year = datetime.now().timetuple().tm_yday
random.seed(day_of_year)
daily_lesson = random.choice(topics)
st.info(f"**💡 {daily_lesson['topic']}**: {daily_lesson['lesson']}")
random.seed()
