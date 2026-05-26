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

# ADDED NASDAQ (^IXIC) FOR GLOBAL TECH INFLUENCE
MACROS_AND_SECTORS = {
    "^NSEI": "Nifty 50", "^NSEBANK": "Bank Nifty", "^INDIAVIX": "India VIX", 
    "^IXIC": "Nasdaq (Global Tech)", "INR=X": "USD/INR", "DX-Y.NYB": "Dollar Index", 
    "BZ=F": "Brent Crude", "GC=F": "Gold (Global)",
    "^CNXIT": "Nifty IT", "^CNXAUTO": "Nifty Auto", "^CNXPHARMA": "Nifty Pharma",
    "^CNXFMCG": "Nifty FMCG", "^CNXMETAL": "Nifty Metal", "^CNXENERGY": "Nifty Energy"
}

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

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

# --- HEADER & SMART NAVIGATION ---
st.title("📊 Nivesh Bodh: Pre-Market Engine")
st.markdown("A top-down algorithmic market scanner by **Nivesh Gyanam | Deepesh Soni**")

# SMART NAVIGATION GUIDE (Tells users exactly what is below)
st.caption("⚡ **Dashboard Quick-View:** 1️⃣ Directional Bias | 2️⃣ Macro Matrix | 3️⃣ Sector Heatmap | 4️⃣ Stock Gyanam Tracker | 5️⃣ Market News")

if st.sidebar.button("🔄 Force Live Refresh"):
    st.cache_data.clear()
    st.rerun()

st.divider()

# --- SIDEBAR: PREMIUM TEASERS & OPTIONS DATA ---
st.sidebar.markdown("### 🧭 Options Pulse (O/I)")
st.sidebar.info("**Nifty PCR:** 0.85 (Oversold Area)\n\n**Max Pain Strike:** 22,500\n\n*(Derivatives API integration pending broker connection)*")
st.sidebar.divider()
st.sidebar.markdown("### 🧠 Premium Features")
st.sidebar.info("**FII / DII Matrix:** Coming Soon...\n\n**Portfolio Alerts:** Coming Soon...")

# --- 1. PRE-MARKET DIRECTIONAL BIAS ENGINE & DYNAMIC ONE-LINER ---
st.subheader("🧭 1. Early Morning Directional Bias")

@st.cache_data(ttl=30)
def calculate_pre_market_bias_safe():
    try:
        gift_ticker = yf.Ticker("IN1!=F")
        gift_df = gift_ticker.history(period="2d")
        
        nifty_ticker = yf.Ticker("^NSEI")
        nifty_df = nifty_ticker.history(period="2d")
        
        vix_ticker = yf.Ticker("^INDIAVIX")
        vix_df = vix_ticker.history(period="2d")
        
        if not gift_df.empty and not nifty_df.empty and not vix_df.empty:
            gift_live = gift_df['Close'].iloc[-1]
            nifty_spot_close = nifty_df['Close'].iloc[-1]
            gap_points = gift_live - nifty_spot_close
            
            nifty_change = ((nifty_spot_close - nifty_df['Close'].iloc[-2]) / nifty_df['Close'].iloc[-2]) * 100
            vix_change = ((vix_df['Close'].iloc[-1] - vix_df['Close'].iloc[-2]) / vix_df['Close'].iloc[-2]) * 100
            
            # Smart One-Liner Logic
            if nifty_change < -0.5 and vix_change > 2:
                pulse = "🚨 **Smart Pulse:** Nifty is facing pressure today amid a sharp spike in India VIX. Defensive stance recommended."
            elif nifty_change > 0.5 and gap_points > 20:
                pulse = "🔥 **Smart Pulse:** Bulls are in full control globally. Look for breakout confirmation in High-Beta sectors like Metals and Autos."
            else:
                pulse = "⚖️ **Smart Pulse:** Market is in a tight consolidation phase. Focus strictly on stock-specific setups and sector rotation."

            if gap_points >= 70:
                sentiment, color = "🚀 STRONG GAP-UP EXPECTED", "green"
            elif 20 <= gap_points < 70:
                sentiment, color = "🟢 MILD POSITIVE OPENING", "green"
            elif -20 < gap_points < 20:
                sentiment, color = "⚪ FLAT / NEUTRAL OPENING", "orange"
            elif -70 < gap_points <= -20:
                sentiment, color = "🔴 MILD NEGATIVE OPENING", "red"
            else:
                sentiment, color = "💥 STRUCTURAL GAP-DOWN EXPECTED", "red"
                
            return {"sentiment": sentiment, "color": color, "gift": gift_live, "nifty": nifty_spot_close, "pulse": pulse}
    except:
        pass
    return None

bias_data = calculate_pre_market_bias_safe()

if bias_data:
    with st.container(border=True):
        if bias_data["color"] == "green":
            st.success(f"### {bias_data['sentiment']}")
        elif bias_data["color"] == "orange":
            st.warning(f"### {bias_data['sentiment']}")
        else:
            st.error(f"### {bias_data['sentiment']}")
            
        st.markdown(bias_data["pulse"])
        st.caption(f"GIFT Nifty Continuous Proxy: {bias_data['gift']:,.2f} | Nifty Spot Prev Close: {bias_data['nifty']:,.2f}")
else:
    st.info("🧭 Syncing cross-border data nodes. Click 'Force Live Refresh' in the sidebar if this takes more than 10 seconds.")

st.divider()

