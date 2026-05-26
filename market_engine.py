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

# --- MARKET SENTIMENT TRACKER SIDEBAR ---
st.sidebar.markdown("### 🧭 Premium Hub Sneak Peek")
st.sidebar.info("**FII / DII Flows Matrix:** Integrating Daily Data Ingestion Pipelines...\n\n**Pro Risk Manager:** Automated Portfolio Alerts Coming Soon...")

# --- 1. [NEW SPRINT FEATURE] PRE-MARKET DIRECTIONAL BIAS ENGINE ---
st.subheader("🧭 Early Morning Directional Bias")

@st.cache_data(ttl=60)
def calculate_pre_market_bias():
    try:
        # Batch download GIFT Nifty futures proxy and Nifty 50 Spot data simultaneously
        data = yf.download(["IN1!=F", "^NSEI"], period="5d", progress=False)
        
        gift_df = data["IN1!=F"].dropna()
        nifty_df = data["^NSEI"].dropna()
        
        if not gift_df.empty and not nifty_df.empty:
            gift_live = gift_df['Close'].iloc[-1]
            nifty_spot_close = nifty_df['Close'].iloc[-1]
            
            # Compute point gap spread value
            gap_points = gift_live - nifty_spot_close
            
            # Algorithmic Sentiment Classification Matrix
            if gap_points >= 70:
                sentiment = "🚀 STRONG GAP-UP EXPECTED"
                color = "green"
                details = f"GIFT Nifty is trading at aggressive premiums (+{gap_points:.2f} points). Institutional opening bids indicate overwhelming bullish control."
            elif 20 <= gap_points < 70:
                sentiment = "🟢 MILD POSITIVE OPENING"
                color = "green"
                details = f"GIFT Nifty is flashing moderate premiums (+{gap_points:.2f} points). Expect a steady, positive start with initial dip buying."
            elif -20 < gap_points < 20:
                sentiment = "⚪ FLAT / NEUTRAL OPENING"
                color = "orange"
                details = f"GIFT Nifty spread is highly compressed ({gap_points:+.2f} points). The market will open flat. Focus purely on stock-specific breakout zones."
            elif -70 < gap_points <= -20:
                sentiment = "🔴 MILD NEGATIVE OPENING"
                color = "red"
                details = f"GIFT Nifty is indicating a discount ({gap_points:.2f} points). Global macro pressures indicate early morning supply overhead."
            else:
                sentiment = "💥 STRUCTURAL GAP-DOWN EXPECTED"
                color = "red"
                details = f"GIFT Nifty is flashing severe downside discounts ({gap_points:.2f} points). Heavy bearish momentum globally; protect long positions."
                
            return {"sentiment": sentiment, "color": color, "details": details, "gift": gift_live, "nifty": nifty_spot_close}
    except:
        pass
    return None

bias_data = calculate_pre_market_bias()

if bias_data:
    with st.container(border=True):
        if bias_data["color"] == "green":
            st.success(f"### {bias_data['sentiment']}")
        elif bias_data["color"] == "orange":
            st.warning(f"### {bias_data['sentiment']}")
        else:
            st.error(f"### {bias_data['sentiment']}")
        st.markdown(f"**Market Context:** {bias_data['details']}")
        st.caption(f"GIFT Nifty Live Continuous Proxy: {bias_data['gift']:,.2f} | Nifty 50 Spot Prev Close: {bias_data['nifty']:,.2f}")
else:
    st.info("🧭 Running cross-border sentiment matrix calculations...")

st.divider()

# --- 2. MACRO MARKET SNAPSHOT (BALANCED ALIGNED GRID) ---
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
                        "Name": MACROS_AND_SECTORS[ticker], 
                        "Price": f"{unit}{last_close:,.2f}", 
                        "Delta": f"{change_pct:+.2f}%"
                    })
    except:
        pass
    return data

macro_data = get_macro_data_batch()

if macro_data:
    for i in range(0, len(macro_data), 4):
        chunk = macro_data[i:i+4]
        cols = st.columns(4)
        for idx, item in enumerate(chunk):
            with cols[idx]:
                with st.container(border=True):
                    st.metric(label=item["Name"], value=item["Price"], delta=item["Delta"])
else:
    st.info("🔄 Refreshing Macro Market feeds...")

st.divider()

# --- 3. SECTOR INDEX HEATMAP ---
st.subheader("2. Sector Index Heatmap")

@st.cache_data(ttl=60)
def get_sector_data_batch():
    sectors = ["^CNXIT", "^CNXAUTO", "^CNXPHARMA", "^CNXFMCG", "^CNXMETAL", "^CNXENERGY"]
    results = []
    try:
        group = yf.download(sectors, period="5d", group_by='ticker', progress=False)
        for ticker in sectors:
            if ticker in group.columns.levels[0]:
                df = group[ticker].dropna()
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

sector_df = get_sector_data_batch()
if not sector_df.empty:
    st.dataframe(sector_df, use_container_width=True)
else:
    st.info("🔄 Re-calculating sector matrices...")

st.divider()

# --- 4. CROSS-SECTOR MULTI-CAP VIEW (WITH GYANAM SCORE) ---
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

# --- 5. STOCK GYANAM: DEEP DIVE HUB ---
st.subheader("🔍 4. Stock Gyanam: Analysis & Charting Hub")

combined_options = list(WATCHLIST.keys()) + [k for k in MACROS_AND_SECTORS.keys() if k in yf.download(list(MACROS_AND_SECTORS.keys()), period="1d", progress=False).columns.levels[0]]
def format_dropdown(ticker):
    if ticker in WATCHLIST: return f"{ticker.replace('.NS', '')} [Stock]"
    return f"{MACROS_AND_SECTORS[ticker]} [Macro/Index]"

selected_asset = st.selectbox("Select Asset to Analyze:", combined_options, format_func=format_dropdown)

if selected_asset:
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
                st.warning("Insufficient trading history to populate chart indicators.")

        with tab_fundamentals:
            if ".NS" not in selected_asset:
                st.info("💡 **Macro Asset Selected:** Institutional metrics like P/E and ROE are restricted to equity stocks.")
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
                    st.warning("Fundamental financial details temporarily out of sync.")
    except:
        st.error("Error generating granular asset insights.")

st.divider()

# --- 6. DAILY LEARNING ---
st.subheader("5. Nivesh Gyanam: Daily Learning")
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
