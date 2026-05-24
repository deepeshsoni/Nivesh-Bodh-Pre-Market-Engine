"""
Telegram alert notifications for Nivesh Bodh
Sends real-time trading signals and alerts to users
"""

import os
from telegram import Bot
from telegram.error import TelegramError
import asyncio
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

class TelegramNotifier:
    """Send alerts via Telegram"""
    
    def __init__(self, bot_token=TELEGRAM_BOT_TOKEN):
        self.bot_token = bot_token
        self.bot = Bot(token=bot_token) if bot_token else None
    
    async def send_alert(self, chat_id, message, parse_mode="HTML"):
        """Send alert message to Telegram"""
        if not self.bot:
            logger.warning("Telegram bot not configured")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info(f"Alert sent to {chat_id}")
            return True
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    def send_alert_sync(self, chat_id, message, parse_mode="HTML"):
        """Synchronous wrapper for alert sending"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.send_alert(chat_id, message, parse_mode))
    
    async def send_price_alert(self, chat_id, ticker, current_price, alert_type, threshold):
        """Send price alert"""
        message = f"""
<b>🚨 Price Alert - {ticker}</b>

<b>Alert Type:</b> {alert_type}
<b>Current Price:</b> ₹{current_price:.2f}
<b>Threshold:</b> ₹{threshold:.2f}

<i>Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return await self.send_alert(chat_id, message)
    
    async def send_technical_signal(self, chat_id, ticker, gyanam_score, signals, rsi, price):
        """Send technical analysis signal"""
        signal_str = " | ".join(signals) if signals else "⚪ NEUTRAL"
        
        message = f"""
<b>📊 Technical Signal - {ticker}</b>

<b>Price:</b> ₹{price:.2f}
<b>Gyanam Score:</b> {gyanam_score}/100
<b>RSI (14):</b> {rsi:.2f}
<b>Signals:</b> {signal_str}

<i>Action: Review chart and confirm with price action</i>
<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return await self.send_alert(chat_id, message)
    
    async def send_correlation_alert(self, chat_id, ticker1, ticker2, correlation, direction):
        """Send correlation-based alert"""
        message = f"""
<b>🔗 Correlation Alert</b>

<b>{ticker1} ↔ {ticker2}</b>
<b>Correlation:</b> {correlation:.3f}
<b>Relationship:</b> {direction}

<i>When {ticker1} moves up, {ticker2} tends to move {'up' if correlation > 0 else 'down'}</i>
<i>Use for hedging and portfolio optimization</i>
"""
        return await self.send_alert(chat_id, message)
    
    async def send_sentiment_alert(self, chat_id, ticker, sentiment_score, sentiment_label, news_summary):
        """Send sentiment analysis alert"""
        sentiment_emoji = "📈" if sentiment_score > 0.3 else "📉" if sentiment_score < -0.3 else "➡️"
        
        message = f"""
<b>{sentiment_emoji} Sentiment Alert - {ticker}</b>

<b>Sentiment Score:</b> {sentiment_score:.3f}
<b>Label:</b> <b>{sentiment_label}</b>

<b>Recent News:</b>
{news_summary[:200]}

<i>Combine with technical analysis for complete picture</i>
"""
        return await self.send_alert(chat_id, message)

def send_telegram_alert(chat_id, ticker, gyanam_score, signals, rsi, price, message_type="technical"):
    """Simple function to send alerts from Streamlit"""
    notifier = TelegramNotifier()
    
    if message_type == "technical":
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            notifier.send_technical_signal(chat_id, ticker, gyanam_score, signals, rsi, price)
        )
