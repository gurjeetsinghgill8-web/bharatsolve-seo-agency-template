"""
BHARATSOLVE SEO AGENCY — Database Operations
All CRUD operations for the SEO agency database.
"""
from .schema import get_connection
from datetime import datetime, timedelta
import json

# ── USER OPERATIONS ──

def create_user(username, password_hash, full_name="", email=""):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO users (username, password_hash, full_name, email) VALUES (?, ?, ?, ?)",
                     (username, password_hash, full_name, email))
        conn.commit()
        return True
    except Exception as e:
        print(f"User creation error: {e}")
        return False
    finally:
        conn.close()

def get_user(username):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

def update_subscription(username, tier):
    conn = get_connection()
    conn.execute("UPDATE users SET subscription_tier = ? WHERE username = ?", (tier, username))
    conn.commit()
    conn.close()

# ── CLIENT OPERATIONS ──

def create_client(user_id, name, website="", email="", phone="", business_type="", location="", notes=""):
    conn = get_connection()
    conn.execute("""
        INSERT INTO clients (user_id, name, website, email, phone, business_type, location, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, name, website, email, phone, business_type, location, notes))
    conn.commit()
    client_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return client_id

def get_clients(user_id):
    conn = get_connection()
    clients = conn.execute("SELECT * FROM clients WHERE user_id = ? AND is_active = 1 ORDER BY created_at DESC", (user_id,)).fetchall()
    conn.close()
    return [dict(c) for c in clients]

def get_client(client_id):
    conn = get_connection()
    client = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    conn.close()
    return dict(client) if client else None

def update_client(client_id, **kwargs):
    conn = get_connection()
    fields = {k: v for k, v in kwargs.items() if v is not None}
    if fields:
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [client_id]
        conn.execute(f"UPDATE clients SET {set_clause} WHERE id = ?", values)
        conn.commit()
    conn.close()

def delete_client(client_id):
    conn = get_connection()
    conn.execute("UPDATE clients SET is_active = 0 WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()

# ── PROJECT OPERATIONS ──

def create_project(client_id, name, target_location="", target_language="hi"):
    conn = get_connection()
    conn.execute("""
        INSERT INTO projects (client_id, name, target_location, target_language)
        VALUES (?, ?, ?, ?)
    """, (client_id, name, target_location, target_language))
    conn.commit()
    project_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return project_id

def get_projects(client_id):
    conn = get_connection()
    projects = conn.execute("SELECT * FROM projects WHERE client_id = ? AND is_active = 1", (client_id,)).fetchall()
    conn.close()
    return [dict(p) for p in projects]

def get_project(project_id):
    conn = get_connection()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    return dict(project) if project else None

def get_all_projects():
    conn = get_connection()
    projects = conn.execute("""
        SELECT p.*, c.name as client_name, c.user_id
        FROM projects p JOIN clients c ON p.client_id = c.id
        WHERE p.is_active = 1
    """).fetchall()
    conn.close()
    return [dict(p) for p in projects]

# ── KEYWORD OPERATIONS ──

def add_keyword(project_id, keyword, target_url="", search_volume=0, difficulty=0):
    conn = get_connection()
    conn.execute("""
        INSERT INTO keywords (project_id, keyword, target_url, search_volume, difficulty)
        VALUES (?, ?, ?, ?, ?)
    """, (project_id, keyword, target_url, search_volume, difficulty))
    conn.commit()
    kid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return kid

def get_keywords(project_id):
    conn = get_connection()
    keywords = conn.execute("SELECT * FROM keywords WHERE project_id = ? AND is_active = 1", (project_id,)).fetchall()
    conn.close()
    return [dict(k) for k in keywords]

def update_keyword_position(keyword_id, position):
    conn = get_connection()
    conn.execute("UPDATE keywords SET current_position = ? WHERE id = ?", (position, keyword_id))
    conn.execute("""
        UPDATE keywords SET best_position = ? WHERE id = ? AND (? < best_position OR best_position = 0)
    """, (position, keyword_id, position))
    conn.execute("INSERT INTO rankings (keyword_id, position) VALUES (?, ?)", (keyword_id, position))
    conn.commit()
    conn.close()

def get_rankings_history(keyword_id, days=30):
    conn = get_connection()
    since = (datetime.now() - timedelta(days=days)).isoformat()
    rows = conn.execute("""
        SELECT position, checked_at FROM rankings
        WHERE keyword_id = ? AND checked_at >= ?
        ORDER BY checked_at ASC
    """, (keyword_id, since)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── CONTENT OPERATIONS ──

def save_content(project_id, title, content, content_type="blog", target_keyword="", meta_title="", meta_description="", schema_json=""):
    conn = get_connection()
    conn.execute("""
        INSERT INTO content_pieces (project_id, title, content, content_type, target_keyword, meta_title, meta_description, schema_json, word_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (project_id, title, content, content_type, target_keyword, meta_title, meta_description, schema_json, len(content.split())))
    conn.commit()
    cid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return cid

def get_content(project_id, content_type=None, limit=20):
    conn = get_connection()
    if content_type:
        rows = conn.execute("""
            SELECT * FROM content_pieces WHERE project_id = ? AND content_type = ?
            ORDER BY created_at DESC LIMIT ?
        """, (project_id, content_type, limit)).fetchall()
    else:
        rows = conn.execute("""
            SELECT * FROM content_pieces WHERE project_id = ?
            ORDER BY created_at DESC LIMIT ?
        """, (project_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── AGENT LOG OPERATIONS ──

def log_agent_action(agent_name, task, status="ok", response_time_ms=0, error_message=""):
    conn = get_connection()
    conn.execute("""
        INSERT INTO agent_logs (agent_name, task, status, response_time_ms, error_message)
        VALUES (?, ?, ?, ?, ?)
    """, (agent_name, task, status, response_time_ms, error_message))
    conn.commit()
    conn.close()

def get_agent_logs(agent_name=None, limit=50):
    conn = get_connection()
    if agent_name:
        rows = conn.execute("""
            SELECT * FROM agent_logs WHERE agent_name = ?
            ORDER BY logged_at DESC LIMIT ?
        """, (agent_name, limit)).fetchall()
    else:
        rows = conn.execute("""
            SELECT * FROM agent_logs ORDER BY logged_at DESC LIMIT ?
        """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_agent_status_summary():
    """Get summary of latest status for each agent."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT agent_name, status, response_time_ms, error_message, logged_at
        FROM agent_logs
        WHERE logged_at IN (SELECT MAX(logged_at) FROM agent_logs GROUP BY agent_name)
        ORDER BY agent_name
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── SOCIAL POST OPERATIONS ──

def schedule_social_post(project_id, platform, content, scheduled_for=None):
    conn = get_connection()
    conn.execute("""
        INSERT INTO social_posts (project_id, platform, content, scheduled_for)
        VALUES (?, ?, ?, ?)
    """, (project_id, platform, content, scheduled_for))
    conn.commit()
    pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return pid

def update_social_post_status(post_id, status, posted_at=None):
    conn = get_connection()
    if posted_at:
        conn.execute("UPDATE social_posts SET status = ?, posted_at = ? WHERE id = ?",
                     (status, posted_at, post_id))
    else:
        conn.execute("UPDATE social_posts SET status = ? WHERE id = ?",
                     (status, post_id))
    conn.commit()
    conn.close()

def get_scheduled_posts(project_id, limit=20):
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM social_posts WHERE project_id = ?
        ORDER BY created_at DESC LIMIT ?
    """, (project_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── SUBSCRIPTION OPERATIONS ──

def create_subscription(user_id, plan_type, amount, transaction_id=""):
    end_date = (datetime.now() + timedelta(days=30)).isoformat()
    conn = get_connection()
    conn.execute("""
        INSERT INTO subscriptions (user_id, plan_type, amount_paid, end_date, is_active, transaction_id)
        VALUES (?, ?, ?, ?, 1, ?)
    """, (user_id, plan_type, amount, end_date, transaction_id))
    conn.commit()
    conn.close()

def get_active_subscription(user_id):
    conn = get_connection()
    sub = conn.execute("""
        SELECT * FROM subscriptions
        WHERE user_id = ? AND is_active = 1 AND end_date > datetime('now')
        ORDER BY end_date DESC LIMIT 1
    """, (user_id,)).fetchone()
    conn.close()
    return dict(sub) if sub else None

# ── DASHBOARD STATS ──

def get_dashboard_stats(user_id):
    conn = get_connection()
    stats = {}
    
    # Total keywords tracked across all client projects
    stats['total_keywords'] = conn.execute("""
        SELECT COUNT(*) FROM keywords k
        JOIN projects p ON k.project_id = p.id
        JOIN clients c ON p.client_id = c.id
        WHERE c.user_id = ? AND k.is_active = 1
    """, (user_id,)).fetchone()[0]
    
    # Active clients
    stats['active_clients'] = conn.execute(
        "SELECT COUNT(*) FROM clients WHERE user_id = ? AND is_active = 1", (user_id,)
    ).fetchone()[0]
    
    # Average rank
    avg = conn.execute("""
        SELECT AVG(k.current_position) FROM keywords k
        JOIN projects p ON k.project_id = p.id
        JOIN clients c ON p.client_id = c.id
        WHERE c.user_id = ? AND k.current_position > 0
    """, (user_id,)).fetchone()[0]
    stats['avg_rank'] = round(avg, 1) if avg else 0
    
    # Content count
    stats['total_content'] = conn.execute("""
        SELECT COUNT(*) FROM content_pieces cp
        JOIN projects p ON cp.project_id = p.id
        JOIN clients c ON p.client_id = c.id
        WHERE c.user_id = ?
    """, (user_id,)).fetchone()[0]
    
    conn.close()
    return stats

# ── WORDPRESS SITE OPERATIONS ──

def save_wp_site(user_id, site_name, url, username, password_encrypted, xmlrpc_url=""):
    """Add a new WordPress site configuration."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO wp_sites (user_id, site_name, url, xmlrpc_url, username, password_encrypted)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, site_name, url, xmlrpc_url, username, password_encrypted))
    conn.commit()
    site_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return site_id

def get_wp_sites(user_id=None):
    """Get WordPress sites, optionally filtered by user."""
    conn = get_connection()
    if user_id:
        rows = conn.execute(
            "SELECT * FROM wp_sites WHERE user_id = ? AND is_active = 1 ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM wp_sites WHERE is_active = 1 ORDER BY created_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_wp_site(site_id):
    """Get a single WordPress site by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM wp_sites WHERE id = ?", (site_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_wp_site(site_id, **kwargs):
    """Update a WordPress site configuration."""
    conn = get_connection()
    fields = {k: v for k, v in kwargs.items() if v is not None}
    if fields:
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [site_id]
        conn.execute(f"UPDATE wp_sites SET {set_clause} WHERE id = ?", values)
        conn.commit()
    conn.close()

def delete_wp_site(site_id):
    """Soft-delete a WordPress site."""
    conn = get_connection()
    conn.execute("UPDATE wp_sites SET is_active = 0 WHERE id = ?", (site_id,))
    conn.commit()
    conn.close()

def update_wp_site_last_sync(site_id):
    """Update the last_sync timestamp for a WP site."""
    conn = get_connection()
    conn.execute("UPDATE wp_sites SET last_sync = CURRENT_TIMESTAMP WHERE id = ?", (site_id,))
    conn.commit()
    conn.close()

# ── CONTENT PUBLISH STATUS ──

def update_content_publish_status(content_id, status, url=""):
    """Update the publish status and URL of a content piece."""
    conn = get_connection()
    conn.execute(
        "UPDATE content_pieces SET status = ?, published_url = ? WHERE id = ?",
        (status, url, content_id)
    )
    conn.commit()
    conn.close()

def get_single_content(content_id):
    """Get a single content piece by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM content_pieces WHERE id = ?", (content_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_unpublished_content(project_id, limit=20):
    """Get content pieces that haven't been published yet."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM content_pieces 
        WHERE project_id = ? AND (published_url IS NULL OR published_url = '')
        ORDER BY created_at DESC LIMIT ?
    """, (project_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_published_content(project_id, limit=20):
    """Get content pieces that have been published."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM content_pieces 
        WHERE project_id = ? AND published_url IS NOT NULL AND published_url != ''
        ORDER BY created_at DESC LIMIT ?
    """, (project_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Search function ──

def search_all(user_id, query):
    """Search across clients, projects, keywords, content."""
    conn = get_connection()
    results = {"clients": [], "projects": [], "keywords": [], "content": []}
    
    like = f"%{query}%"
    
    clients = conn.execute("""
        SELECT id, name, website FROM clients
        WHERE user_id = ? AND (name LIKE ? OR website LIKE ? OR location LIKE ?)
        LIMIT 5
    """, (user_id, like, like, like)).fetchall()
    results['clients'] = [dict(c) for c in clients]
    
    keywords = conn.execute("""
        SELECT k.id, k.keyword, k.current_position, p.name as project_name
        FROM keywords k JOIN projects p ON k.project_id = p.id
        JOIN clients c ON p.client_id = c.id
        WHERE c.user_id = ? AND k.keyword LIKE ?
        LIMIT 5
    """, (user_id, like)).fetchall()
    results['keywords'] = [dict(k) for k in keywords]
    
    conn.close()
    return results
