"""
BHARATSOLVE SEO AGENCY — Dashboard UI
Main dashboard with stats, charts, and quick actions.
"""
import streamlit as st
import json
from datetime import datetime, timedelta
from db.operations import (
    get_dashboard_stats, get_clients, get_all_projects,
    get_agent_status_summary, get_agent_logs
)
from agents.manager_agent import get_manager_response


def show_dashboard():
    """Render the main dashboard with AI assistant."""
    user_id = st.session_state["user_id"]
    stats = get_dashboard_stats(user_id)
    clients = get_clients(user_id)
    agent_status = get_agent_status_summary()
    logs = get_agent_logs(limit=10)
    
    # ── Header ──
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="color: #0077b6; font-size: 2.5rem; margin: 0;">🚀 BHARATSOLVE DASHBOARD</h1>
        <p style="color: #555;">Your AI-Powered SEO Agency Control Center</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ── Stats Cards — Sky Blue Gradient Palette ──
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #0077b6, #00b4d8); 
                    border-radius: 15px; padding: 1.2rem; text-align: center;
                    box-shadow: 0 4px 15px rgba(0,119,182,0.2);">
            <h3 style="color: white; margin: 0; font-size: 2rem;">{stats['active_clients']}</h3>
            <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 1rem;">👥 Active Clients</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #0096c7, #48cae4); 
                    border-radius: 15px; padding: 1.2rem; text-align: center;
                    box-shadow: 0 4px 15px rgba(0,150,199,0.2);">
            <h3 style="color: white; margin: 0; font-size: 2rem;">{stats['total_keywords']}</h3>
            <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 1rem;">🔑 Keywords Tracked</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_rank = stats['avg_rank'] or 'N/A'
        rank_color = "#0077b6" if isinstance(avg_rank, (int, float)) and avg_rank <= 10 else \
                     "#ff9f1c" if isinstance(avg_rank, (int, float)) and avg_rank <= 30 else "#e63946"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #00b4d8, #90e0ef); 
                    border-radius: 15px; padding: 1.2rem; text-align: center;
                    box-shadow: 0 4px 15px rgba(0,180,216,0.2);">
            <h3 style="color: {rank_color}; margin: 0; font-size: 2rem;">{avg_rank}</h3>
            <p style="color: #333; margin: 0; font-size: 1rem;">📊 Avg. Rank</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #48cae4, #ade8f4); 
                    border-radius: 15px; padding: 1.2rem; text-align: center;
                    box-shadow: 0 4px 15px rgba(72,202,228,0.2);">
            <h3 style="color: #0077b6; margin: 0; font-size: 2rem;">{stats['total_content']}</h3>
            <p style="color: #333; margin: 0; font-size: 1rem;">📝 Content Pieces</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ── Main Content ──
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        st.markdown("### 🤖 AI Assistant - Agent Manager")
        
        # Chat interface
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Namaste! 👋 Main aapka SEO Manager Agent hoon. Aapko kya help chahiye?\n\nमैं ये कर सकता हूँ:\n• 📈 Rankings check कर सकता हूँ\n• 🔑 नए keywords suggest कर सकता हूँ\n• 📝 Content generate कर सकता हूँ\n• 📱 Social posts create कर सकता हूँ\n• 📊 Reports generate कर सकता हूँ"}
            ]
        
        # Show chat
        chat_container = st.container(height=350)
        with chat_container:
            for msg in st.session_state.chat_history:
                if msg['role'] == 'user':
                    st.markdown(f"""
                    <div style="text-align: right; margin: 0.5rem 0;">
                        <span style="background: linear-gradient(135deg, #0077b6, #00b4d8); color: white; padding: 0.5rem 1rem; 
                                     border-radius: 15px 15px 0 15px; display: inline-block; max-width: 80%;
                                     box-shadow: 0 2px 8px rgba(0,119,182,0.15);">
                            {msg['content']}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align: left; margin: 0.5rem 0;">
                        <span style="background: rgba(255,255,255,0.85); color: #333; padding: 0.5rem 1rem; 
                                     border-radius: 15px 15px 15px 0; display: inline-block; max-width: 80%;
                                     border: 1px solid #90e0ef; box-shadow: 0 2px 8px rgba(0,119,182,0.08);">
                            🤖 {msg['content']}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        user_input = st.chat_input("Ask me anything about your SEO...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            with st.spinner("🤔 Thinking..."):
                result = get_manager_response(user_input, user_id)
                response = result['response']
            
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col_right:
        st.markdown("### 📊 Quick Overview")
        
        # Active clients list
        if clients:
            st.markdown("**👥 Recent Clients**")
            for client in clients[:5]:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.7); border-radius: 8px; padding: 0.5rem 1rem; margin: 0.3rem 0;
                            border: 1px solid #90e0ef;">
                    <strong style="color: #0077b6;">{client['name']}</strong>
                    <span style="color: #666; float: right;">{client.get('business_type', 'General')}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👆 No clients yet. Add your first client!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Agent Status
        st.markdown("**🤖 Agent Health**")
        if agent_status:
            for agent in agent_status[:5]:
                status_icon = "✅" if agent['status'] == 'ok' else "❌"
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.7); border-radius: 5px; padding: 0.3rem 0.8rem; margin: 0.2rem 0; font-size: 0.9rem; border: 1px solid #90e0ef;">
                    {status_icon} <strong style="color: #0077b6;">{agent['agent_name']}</strong>
                    <span style="color: #666; float: right;">{agent.get('response_time_ms', 0)}ms</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Agents haven't run yet")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Recent activity
        st.markdown("**📋 Recent Activity**")
        if logs:
            for log in logs[:5]:
                time_ago = datetime.fromisoformat(log['logged_at']) if 'T' in log['logged_at'] else datetime.now()
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.5); border-radius: 5px; padding: 0.3rem 0.8rem; margin: 0.2rem 0; font-size: 0.8rem; border: 1px solid #e0f0ff;">
                    <strong style="color: #0077b6;">{log['agent_name']}</strong>: {log['task'][:50]}...
                    <span style="color: #666; float: right;">{log['status']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No activity yet")
