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

## Website SEO Fixes (Aug 2026)
- **Website source**: `C:\Users\pc\Desktop\gurjas ai\Dr G S GILL WEBSITE\index.html` (5,864 lines, single-page site)
- **Live**: https://gurjeetsinghgill8-web.github.io/gill-heart-clinic/
- **GitHub Repo**: gurjeetsinghgill8-web/gill-heart-clinic

### Fixes Applied (2026-08-02)
1. **H1 optimized**: `"Dr. Gurjeet Singh Gill (Dr. GS Gill)"` → `"Best Heart Doctor in Meerut — Dr. Gurjeet Singh Gill | Gill Heart Clinic"`
   - Added location + keyword targeting for local cardiac searches
2. **Physician Schema added**: Individual doctor schema with credentials (MBBS, Diploma Cardiology, PGDCCP, AI IIT Kanpur), address, memberOf MedicalClinic
   - Enables Google Knowledge Panel for Dr. Gill as a verified medical entity
3. **FAQPage Schema expanded (10 FAQs)**: Added 5 English FAQs (diabetic checkup frequency, silent heart disease, ECG timing, ECG vs Echo, acidity vs heart attack) + 5 location/cost FAQs
   - Enables rich results with expandable Q&A in Google search (potential 20-50% CTR increase)
4. **Breadcrumb Schema added**: Basic breadcrumb list for page hierarchy
5. **Duplicate HTML ID fixed**: First gallery section `id="gallery"` → `id="facilities"` (second photo gallery keeps `id="gallery"`)
   - Was causing HTML validation error; nav `#gallery` now correctly points to photo gallery
6. **15+ Years Experience Consistency**: Updated all experience references across site bio, schema, and badges from 12+ to 15+ years
7. **English FAQ Accordion & Knowledge Hub**: Added interactive UI accordion + Cardiology Knowledge Hub cluster wheel linking diagnostic services, calculators, and booking
8. **Local Signal Landmarks**: Enriched address & footer text with NH-58 Corridor, Near Meerut South RRTS Station, Partapur Flyover, Sugar Mill Mohiuddinpur (Metro Pillar 1375)

### Existing Schemas (before fixes)
- MedicalClinic (name, address, geo, hours, founder)
- JobPosting × 3 (MBBS, BMS, BHMS doctors)

### Not Changed (already strong)
- Title tag, meta description, OG tags, canonical URL
- MedicalClinic schema, JobPosting schemas
- All blog content, services, about, testimonials, health tools, contact/map sections

## Website Source Map
| File | Purpose |
|------|---------|
| `index.html` | Main single-page clinic website (deployed) |
| `standalone.html` | Simpler alternate version |
| `index-dev.html` | Development copy |
| `manual.html` | Manual/guide page |

## Deployment
- Streamlit Cloud auto-deploys on `git push origin master`
- Requires `GEMINI_API_KEY` in Streamlit Secrets
- Optional: `GITHUB_TOKEN`, `GROQ_API_KEY`, `SMTP_USER/PASS`
