"""
Database management for Nivesh Bodh
Handles persistent storage for watchlists, alerts, and user preferences
"""

import sqlite3
import json
from datetime import datetime
import os
from pathlib import Path

DB_PATH = Path("data/nivesh_bodh.db")
DB_PATH.parent.mkdir(exist_ok=True)

def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Watchlist table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watchlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT 'default',
            ticker TEXT NOT NULL,
            sector TEXT,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, ticker)
        )
    ''')
    
    # Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT 'default',
            ticker TEXT NOT NULL,
            alert_type TEXT,
            threshold REAL,
            telegram_chat_id TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            triggered_date TIMESTAMP
        )
    ''')
    
    # User preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferences (
            user_id TEXT PRIMARY KEY,
            telegram_chat_id TEXT,
            telegram_enabled BOOLEAN DEFAULT 0,
            email TEXT,
            theme TEXT DEFAULT 'dark',
            alert_frequency TEXT DEFAULT 'immediate',
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Price history for correlation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            price REAL,
            volume INTEGER,
            date DATE,
            UNIQUE(ticker, date)
        )
    ''')
    
    conn.commit()
    conn.close()

class WatchlistManager:
    """Manage user watchlists"""
    
    @staticmethod
    def add_to_watchlist(ticker, sector, user_id="default"):
        """Add stock to watchlist"""
        init_database()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO watchlists (user_id, ticker, sector) VALUES (?, ?, ?)',
                (user_id, ticker, sector)
            )
            conn.commit()
            return {"status": "success", "message": f"{ticker} added to watchlist"}
        except sqlite3.IntegrityError:
            return {"status": "exists", "message": f"{ticker} already in watchlist"}
        finally:
            conn.close()
    
    @staticmethod
    def get_watchlist(user_id="default"):
        """Get all watchlist items"""
        init_database()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT ticker, sector, added_date FROM watchlists WHERE user_id = ? ORDER BY added_date DESC',
            (user_id,)
        )
        results = cursor.fetchall()
        conn.close()
        
        return [{"ticker": r[0], "sector": r[1], "added_date": r[2]} for r in results]
    
    @staticmethod
    def remove_from_watchlist(ticker, user_id="default"):
        """Remove stock from watchlist"""
        init_database()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            'DELETE FROM watchlists WHERE user_id = ? AND ticker = ?',
            (user_id, ticker)
        )
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"{ticker} removed from watchlist"}

class AlertManager:
    """Manage price and technical alerts"""
    
    @staticmethod
    def create_alert(ticker, alert_type, threshold, telegram_chat_id=None, user_id="default"):
        """Create new alert"""
        init_database()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts (user_id, ticker, alert_type, threshold, telegram_chat_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, ticker, alert_type, threshold, telegram_chat_id))
        
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Alert created for {ticker} ({alert_type})"}
    
    @staticmethod
    def get_active_alerts(user_id="default"):
        """Get all active alerts"""
        init_database()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, ticker, alert_type, threshold, telegram_chat_id, created_date
            FROM alerts WHERE user_id = ? AND is_active = 1
            ORDER BY created_date DESC
        ''', (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": r[0],
                "ticker": r[1],
                "alert_type": r[2],
                "threshold": r[3],
                "telegram_chat_id": r[4],
                "created_date": r[5]
            } for r in results
        ]
    
    @staticmethod
    def delete_alert(alert_id, user_id="default"):
        """Deactivate alert"""
        init_database()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE alerts SET is_active = 0 WHERE id = ? AND user_id = ?',
            (alert_id, user_id)
        )
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Alert deleted"}

class PreferencesManager:
    """Manage user preferences"""
    
    @staticmethod
    def set_telegram(telegram_chat_id, user_id="default"):
        """Set telegram chat ID"""
        init_database()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO preferences (user_id, telegram_chat_id, telegram_enabled)
            VALUES (?, ?, 1)
        ''', (user_id, telegram_chat_id))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_preferences(user_id="default"):
        """Get user preferences"""
        init_database()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT telegram_chat_id, telegram_enabled, theme FROM preferences WHERE user_id = ?',
            (user_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "telegram_chat_id": result[0],
                "telegram_enabled": result[1],
                "theme": result[2]
            }
        return {"telegram_chat_id": None, "telegram_enabled": False, "theme": "dark"}
