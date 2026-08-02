"""
BHARATSOLVE SEO AGENCY — Database Schema (SQLite)
Multi-agent SEO system with full relational model.
"""
import sqlite3
import os

# On Streamlit Cloud, use /tmp directory for writable DB
_is_cloud = os.environ.get('STREAMLIT_RUNNER_ID') is not None
if _is_cloud:
    DB_PATH = "/tmp/seo_agency.db"
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "seo_agency.db")

def get_connection():
    """Get a thread-safe SQLite connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # ── Users (agency owner) ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT DEFAULT '',
            email TEXT DEFAULT '',
            is_admin INTEGER DEFAULT 0,
            subscription_tier TEXT DEFAULT 'freelancer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Clients ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            website TEXT DEFAULT '',
            email TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            business_type TEXT DEFAULT '',
            location TEXT DEFAULT '',
            google_business_url TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Projects ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            target_location TEXT DEFAULT '',
            target_language TEXT DEFAULT 'hi',
            monthly_budget REAL DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)

    # ── Keywords ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            keyword TEXT NOT NULL,
            target_url TEXT DEFAULT '',
            current_position INTEGER DEFAULT 0,
            best_position INTEGER DEFAULT 0,
            search_volume INTEGER DEFAULT 0,
            difficulty INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # ── Rankings History ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rankings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword_id INTEGER NOT NULL,
            position INTEGER NOT NULL,
            search_type TEXT DEFAULT 'organic',
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (keyword_id) REFERENCES keywords(id)
        )
    """)

    # ── Content Pieces ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_pieces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content_type TEXT DEFAULT 'blog',
            status TEXT DEFAULT 'draft',
            word_count INTEGER DEFAULT 0,
            target_keyword TEXT DEFAULT '',
            meta_title TEXT DEFAULT '',
            meta_description TEXT DEFAULT '',
            schema_json TEXT DEFAULT '',
            content TEXT DEFAULT '',
            published_url TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # ── Backlinks ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backlinks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            source_url TEXT NOT NULL,
            target_url TEXT NOT NULL,
            domain_authority INTEGER DEFAULT 0,
            is_follow INTEGER DEFAULT 1,
            status TEXT DEFAULT 'discovered',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # ── Crawl Audits ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crawl_audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            total_pages INTEGER DEFAULT 0,
            broken_links INTEGER DEFAULT 0,
            missing_meta INTEGER DEFAULT 0,
            slow_pages INTEGER DEFAULT 0,
            schema_errors INTEGER DEFAULT 0,
            score INTEGER DEFAULT 0,
            report_json TEXT DEFAULT '',
            audited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # ── Reports ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            report_type TEXT DEFAULT 'weekly',
            pdf_path TEXT DEFAULT '',
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # ── Social Posts ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS social_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            content TEXT NOT NULL,
            media_url TEXT DEFAULT '',
            scheduled_for TIMESTAMP,
            posted_at TIMESTAMP,
            status TEXT DEFAULT 'scheduled',
            engagement_data TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # ── Subscriptions ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_type TEXT DEFAULT 'freelancer',
            amount_paid REAL DEFAULT 499,
            start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_date TIMESTAMP,
            is_active INTEGER DEFAULT 0,
            payment_method TEXT DEFAULT 'UPI',
            transaction_id TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Agent Logs ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_name TEXT NOT NULL,
            task TEXT DEFAULT '',
            status TEXT DEFAULT 'ok',
            response_time_ms INTEGER DEFAULT 0,
            error_message TEXT DEFAULT '',
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── API Keys ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            provider TEXT NOT NULL,
            api_key_encrypted TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── WordPress Sites ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wp_sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            site_name TEXT NOT NULL,
            url TEXT NOT NULL,
            xmlrpc_url TEXT DEFAULT '',
            username TEXT NOT NULL,
            password_encrypted TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            last_sync TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Chat History (for Manager Agent) ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Clinic Configuration (for Gill Heart Clinic) ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clinic_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT DEFAULT '',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Competitors Tracking ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS competitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            location TEXT DEFAULT '',
            specialty TEXT DEFAULT '',
            estimated_reviews INTEGER DEFAULT 0,
            estimated_rating REAL DEFAULT 0,
            strengths TEXT DEFAULT '[]',
            website TEXT DEFAULT '',
            keywords_overlap INTEGER DEFAULT 0,
            avg_rank REAL DEFAULT 0,
            last_scanned TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Review Replies History ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS review_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            review_id TEXT NOT NULL,
            reviewer_name TEXT DEFAULT '',
            review_text TEXT DEFAULT '',
            rating INTEGER DEFAULT 0,
            reply_text TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            posted_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Patient Community Posts (GEO Community Feature) ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_community (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            author_name TEXT DEFAULT 'Anonymous Patient',
            post_type TEXT DEFAULT 'testimonial',
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            doctor_reply TEXT DEFAULT '',
            is_approved INTEGER DEFAULT 0,
            is_featured INTEGER DEFAULT 0,
            likes_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Seed Default Admin Users ──
    try:
        import hashlib
        def _h(p): return hashlib.sha256(p.encode()).hexdigest()
        
        # Check if GG user exists
        user_gg = cursor.execute("SELECT id FROM users WHERE username = ?", ("GG",)).fetchone()
        if not user_gg:
            cursor.execute(
                "INSERT INTO users (username, password_hash, full_name, email, is_admin, subscription_tier) VALUES (?, ?, ?, ?, ?, ?)",
                ("GG", _h("12"), "Dr. Gurjeet Singh Gill", "gurjeetsinghgill8@gmail.com", 1, "agency")
            )
            print("Permanent user 'GG' created (password: 12)")

        # Check if drgill user exists
        user_check = cursor.execute("SELECT id FROM users WHERE username = ?", ("drgill",)).fetchone()
        if not user_check:
            cursor.execute(
                "INSERT INTO users (username, password_hash, full_name, email, is_admin, subscription_tier) VALUES (?, ?, ?, ?, ?, ?)",
                ("drgill", _h("gill123"), "Dr. Gurjeet Singh Gill", "gurjeetsinghgill8@gmail.com", 1, "agency")
            )
            print("Default user 'drgill' created (password: gill123)")

        # Check if default Gill Clinic client exists
        user_id_ref = cursor.execute("SELECT id FROM users WHERE username = ?", ("GG",)).fetchone()
        if user_id_ref:
            uid = user_id_ref[0]
            client_check = cursor.execute("SELECT id FROM clients WHERE user_id = ?", (uid,)).fetchone()
            if not client_check:
                cursor.execute(
                    "INSERT INTO clients (user_id, name, website, email, phone, business_type, location) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (uid, "Gill Heart Clinic", "https://gurjeetsinghgill8-web.github.io/gill-heart-clinic/", "gurjeetsinghgill8@gmail.com", "+91-9258879884", "Cardiology Clinic", "Mohiuddinpur, Meerut")
                )
                print("Default client created")
                client_id = cursor.lastrowid
            else:
                client_id = client_check[0]

            proj_check = cursor.execute("SELECT id FROM projects WHERE client_id = ?", (client_id,)).fetchone()
            if not proj_check:
                cursor.execute(
                    "INSERT INTO projects (client_id, name, target_location, target_language) VALUES (?, ?, ?, ?)",
                    (client_id, "Gill Clinic SEO", "Meerut, Delhi NCR", "hi")
                )
                print("Default project created")
        
        conn.commit()
    except Exception as e:
        print(f"User seeding warning: {e}")

    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
