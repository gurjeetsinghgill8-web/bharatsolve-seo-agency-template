"""
BHARATSOLVE SEO AGENCY — Backup & Restore UI
Cloud backup management with local + Gist support.
"""
import streamlit as st
import os
import json
from datetime import datetime

from utils.cloud_backup import (
    export_db_to_json, import_db_from_json, save_backup_to_file,
    load_backup_from_file, list_backups, delete_backup,
    backup_to_gist, restore_from_gist, get_gist_token,
    auto_backup, full_export
)
from db.operations import log_agent_action


def show_backup_page():
    """Render the backup & restore management page."""
    user_id = st.session_state["user_id"]
    
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <h1 style="background: linear-gradient(90deg, #00d2ff, #3a7bd5); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size: 2rem; margin: 0;">💾 Backup & Restore</h1>
        <p style="color: #888;">Protect your SEO data — local exports, cloud sync, and disaster recovery</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ── Cloud status ──
    is_cloud = os.environ.get('STREAMLIT_RUNNER_ID') is not None
    has_gist_token = bool(get_gist_token())
    backup_dir_info = "/tmp/backups" if is_cloud else "backups/"
    
    if is_cloud:
        st.warning("☁️ **Streamlit Cloud detected!** Database is in `/tmp/` and will reset on redeploy. "
                   "Use backups to persist your data.")
    
    st.info(f"📁 Backup directory: `{backup_dir_info}`")
    
    st.markdown("---")
    
    # ════════════════════════════════════════
    # TABS
    # ════════════════════════════════════════
    tab1, tab2, tab3 = st.tabs(["💾 Create Backup", "📂 Restore", "⚙️ Cloud Sync"])
    
    # ════════════════════════════════════════
    # TAB 1: Create Backup
    # ════════════════════════════════════════
    with tab1:
        st.markdown("### Create a Backup")
        st.markdown("Export your entire database (clients, projects, keywords, content, posts, etc.) to a JSON file.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📥 Local Backup**")
            if st.button("💾 Export DB to File", type="primary", use_container_width=True):
                with st.spinner("Exporting database..."):
                    filepath = save_backup_to_file(label="manual")
                st.success(f"✅ Backup saved! `{os.path.basename(filepath)}`")
                st.info(f"📁 Size: {os.path.getsize(filepath) / 1024:.1f} KB")
                log_agent_action("backup", f"Manual backup saved: {filepath}")
        
        with col2:
            st.markdown("**📊 Full System Export**")
            if st.button("📦 Export All (DB + Config)", use_container_width=True):
                with st.spinner("Exporting full system state..."):
                    export = full_export()
                    filepath = save_backup_to_file(export, label="full_system")
                st.success(f"✅ Full export saved!")
                st.info(f"📁 Includes DB, config.json, and env references")
        
        with col3:
            st.markdown("**☁️ Backup to Gist**")
            if not has_gist_token:
                st.warning("⚠️ Set `GIST_API_TOKEN` in secrets")
            else:
                if st.button("☁️ Upload to GitHub Gist", use_container_width=True):
                    with st.spinner("Uploading to Gist..."):
                        result = backup_to_gist()
                    if result.get('success'):
                        st.success(f"✅ Backup uploaded to Gist!")
                        st.markdown(f"🔗 [Open Gist]({result.get('url', '#')})")
                        log_agent_action("backup", f"Gist backup: {result.get('gist_id', '')}")
                    else:
                        st.error(f"❌ {result.get('error', 'Upload failed')}")
        
        st.markdown("---")
        
        # ── Auto-backup settings ──
        st.markdown("### 🤖 Auto-Backup")
        st.markdown("""
        When the **Auto-Pilot** or **Scheduler** runs, it automatically creates a backup.
        
        - **Local:** Always saves a timestamped JSON file
        - **Cloud (Gist):** Uploads to GitHub Gist if `GIST_API_TOKEN` is configured
        """)
        
        # Show existing backups
        st.markdown("---")
        st.markdown("### 📋 Existing Backups")
        
        backups = list_backups()
        if backups:
            for b in backups:
                with st.container():
                    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                    c1.markdown(f"📄 `{b['filename']}`")
                    c2.markdown(f"{b['size_kb']} KB")
                    c3.markdown(f"{b['modified'][:16]}")
                    
                    if c4.button("🗑️ Delete", key=f"del_backup_{b['filename']}"):
                        if delete_backup(b['path']):
                            st.success(f"Deleted {b['filename']}")
                            st.rerun()
                    
                    if b.get('is_latest'):
                        c1.markdown("⭐ **Latest**")
                    
                    st.markdown("---")
        else:
            st.info("💡 No backups yet. Create your first backup above!")
    
    # ════════════════════════════════════════
    # TAB 2: Restore
    # ════════════════════════════════════════
    with tab2:
        st.markdown("### 🔄 Restore from Backup")
        st.warning("⚠️ **Warning:** Restoring will overwrite your current database data!")
        
        st.markdown("#### 📁 Restore from Local File")
        
        backups = list_backups()
        if backups:
            backup_files = [b['filename'] for b in backups]
            selected_file = st.selectbox("Select a backup to restore", backup_files)
            
            if st.button("🔄 Restore Selected Backup", type="primary", use_container_width=True):
                if selected_file:
                    with st.spinner("Loading backup..."):
                        backup_data = load_backup_from_file(
                            os.path.join(
                                "/tmp/backups" if is_cloud else 
                                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups"),
                                selected_file
                            )
                        )
                    
                    if backup_data:
                        st.info(f"📊 Backup contains: {list(backup_data.get('tables', {}).keys())}")
                        
                        confirm = st.checkbox("I understand this will overwrite current data")
                        if confirm:
                            with st.spinner("Restoring database..."):
                                result = import_db_from_json(backup_data)
                            
                            if result.get('success'):
                                st.success(f"✅ Restore complete!")
                                st.markdown(f"""
                                - Tables processed: {result.get('tables_processed', 0)}
                                - Rows imported: {result.get('total_rows_imported', 0)}
                                """)
                                log_agent_action("backup", f"Restored from: {selected_file}")
                            else:
                                st.error(f"❌ Restore failed: {result.get('error', '')}")
                    else:
                        st.error("❌ Could not load backup file")
        else:
            st.info("💡 No backup files found. Create a backup first in the 'Create Backup' tab.")
        
        st.markdown("---")
        st.markdown("#### 📝 Manual Upload")
        
        uploaded_file = st.file_uploader("Upload a backup JSON file", type=['json'])
        if uploaded_file is not None:
            try:
                backup_data = json.loads(uploaded_file.read())
                st.success(f"✅ Loaded backup from `{uploaded_file.name}`")
                
                if st.button("🔄 Restore from Uploaded File", type="primary", use_container_width=True):
                    with st.spinner("Restoring..."):
                        result = import_db_from_json(backup_data)
                    if result.get('success'):
                        st.success(f"✅ Restored! {result.get('total_rows_imported', 0)} rows imported")
                    else:
                        st.error(f"❌ {result.get('error', '')}")
            except Exception as e:
                st.error(f"❌ Invalid backup file: {e}")
    
    # ════════════════════════════════════════
    # TAB 3: Cloud Sync
    # ════════════════════════════════════════
    with tab3:
        st.markdown("### ☁️ GitHub Gist Sync")
        st.markdown("""
        Use GitHub Gists to persist your database on Streamlit Cloud.
        Since `/tmp/` is ephemeral, Gist backups let you:
        
        1. **Backup up** → Upload your DB to a private Gist
        2. **Restore down** → Download and restore from a Gist
        3. **Auto-backup** → Scheduled via the Sagger
        """)
        
        # Gist token config
        has_token = bool(get_gist_token())
        
        if has_token:
            st.success("✅ **GIST_API_TOKEN** is configured!")
        else:
            st.error("❌ **GIST_API_TOKEN** not found!")
            st.markdown("""
            **To set up Gist backup:**
            1. Create a [GitHub Personal Access Token](https://github.com/settings/tokens/new)
               with scope: `gist`
            2. Add it to your Streamlit secrets:
            ```toml
            # .streamlit/secrets.toml
            GIST_API_TOKEN = "ghp_xxxxxxxxxxxxxxxx"
            ```
            Or as environment variable `GIST_API_TOKEN`.
            """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⬆️ Upload to Gist")
            if st.button("☁️ Backup to Gist", use_container_width=True, type="primary"):
                if has_token:
                    with st.spinner("Uploading..."):
                        result = backup_to_gist()
                    if result.get('success'):
                        st.success(f"✅ Uploaded!")
                        st.markdown(f"🆔 Gist ID: `{result.get('gist_id', '')}`")
                        st.markdown(f"🔗 [Open]({result.get('url', '#')})")
                    else:
                        st.error(f"❌ {result.get('error', '')}")
                else:
                    st.warning("Configure GIST_API_TOKEN first")
        
        with col2:
            st.markdown("#### ⬇️ Restore from Gist")
            gist_id = st.text_input("Gist ID or URL", 
                                     placeholder="https://api.github.com/gists/xxx or just xxx")
            
            if st.button("🔄 Restore from Gist", use_container_width=True, type="secondary"):
                if gist_id:
                    with st.spinner("Downloading and restoring..."):
                        result = restore_from_gist(gist_id)
                    if result.get('success'):
                        st.success(f"✅ Restored from Gist!")
                        st.markdown(f"📊 {result.get('total_rows_imported', 0)} rows imported")
                    else:
                        st.error(f"❌ {result.get('error', '')}")
                else:
                    st.warning("Enter a Gist ID")
        
        st.markdown("---")
        st.markdown("#### 🔧 One-Click Cloud Recovery")
        st.markdown("""
        If your Streamlit Cloud app lost data (deploy reset):
        1. Enter your Gist ID above
        2. Click "Restore from Gist"
        3. Refresh the app — your data will be back!
        """)
        
        st.markdown("---")
        
        # Backup schedule info
        st.markdown("#### 📅 Backup Schedule")
        st.markdown("""
        - **Auto-backup:** Runs with every full scheduler cycle
        - **On deploy:** Run a manual backup after setting up your data
        - **Frequency:** Recommend weekly backups to Gist for cloud safety
        """)
