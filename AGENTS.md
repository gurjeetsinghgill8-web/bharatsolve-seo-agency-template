# BHARATSOLVE SEO AGENCY — AI Memory File

## App Identity
- **Name**: BHARATSOLVE SEO AGENCY v1.0
- **Client**: Dr. Gurjeet Singh Gill — Gill Heart Clinic, Mohiuddinpur, Meerut
- **Stack**: Python 3.11 + Streamlit + SQLite + Groq/Gemini LLM
- **Live URL**: https://bharatsolve-seo-agency-template-d7c7gtbuaxpkxkya3dsmcz.streamlit.app/
- **Website**: https://gurjeetsinghgill8-web.github.io/gill-heart-clinic/
- **GitHub Repo**: gurjeetsinghgill8-web/bharatsolve-seo-agency-template (app) | gurjeetsinghgill8-web/gill-heart-clinic (website)

## Architecture
```
app.py                          → Main entry, routing, sidebar nav, auth
ui/gill_clinic.py (107KB)       → Gill Clinic Command Center (main UI)
ui/auth.py                      → Login/Register
agents/*.py                     → Business logic (content, competitor, rank, reviews, etc.)
db/schema.py + operations.py    → SQLite (18 tables, 1 file)
utils/llm_client.py             → Multi-provider LLM: Groq → Gemini → DeepSeek fallback
harness/                        → Scheduler & Auto-Pilot
```

## Key Session State Variables (gill_clinic.py)
- `gc_project_id` — Auto-created Gill Clinic project ID
- `gc_staged_weekly_drafts` — Dict[int, dict] for 7-day planner
- `gc_last_blog`, `gc_blog_title`, `gc_blog_content`, `gc_review_mode` — Blog editor
- `my_competitors` — User's custom competitor list
- `show_full_plan_checkbox` — Persists 50+ search plan visibility

## CRITICAL: Streamlit Cloud Session Limitations
- **Sessions recycle after ~5-10 min inactivity** → ALL `st.session_state` is LOST
- **MUST persist any user-generated content to DB** (`content_pieces` table)
- DB is at `/tmp/seo_agency.db` on Cloud, `seo_agency.db` locally
- Always reload from DB at function start as fallback for session state

## Bugs Fixed (Aug 2026)
1. **Language detection**: `"english" in "hinglish"` = True → Hinglish was treated as English
   - Fix: Check "hinglish" FIRST, then "hindi", then "english"
   - Files: `agents/content_agent.py`, `agents/github_publisher.py`
2. **Dual-language forced Hindi**: Prompt mandated Hindi+English in every article, ignoring user's language choice
   - Fix: Target-language-only mandate
3. **7-Day Planner resets to PENDING**: Drafts stored only in session_state, lost on Cloud recycle
   - Fix: Save drafts to DB as `content_type='weekly_planner'`, reload at function start
4. **Blog generator review mode lost**: Same session_state loss
   - Fix: Auto-restore last `status='draft'` blog from DB on page load
5. **View Full 50+ Plan disappeared**: `st.button` only True on click frame
   - Fix: Replaced with persistent `st.checkbox`
6. **Competitor shows ~8 not 62**: Used local `MY_COMPETITORS` with 16 blanks
   - Fix: Import 62 `DEFAULT_COMPETITORS` from `agents/competitor_agent.py`
7. **Blog Gen missing HTML download**: Only had PDF+WhatsApp+Telegram
   - Fix: Added `🌐 Save Web HTML File` via `utils/html_preview_generator`

## Language Handling
- 3 modes: Hinglish (हिंग्लिश), English, हिंदी
- Radio label: `["Hinglish (हिंग्लिश)", "English", "हिंदी"]`
- Mapping in `content_agent.py` → `target_lang_instruction`
- Same mapping in `github_publisher.py` → `lang_instruction`
- DB default: `target_language='hi'`

## Database: content_pieces Table
```sql
id, project_id, title, content_type, status, word_count,
target_keyword, meta_title, meta_description, schema_json,
content, published_url, created_at
```
- `content_type`: 'blog', 'weekly_planner', 'social_post', etc.
- `status`: 'draft', 'published', 'deleted'
- `save_content()` in `db/operations.py` auto-sets status based on `published_url`

## Key Functions
| Function | File | Purpose |
|----------|------|---------|
| `render_blog_section()` | gill_clinic.py:595 | 3-step blog generator + manager |
| `render_local_search_engine()` | gill_clinic.py:1417 | 7-day content planner |
| `render_competitor_section()` | gill_clinic.py:1245 | Competitor intel table |
| `show_gill_clinic()` | gill_clinic.py:1974 | Main orchestrator with quick-jump |
| `generate_content()` | content_agent.py:70 | AI content generation |
| `get_competitor_data()` | gill_clinic.py:384 | Load 62 competitors from agent |
| `save_content()` | operations.py:154 | Insert into content_pieces |

## Deployment
- Streamlit Cloud auto-deploys on `git push origin master`
- Requires `GEMINI_API_KEY` in Streamlit Secrets
- Optional: `GITHUB_TOKEN`, `GROQ_API_KEY`, `SMTP_USER/PASS`
