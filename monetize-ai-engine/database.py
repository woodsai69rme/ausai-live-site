import os
import sqlite3
import json

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "automonetize.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        niche TEXT,
        pricing_model TEXT,
        estimated_mrr TEXT,
        html_code TEXT,
        css_code TEXT,
        js_code TEXT,
        qa_score INTEGER DEFAULT 100,
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS marketing_campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_name TEXT,
        target_audience TEXT,
        campaign_json TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS domain_watchlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT UNIQUE,
        status TEXT,
        price_estimate TEXT,
        category TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def save_project(title, niche="", pricing_model="", estimated_mrr="", html_code="", css_code="", js_code="", qa_score=100, notes=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO projects (title, niche, pricing_model, estimated_mrr, html_code, css_code, js_code, qa_score, notes, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (title, niche, pricing_model, estimated_mrr, html_code, css_code, js_code, qa_score, notes))
    pid = c.lastrowid
    conn.commit()
    conn.close()
    return pid

def list_projects():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM projects ORDER BY updated_at DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_project(pid):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM projects WHERE id = ?", (pid,))
    r = c.fetchone()
    conn.close()
    return dict(r) if r else None

def delete_project(pid):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM projects WHERE id = ?", (pid,))
    conn.commit()
    conn.close()
    return True

def save_campaign(app_name, target_audience, campaign_data):
    conn = get_connection()
    c = conn.cursor()
    cj = json.dumps(campaign_data) if isinstance(campaign_data, dict) else str(campaign_data)
    c.execute("INSERT INTO marketing_campaigns (app_name, target_audience, campaign_json) VALUES (?, ?, ?)", (app_name, target_audience, cj))
    cid = c.lastrowid
    conn.commit()
    conn.close()
    return cid

def list_campaigns():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM marketing_campaigns ORDER BY created_at DESC LIMIT 25")
    rows = []
    for r in c.fetchall():
        d = dict(r)
        try:
            d["campaign_data"] = json.loads(d["campaign_json"])
        except:
            d["campaign_data"] = {}
        rows.append(d)
    conn.close()
    return rows

def save_domain_watchlist(domain, status, price_estimate, category=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO domain_watchlist (domain, status, price_estimate, category, created_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)", (domain, status, price_estimate, category))
    conn.commit()
    conn.close()
    return True

def list_domain_watchlist():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM domain_watchlist ORDER BY created_at DESC LIMIT 50")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

init_db()
