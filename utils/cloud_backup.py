"""
BHARATSOLVE SEO AGENCY — Cloud Backup & Sync
Database export/import for Streamlit Cloud persistence.
Since SQLite on Streamlit Cloud uses /tmp/ (ephemeral),
this provides JSON-based backup that can be stored in:

1. GitHub Gist (via API token)
2. Local JSON export/import
3. Streamlit Cloud session-based recovery
"""
import json
import os
import base64
import hashlib
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# ── Paths ──
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups")
_IS_CLOUD = os.environ.get('STREAMLIT_RUNNER_ID') is not None

if _IS_CLOUD:
    BACKUP_DIR = "/tmp/backups"

os.makedirs(BACKUP_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# BACKUP FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def export_db_to_json() -> Dict[str, Any]:
    """
    Export the entire SQLite database to a JSON-serializable dict.
    All tables are exported as lists of row dicts.
    """
    from db.schema import get_connection, DB_PATH
    
    conn = get_connection()
    try:
        # Get all table names
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        
        backup = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "source_db": os.path.basename(DB_PATH),
            "tables": {},
            "hash": ""
        }
        
        for (table_name,) in tables:
            if table_name == "sqlite_sequence":
                continue
            
            rows = conn.execute(f"SELECT * FROM {table_name}").fetchall()
            if rows:
                backup["tables"][table_name] = [dict(r) for r in rows]
            else:
                backup["tables"][table_name] = []
        
        # Create hash for integrity checking
        content_for_hash = json.dumps(backup["tables"], sort_keys=True, default=str)
        backup["hash"] = hashlib.sha256(content_for_hash.encode()).hexdigest()
        
        return backup
    finally:
        conn.close()


