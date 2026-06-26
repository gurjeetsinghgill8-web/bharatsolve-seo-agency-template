"""
BHARATSOLVE SEO AGENCY — Client Management UI
Add, edit, view clients and their projects.
"""
import streamlit as st
from db.operations import (
    create_client, get_clients, get_client, update_client, delete_client,
    create_project, get_projects
)


def show_clients_page():
    """Render client management page."""
    user_id = st.session_state["user_id"]
    
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <h1 style="background: linear-gradient(90deg, #00d2ff, #3a7bd5); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size: 2rem; margin: 0;">👥 Client Management</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # ── Add New Client ──
    with st.expander("➕ Add New Client", expanded=False):
        with st.form("new_client_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Client Name *", placeholder="e.g., Sharma Dentclinic")
                website = st.text_input("Website", placeholder="https://example.com")
                email = st.text_input("Email", placeholder="client@email.com")
                phone = st.text_input("Phone", placeholder="+91-9876543210")
            
            with col2:
                business_type = st.selectbox(
                    "Business Type",
                    ["General", "Clinic", "Dental", "Ayurveda", "Real Estate", 
                     "Education", "E-commerce", "Travel", "Restaurant", "Other"]
                )
                location = st.text_input("Location", placeholder="e.g., Delhi, India")
                notes = st.text_area("Notes", placeholder="Any special instructions...", height=100)
            
            submitted = st.form_submit_button("✅ Add Client", use_container_width=True)
            
            if submitted and name:
                client_id = create_client(user_id, name, website, email, phone, business_type, location, notes)
                st.success(f"✅ Client '{name}' added successfully!")
                st.rerun()
            elif submitted:
                st.warning("⚠️ Client name is required!")
    
    st.markdown("---")
    
    # ── Client List ──
    clients = get_clients(user_id)
    
    if not clients:
        st.info("👆 No clients yet. Add your first client above!")
        return
    
    # Search/filter
    search = st.text_input("🔍 Search clients...", placeholder="Search by name, website, or location")
    
    if search:
        clients = [c for c in clients if search.lower() in c['name'].lower() or 
                   search.lower() in c.get('website', '').lower() or
                   search.lower() in c.get('location', '').lower()]
    
    st.markdown(f"**Total Clients: {len(clients)}**")
    
    # Client cards
    for client in clients:
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.7); border-radius: 10px; padding: 1rem; margin: 0.3rem 0;
                            border-left: 4px solid #0077b6; box-shadow: 0 2px 8px rgba(0,119,182,0.08);">
                    <h3 style="margin: 0; color: #0077b6;">{client['name']}</h3>
                    <p style="margin: 0.2rem 0; color: #555;">
                        {'🌐 ' + client['website'] if client['website'] else ''}
                        {' 📍 ' + client['location'] if client['location'] else ''}
                        {' 🏢 ' + client['business_type'] if client['business_type'] else ''}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("📝 Edit", key=f"edit_{client['id']}", use_container_width=True):
                    st.session_state[f"editing_client_{client['id']}"] = True
            
            with col3:
                if st.button("🗑️", key=f"del_{client['id']}", use_container_width=True):
                    delete_client(client['id'])
                    st.rerun()
        
        # Edit form
        if st.session_state.get(f"editing_client_{client['id']}", False):
            with st.form(f"edit_client_form_{client['id']}"):
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Name", value=client['name'])
                    new_website = st.text_input("Website", value=client.get('website', ''))
                    new_email = st.text_input("Email", value=client.get('email', ''))
                with col2:
                    new_location = st.text_input("Location", value=client.get('location', ''))
                    new_notes = st.text_area("Notes", value=client.get('notes', ''), height=80)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.form_submit_button("💾 Save", use_container_width=True):
                        update_client(client['id'], name=new_name, website=new_website,
                                    email=new_email, location=new_location, notes=new_notes)
                        st.session_state[f"editing_client_{client['id']}"] = False
                        st.rerun()
                with col_b:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state[f"editing_client_{client['id']}"] = False
                        st.rerun()
        
        # Projects for this client
        projects = get_projects(client['id'])
        if projects:
            with st.expander(f"📁 Projects ({len(projects)})", key=f"proj_{client['id']}"):
                for proj in projects:
                    st.markdown(f"""
                    <div style="background: rgba(0,119,182,0.05); border-radius: 5px; padding: 0.5rem 1rem; margin: 0.2rem 0; border: 1px solid #e0f0ff;">
                        📂 <strong style="color: #0077b6;">{proj['name']}</strong>
                        <span style="color: #666; margin-left: 1rem;">📍 {proj.get('target_location', 'Any')}</span>
                        <span style="color: #666; float: right;">💰 ₹{proj.get('monthly_budget', 0)}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Add project button
        with st.expander(f"➕ Add Project for {client['name']}", key=f"add_proj_{client['id']}"):
            with st.form(f"project_form_{client['id']}"):
                col1, col2 = st.columns(2)
                with col1:
                    proj_name = st.text_input("Project Name *", placeholder="e.g., SEO Campaign 2026")
                    proj_location = st.text_input("Target Location", placeholder="e.g., Delhi NCR")
                with col2:
                    proj_lang = st.selectbox("Content Language", ["hi", "en", "hi+en"], 
                                             format_func=lambda x: {"hi": "हिन्दी", "en": "English", "hi+en": "Hinglish"}[x])
                    budget = st.number_input("Monthly Budget (₹)", min_value=0, value=0, step=500)
                
                if st.form_submit_button("✅ Create Project", use_container_width=True):
                    if proj_name:
                        create_project(client['id'], proj_name, proj_location, proj_lang)
                        st.success(f"✅ Project '{proj_name}' created!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Project name required!")
        
        st.markdown("<hr style='opacity: 0.1;'>", unsafe_allow_html=True)