# --- 2. PREMIUM MACRO MARKET SNAPSHOT ---
st.subheader("🌐 2. Macro Market Snapshot")

@st.cache_data(ttl=60)
def get_macro_data_batch():
    macros = ["^NSEI", "^NSEBANK", "^INDIAVIX", "^IXIC", "INR=X", "DX-Y.NYB", "BZ=F", "GC=F"]
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
                    unit = "$" if "F" in ticker or "^IXIC" in ticker else "₹" if "INR" in ticker or "NSE" in ticker else ""
                    
                    data.append({
                        "Global Asset": MACROS_AND_SECTORS[ticker], 
                        "Value": f"{unit}{last_close:,.2f}", 
                        "RawChange": change_pct, 
                        "Change (%)": f"{change_pct:+.2f}%"
                    })
    except:
        pass
    return data

macro_list = get_macro_data_batch()

if macro_list:
    macro_matrix_df = pd.DataFrame(macro_list)
    def style_macro_ticker(row):
        text_color = "#48bb78" if row["RawChange"] >= 0 else "#f56565"
        return ["", f"color: {text_color}; font-weight: bold;", "", f"color: {text_color}; font-weight: bold;"]

    cleaned_render_df = macro_matrix_df.drop(columns=["RawChange"])
    styled_ticker_df = macro_matrix_df.style.apply(style_macro_ticker, axis=1)
    st.dataframe(styled_ticker_df, use_container_width=True, hide_index=True, column_order=["Global Asset", "Value", "Change (%)"])
else:
    st.info("🔄 Refreshing Macro Market feeds...")

st.divider()

# --- 3. INTERACTIVE SECTOR HEATMAP (ANIMATED TREEMAP) ---
st.subheader("🔥 3. Sector Index Heatmap")

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
        return pd.DataFrame(results)
    return pd.DataFrame(columns=["Sector", "Close", "Change (%)"])

sector_df = get_sector_data_batch()
if not sector_df.empty:
    sector_df["Market"] = "NSE Sectors"
    fig_tree = px.treemap(
        sector_df, path=["Market", "Sector"], values="Close", color="Change (%)",
        color_continuous_scale=["#f56565", "#1e2430", "#48bb78"], color_continuous_midpoint=0,
        custom_data=["Change (%)", "Close"]
    )
    fig_tree.update_traces(texttemplate="<b>%{label}</b><br>%{customdata[0]:+.2f}%", hovertemplate="<b>%{label}</b><br>Close: ₹%{customdata[1]:,.2f}<br>Change: %{customdata[0]:+.2f}%<extra></extra>", textfont=dict(size=14, color="white"))
    fig_tree.update_layout(margin=dict(t=10, l=0, r=0, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350)
    st.plotly_chart(fig_tree, use_container_width=True)
else:
    st.info("🔄 Re-calculating sector matrices...")

st.divider()

# --- 4. MULTI-CAP VIEW (ANIMATED PROGRESS BARS) ---
st.subheader("🎯 4. Cross-Sector Multi-Cap Tracker")

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
                        "Gyanam Score": int(g_score),
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
    st.dataframe(
        stock_df, use_container_width=True, hide_index=True,
        column_config={
            "Gyanam Score": st.column_config.ProgressColumn("Gyanam Health Score", help="> 70 indicates strong bullish momentum.", format="%d", min_value=0, max_value=100),
            "RSI (14)": st.column_config.NumberColumn("RSI (14)", help="Over 70 = Overbought | Under 30 = Oversold", format="%.2f")
        }
    )
else:
    st.info("🔄 Running multi-cap scan...")

st.divider()

# --- 5. STOCK GYANAM: DEEP DIVE HUB ---
st.subheader("🔍 5. Stock Gyanam: Analysis & Charting Hub")

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

# --- 6. MARKET NEWS & DAILY LEARNING ---
st.subheader("📰 6. Market News & Daily Learning")

tab_news, tab_learn = st.tabs(["Breaking News", "Algorithmic Learning"])

with tab_news:
    # This is a placeholder UI layout for future News API integration
    st.info("🔌 *News API integration pending. Displaying curated macro themes:*")
    st.markdown("""
    * **Global Equities:** US Federal Reserve maintains rates, sparking tech sector relief rally (Nasdaq impact).
    * **Domestic Flows:** SEBI issues new framework for derivative (F&O) trading volumes to curb retail speculation.
    * **Commodities:** Brent Crude prices stabilize around $82/bbl as OPEC+ maintains supply cuts.
    """)

with tab_learn:
    topics = [
        {"topic": "MACD Crossovers", "lesson": "When the MACD line crosses above the Signal line, it indicates shifting bullish momentum. When paired with an RSI crossing 50, probability of a sustained rally increases."},
        {"topic": "The 50-EMA Baseline", "lesson": "The 50-Day Exponential Moving Average is the institutional baseline. Assets trading above it are in uptrends; assets below it are in downtrends. Buy the bounces, sell the breakdowns."},
        {"topic": "Volume Validation", "lesson": "A breakout is only trustworthy if the daily volume significantly exceeds the 20-day Volume MA. Low volume breakouts are often traps."}
    ]
    day_of_year = datetime.now().timetuple().tm_yday
    random.seed(day_of_year)
    daily_lesson = random.choice(topics)
    st.success(f"**💡 {daily_lesson['topic']}**: {daily_lesson['lesson']}")
    random.seed()
