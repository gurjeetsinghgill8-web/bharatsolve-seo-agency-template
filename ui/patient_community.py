"""
BHARATSOLVE SEO AGENCY — Patient Community Page
GEO Community Feature: Real patient stories, Q&A, and health tips.
Builds topical authority and authentic UGC that AI search engines recognize.
"""
import streamlit as st

from db.operations import (
    create_community_post,
    get_community_posts,
    get_featured_community_posts,
    approve_community_post,
    like_community_post,
    delete_community_post,
    get_community_stats,
)


def show_patient_community():
    """Render the Patient Community page."""
    user_id = st.session_state["user_id"]

    # ── Page Header ──
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0 1rem;">
        <h1 style="background: linear-gradient(90deg, #00d2ff, #3a7bd5);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size: 2rem; margin: 0;">🫂 Heart Health Patient Community</h1>
        <p style="color: #888; font-size: 0.95rem; margin: 0.3rem 0;">
            Real Stories · Real Questions · Real Answers — Powered by Dr. Gurjeet Singh Gill
        </p>
        <p style="color: #0077b6; font-size: 0.8rem; margin: 0;">
            🏆 GEO Strategy: Authentic patient community content helps rank on ChatGPT, Gemini & Perplexity AI
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats Row ──
    stats = get_community_stats(user_id)
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #0077b6, #00b4d8); border-radius: 12px; 
                    padding: 0.8rem; text-align: center; color: white; box-shadow: 0 3px 12px rgba(0,119,182,0.15);">
            <div style="font-size: 1.5rem; font-weight: bold;">{stats['total_posts']}</div>
            <div style="font-size: 0.75rem; opacity: 0.9;">Total Posts</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #00b894, #00cec9); border-radius: 12px;
                    padding: 0.8rem; text-align: center; color: white; box-shadow: 0 3px 12px rgba(0,184,148,0.15);">
            <div style="font-size: 1.5rem; font-weight: bold;">{stats['approved']}</div>
            <div style="font-size: 0.75rem; opacity: 0.9;">Approved</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fdcb6e, #e17055); border-radius: 12px;
                    padding: 0.8rem; text-align: center; color: white; box-shadow: 0 3px 12px rgba(253,203,110,0.15);">
            <div style="font-size: 1.5rem; font-weight: bold;">{stats['featured']}</div>
            <div style="font-size: 0.75rem; opacity: 0.9;">⭐ Featured</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #e84393, #fd79a8); border-radius: 12px;
                    padding: 0.8rem; text-align: center; color: white; box-shadow: 0 3px 12px rgba(232,67,147,0.15);">
            <div style="font-size: 1.5rem; font-weight: bold;">{stats['total_engagement']}</div>
            <div style="font-size: 0.75rem; opacity: 0.9;">Total 👍 Likes</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌟 Patient Stories & Testimonials",
        "🩺 Ask Dr. Gill (Q&A)",
        "💚 Health Tips Wall",
        "⚙️ Manage Posts"
    ])

    # ════════════════════════════════════════════════════
    # TAB 1: Patient Stories & Testimonials
    # ════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 🌟 Real Patient Stories & Testimonials")
        st.markdown("*Real experiences from patients at Gill Heart Clinic, Mohiuddinpur, Meerut.*")

        # Featured stories grid
        featured_stories = get_featured_community_posts(user_id, limit=6)
        if featured_stories:
            cols = st.columns(2)
            for i, story in enumerate(featured_stories):
                col_idx = i % 2
                with cols[col_idx]:
                    story_type_icons = {
                        "testimonial": "💬",
                        "success_story": "🏆",
                        "question": "❓",
                        "health_tip": "💚",
                    }
                    icon = story_type_icons.get(story.get("post_type", "testimonial"), "💬")
                    reply_html = ""
                    if story.get("doctor_reply"):
                        reply_html = f"""
                        <div style="background:#f0f8ff; border-left:3px solid #0077b6; padding:0.6rem; 
                                    border-radius:6px; margin-top:0.5rem; font-size:0.85rem;">
                            <strong>🩺 Dr. Gill replied:</strong> {story['doctor_reply'][:300]}
                        </div>
                        """
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.8); border-radius: 10px; padding: 1rem;
                                border: 1px solid #90e0ef; box-shadow: 0 2px 8px rgba(0,119,182,0.06);
                                margin-bottom: 0.8rem;">
                        <div style="font-size:0.8rem; color:#888; margin-bottom:0.3rem;">
                            {icon} {story.get('post_type','testimonial').replace('_',' ').title()} · 
                            👍 {story.get('likes_count',0)} · 
                            {story.get('created_at','')[:10]}
                        </div>
                        <strong style="color:#0077b6;">{story.get('title','')[:120]}</strong>
                        <p style="color:#444; font-size:0.9rem; margin:0.4rem 0;">{story.get('content','')[:400]}</p>
                        <small style="color:#888;">— {story.get('author_name','Anonymous Patient')}</small>
                        {reply_html}
                    </div>
                    """, unsafe_allow_html=True)

            if st.button("👍 Like these stories", key="like_stories", use_container_width=True):
                for s in featured_stories:
                    like_community_post(s["id"])
                st.success("❤️ Thank you for your appreciation! Patients value your support.")
                st.rerun()
        else:
            st.info("🌟 No featured patient stories yet. Be the first to share your experience at Gill Heart Clinic!")

        # Submit testimonial form
        st.markdown("---")
        st.markdown("### ✍️ Share Your Story")
        with st.expander("📝 Submit Your Testimonial or Success Story", expanded=False):
            with st.form("submit_testimonial_form"):
                author = st.text_input("Your Name", placeholder="e.g., Rajesh Kumar")
                story_type = st.selectbox("Story Type", [
                    "testimonial", "success_story"
                ], format_func=lambda x: "💬 Testimonial" if x == "testimonial" else "🏆 Success Story")
                title = st.text_input("Title", placeholder="e.g., 'How Dr. Gill helped me control my BP in 3 months'")
                content = st.text_area("Your Story", height=120, 
                    placeholder="Share your experience at Gill Heart Clinic...\nWhat problem did you have? How did Dr. Gill help? How are you doing now?")
                submitted = st.form_submit_button("🌟 Submit My Story", use_container_width=True, type="primary")
                if submitted:
                    if not title or not content:
                        st.error("Please fill both title and your story.")
                    else:
                        create_community_post(
                            user_id=user_id,
                            author_name=author or "Anonymous Patient",
                            post_type=story_type,
                            title=title,
                            content=content
                        )
                        st.success("✅ Thank you for sharing! Your story will be reviewed by Dr. Gill before publishing.")
                        st.balloons()
                        st.rerun()

    # ════════════════════════════════════════════════════
    # TAB 2: Ask Dr. Gill (Q&A)
    # ════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 🩺 Ask Dr. Gill — Your Heart Health Questions Answered")
        st.markdown("*Ask any heart health question. Dr. Gurjeet Singh Gill will personally answer.*")

        # Submit question form
        with st.form("ask_drgill_form"):
            col_q1, col_q2 = st.columns([2, 1])
            with col_q1:
                question_title = st.text_input("Your Question", placeholder="e.g., 'Kya BP ki dawai zindagi bhar leni padti hai?'")
            with col_q2:
                question_author = st.text_input("Your Name (optional)", placeholder="e.g., Sunita ji")
            question_details = st.text_area("Additional Details", height=80,
                placeholder="Any specific details about your situation? (optional)")
            ask_submitted = st.form_submit_button("🩺 Ask Dr. Gill", use_container_width=True, type="primary")
            if ask_submitted:
                if not question_title:
                    st.error("Please enter your question.")
                else:
                    create_community_post(
                        user_id=user_id,
                        author_name=question_author or "Curious Patient",
                        post_type="question",
                        title=question_title,
                        content=question_details or question_title
                    )
                    st.success("✅ Question submitted! Dr. Gill will answer soon. Check back for the reply.")
                    st.rerun()

        # Answered questions
        st.markdown("---")
        st.markdown("### 📋 Answered Questions")
        answered = get_community_posts(user_id, post_type="question", status="approved")
        answered = [q for q in answered if q.get("doctor_reply")]
        if answered:
            for q in answered:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.8); border-radius: 10px; padding: 1rem;
                            border: 1px solid #90e0ef; box-shadow: 0 2px 8px rgba(0,119,182,0.06);
                            margin-bottom: 0.8rem;">
                    <div style="color:#888; font-size:0.8rem;">
                        ❓ Question · 👍 {q.get('likes_count',0)} · {q.get('created_at','')[:10]}
                    </div>
                    <strong style="color:#d90429;">Q: {q.get('title','')[:200]}</strong>
                    {f'<p style="color:#555;font-size:0.85rem;margin:0.2rem 0;">{q.get("content","")[:300]}</p>' if q.get("content","") != q.get("title","") else ""}
                    <div style="background:#f0f8ff; border-left:3px solid #0077b6; padding:0.7rem;
                                border-radius:6px; margin-top:0.5rem;">
                        <strong>🩺 Dr. Gill's Answer:</strong><br>
                        <span style="color:#333;">{q['doctor_reply'][:600]}</span>
                    </div>
                    <small style="color:#888;">— Asked by {q.get('author_name','Anonymous Patient')}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("❓ No answered questions yet. Ask the first question above!")

    # ════════════════════════════════════════════════════
    # TAB 3: Health Tips Wall
    # ════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 💚 Community Health Tips Wall")
        st.markdown("*Practical heart health tips shared by Dr. Gill and the community.*")

        # Submit tip form
        with st.form("submit_tip_form"):
            tip_text = st.text_area("Share a Heart Health Tip", height=80,
                placeholder="e.g., 'Roz 30 minute walk karne se BP control mein madad milti hai. Dr. Gill ke patient Rajesh ne ye routine follow kiya...'")
            tip_author = st.text_input("Your Name (optional)", key="tip_author")
            tip_submitted = st.form_submit_button("💚 Share Tip", use_container_width=True, type="primary")
            if tip_submitted:
                if not tip_text:
                    st.error("Please write a health tip.")
                else:
                    create_community_post(
                        user_id=user_id,
                        author_name=tip_author or "Health Conscious Member",
                        post_type="health_tip",
                        title=tip_text[:150] + ("..." if len(tip_text) > 150 else ""),
                        content=tip_text
                    )
                    st.success("💚 Tip shared! Thank you for contributing to community health awareness.")
                    st.rerun()

        # Tips wall
        tips = get_community_posts(user_id, post_type="health_tip", status="approved")
        if tips:
            cols_tip = st.columns(2)
            for i, tip in enumerate(tips):
                with cols_tip[i % 2]:
                    doctor_badge = ""
                    if tip.get("doctor_reply"):
                        doctor_badge = '<span style="background:#0077b6;color:white;padding:2px 8px;border-radius:8px;font-size:0.7rem;">✅ Doctor Approved</span>'
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.8); border-radius: 10px; padding: 0.9rem;
                                border: 1px solid #b8f2e6; box-shadow: 0 2px 8px rgba(0,184,148,0.06);
                                margin-bottom: 0.8rem;">
                        <div style="font-size:0.75rem;color:#888;margin-bottom:0.3rem;">
                            💚 Health Tip · 👍 {tip.get('likes_count',0)} · {tip.get('created_at','')[:10]}
                            {doctor_badge}
                        </div>
                        <p style="color:#333;font-size:0.9rem;margin:0.3rem 0;">{tip.get('content','')[:350]}</p>
                        <small style="color:#888;">— {tip.get('author_name','Anonymous')}</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("💚 No health tips published yet. Share the first tip above!")
            st.markdown("""
            <div style="background:#f0f8ff; border-radius:10px; padding:1rem; text-align:center; margin:1rem 0;">
                <p style="color:#0077b6;">💡 <strong>Did you know?</strong> Sharing community health tips creates authentic content that ChatGPT, Google Gemini, and AI search engines love to index and recommend!</p>
            </div>
            """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    # TAB 4: Manage Posts (Admin)
    # ════════════════════════════════════════════════════
    with tab4:
        st.markdown("### ⚙️ Manage Community Posts")
        st.markdown("*Approve, reply, feature, or delete patient submissions.*")

        # Pending posts first
        pending = get_community_posts(user_id, status="pending")
        st.markdown(f"#### ⏳ Pending Review ({len(pending)})")
        if pending:
            for p in pending:
                with st.expander(f"📝 {p.get('post_type','').replace('_',' ').title()}: {p.get('title','')[:100]}", expanded=False):
                    st.caption(f"By: {p.get('author_name','Anonymous')} | Type: {p.get('post_type','')} | {p.get('created_at','')}")
                    st.markdown(f"**Content:** {p.get('content','')[:500]}")
                    
                    col_a, col_r = st.columns([3, 1])
                    with col_a:
                        doctor_reply = st.text_area("Doctor's Reply", key=f"reply_{p['id']}", height=60,
                            placeholder="Write Dr. Gill's personal reply to this patient...")
                    
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                    with col_btn1:
                        if st.button("✅ Approve & Publish", key=f"approve_{p['id']}", use_container_width=True, type="primary"):
                            approve_community_post(p["id"], doctor_reply=doctor_reply, feature=False)
                            st.success("✅ Post approved and published!")
                            st.rerun()
                    with col_btn2:
                        if st.button("⭐ Approve & Feature", key=f"feature_{p['id']}", use_container_width=True):
                            approve_community_post(p["id"], doctor_reply=doctor_reply, feature=True)
                            st.success("⭐ Post approved and featured on community wall!")
                            st.rerun()
                    with col_btn3:
                        if st.button("🗑️ Delete", key=f"del_{p['id']}", use_container_width=True):
                            delete_community_post(p["id"])
                            st.warning("🗑️ Post deleted.")
                            st.rerun()
        else:
            st.success("🎉 No pending posts! All caught up.")

        # All approved posts
        st.markdown("---")
        st.markdown("#### ✅ Published Posts")
        all_posts = get_community_posts(user_id, status="approved")
        if all_posts:
            for p in all_posts:
                with st.expander(f"{'⭐' if p.get('is_featured') else '📄'} {p.get('post_type','').replace('_',' ').title()}: {p.get('title','')[:100]}", expanded=False):
                    st.caption(f"By: {p.get('author_name','Anonymous')} | 👍 {p.get('likes_count',0)} | {p.get('created_at','')}")
                    st.markdown(f"**Content:** {p.get('content','')[:400]}")
                    if p.get("doctor_reply"):
                        st.markdown(f"**🩺 Dr. Gill's Reply:** {p.get('doctor_reply','')[:400]}")
                    
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        if p.get("is_featured"):
                            if st.button("⬇️ Unfeature", key=f"unfeature_{p['id']}", use_container_width=True):
                                approve_community_post(p["id"], doctor_reply=p.get("doctor_reply",""), feature=False)
                                st.rerun()
                        else:
                            if st.button("⭐ Feature", key=f"feat_{p['id']}", use_container_width=True):
                                approve_community_post(p["id"], doctor_reply=p.get("doctor_reply",""), feature=True)
                                st.rerun()
                    with col_m2:
                        if st.button("🗑️ Delete", key=f"delpub_{p['id']}", use_container_width=True):
                            delete_community_post(p["id"])
                            st.warning("🗑️ Post deleted.")
                            st.rerun()
        else:
            st.info("No published posts yet.")