def import_db_from_json(backup_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Import data from a JSON backup into the SQLite database.
    
    Args:
        backup_data: Dict with 'tables' key containing table data
    
    Returns:
        Dict with import results (tables processed, row counts)
    """
    from db.schema import get_connection
    
    if not backup_data or "tables" not in backup_data:
        return {"success": False, "error": "Invalid backup format"}
    
    # Verify hash if present
    tables_data = backup_data.get("tables", {})
    if backup_data.get("hash"):
        content = json.dumps(tables_data, sort_keys=True, default=str)
        expected_hash = hashlib.sha256(content.encode()).hexdigest()
        if expected_hash != backup_data["hash"]:
            return {"success": False, "error": "Backup hash mismatch — data may be corrupted"}
    
    conn = get_connection()
    results = {}
    
    try:
        for table_name, rows in tables_data.items():
            if not rows:
                results[table_name] = 0
                continue
            
            # Get column info
            col_info = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
            columns = [c[1] for c in col_info if c[1] not in ('id',)]
            id_column = table_name == "users"  # Don't overwrite users
            
            inserted = 0
            for row in rows:
                try:
                    # Filter to valid columns
                    filtered = {k: v for k, v in row.items() if k in columns}
                    
                    if filtered:
                        cols = list(filtered.keys())
                        placeholders = ", ".join(["?" for _ in cols])
                        values = [filtered[c] for c in cols]
                        
                        # Convert timestamps to strings if they're datetime objects
                        values = [v.isoformat() if hasattr(v, 'isoformat') else v for v in values]
                        
                        conn.execute(
                            f"INSERT OR IGNORE INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders})",
                            values
                        )
                        inserted += 1
                except Exception as row_err:
                    logger.warning(f"⚠️ Skipping row in {table_name}: {row_err}")
            
            results[table_name] = inserted
        
        conn.commit()
        return {
            "success": True,
            "tables_processed": len(tables_data),
            "total_rows_imported": sum(results.values()),
            "details": results
        }
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def save_backup_to_file(backup_data: Optional[Dict] = None, label: str = "manual") -> str:
    """
    Export DB and save to a JSON file in backup directory.
    
    Args:
        backup_data: Optional data to save. If None, exports live DB.
        label: Label for the backup file
    
    Returns:
        Path to the backup file
    """
    if backup_data is None:
        backup_data = export_db_to_json()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"seo_backup_{label}_{timestamp}.json"
    filepath = os.path.join(BACKUP_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, default=str)
    
    # Also save a "latest" copy for easy restore
    latest_path = os.path.join(BACKUP_DIR, "seo_backup_latest.json")
    with open(latest_path, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, default=str)
    
    logger.info(f"💾 Backup saved: {filepath}")
    return filepath


def load_backup_from_file(filepath: str) -> Optional[Dict]:
    """Load a backup from a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load backup: {e}")
        return None


def list_backups() -> List[Dict]:
    """List all available backup files."""
    if not os.path.exists(BACKUP_DIR):
        return []
    
    backups = []
    for fname in os.listdir(BACKUP_DIR):
        if fname.endswith(".json") and fname.startswith("seo_backup_"):
            fpath = os.path.join(BACKUP_DIR, fname)
            size = os.path.getsize(fpath)
            mtime = os.path.getmtime(fpath)
            backups.append({
                "filename": fname,
                "path": fpath,
                "size_kb": round(size / 1024, 1),
                "modified": datetime.fromtimestamp(mtime).isoformat(),
                "is_latest": "latest" in fname
            })
    
    return sorted(backups, key=lambda b: b['modified'], reverse=True)


def delete_backup(filepath: str) -> bool:
    """Delete a backup file."""
    try:
        os.remove(filepath)
        return True
    except:
        return False


# ═══════════════════════════════════════════════════════════════
# GIST BACKUP (for Streamlit Cloud persistence)
# ═══════════════════════════════════════════════════════════════

def get_gist_token() -> str:
    """Get GitHub Gist API token from environment or secrets."""
    token = os.getenv("GIST_API_TOKEN", "")
    if not token:
        try:
            import streamlit as st
            token = st.secrets.get("GIST_API_TOKEN", "")
        except:
            pass
    
    # Fallback: try to get from any GitHub token available
    if not token:
        token = os.getenv("GITHUB_TOKEN", "")
    return token


def backup_to_gist(backup_data: Optional[Dict] = None, 
                   description: str = "BHARATSOLVE SEO Agency Backup") -> Dict:
    """
    Upload backup to GitHub Gist for cloud persistence.
    
    Args:
        backup_data: Backup data to upload. If None, exports live DB.
        description: Gist description
    
    Returns:
        Dict with result including gist URL if successful
    """
    token = get_gist_token()
    if not token:
        return {"success": False, "error": "No GIST_API_TOKEN configured"}
    
    if backup_data is None:
        backup_data = export_db_to_json()
    
    filename = f"seo_backup_{datetime.now().strftime('%Y-%m-%d')}.json"
    
    import requests
    
    try:
        gist_data = {
            "description": description,
            "public": False,
            "files": {
                filename: {
                    "content": json.dumps(backup_data, indent=2, default=str)
                }
            }
        }
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        resp = requests.post(
            "https://api.github.com/gists",
            headers=headers,
            json=gist_data,
            timeout=30
        )
        
        if resp.status_code in (200, 201):
            data = resp.json()
            return {
                "success": True,
                "gist_id": data.get("id", ""),
                "url": data.get("html_url", ""),
                "filename": filename
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {resp.status_code}: {resp.text[:200]}"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def restore_from_gist(gist_id: str) -> Dict:
    """
    Download and restore a backup from GitHub Gist.
    
    Args:
        gist_id: The Gist ID (or full URL)
    
    Returns:
        Dict with restore results
    """
    token = get_gist_token()
    if not token:
        return {"success": False, "error": "No GIST_API_TOKEN configured"}
    
    # Extract ID from URL if full URL provided
    if gist_id.startswith("http"):
        gist_id = gist_id.rstrip('/').split('/')[-1]
    
    import requests
    
    try:
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        resp = requests.get(
            f"https://api.github.com/gists/{gist_id}",
            headers=headers,
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            files = data.get("files", {})
            
            # Find the backup file in the gist
            for fname, fdata in files.items():
                if fname.endswith(".json") and "seo_backup" in fname:
                    content = json.loads(fdata.get("content", "{}"))
                    result = import_db_from_json(content)
                    result["gist_url"] = data.get("html_url", "")
                    result["restored_from"] = fname
                    return result
            
            return {"success": False, "error": "No backup file found in gist"}
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# CONFIG BACKUP
# ═══════════════════════════════════════════════════════════════

def export_config() -> Dict:
    """Export app configuration."""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config.json"
    )
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except:
        return {}


def export_env_references() -> Dict:
    """Export env variable names (not values) for documentation."""
    return {
        "required_vars": [
            "GROQ_API_KEY",
            "GEMINI_API_KEY",
        ],
        "optional_vars": [
            "OPENAI_API_KEY",
            "DEEPSEEK_API_KEY",
            "FACEBOOK_ACCESS_TOKEN",
            "FACEBOOK_PAGE_ID",
            "INSTAGRAM_BUSINESS_ID",
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_CHAT_ID",
            "SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS",
            "SENDGRID_API_KEY",
            "GOOGLE_BUSINESS_TOKEN",
            "GSC_SERVICE_ACCOUNT_JSON",
            "GIST_API_TOKEN",
        ]
    }


def full_export(label: str = "full") -> Dict:
    """
    Perform a full system export: DB + config + env references.
    
    Returns:
        Dict with all exported data
    """
    return {
        "type": "full_export",
        "exported_at": datetime.now().isoformat(),
        "data": {
            "db_export": export_db_to_json(),
            "config": export_config(),
            "env_references": export_env_references(),
        }
    }


def auto_backup():
    """
    Automatic backup routine — can be called by scheduler.
    Saves to local file, optionally to Gist if token is configured.
    """
    try:
        # Always save local backup
        backup_data = export_db_to_json()
        filepath = save_backup_to_file(backup_data, label="auto")
        
        # Try Gist if token available
        token = get_gist_token()
        if token:
            gist_result = backup_to_gist(backup_data)
            if gist_result.get('success'):
                logger.info(f"☁️ Gist backup: {gist_result.get('url', '')}")
        
        return {"success": True, "local_path": filepath}
    except Exception as e:
        logger.error(f"Auto-backup failed: {e}")
        return {"success": False, "error": str(e)}
