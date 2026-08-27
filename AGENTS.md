# BHARATSOLVE SEO AGENCY — AI Memory File

## App Identity
- **Name**: BHARATSOLVE SEO AGENCY v1.0
- **Client**: Dr. Gurjeet Singh Gill — Gill Heart Clinic, Mohiuddinpur, Meerut
- **Stack**: Python 3.11 + Streamlit + SQLite + Groq/Gemini LLM + GitHub Actions Cron
- **Live URL**: https://bharatsolve-seo-agency-template-d7c7gtbuaxpkxkya3dsmcz.streamlit.app/
- **Website**: https://gurjeetsinghgill8-web.github.io/gill-heart-clinic/
- **GitHub Repo**: gurjeetsinghgill8-web/bharatsolve-seo-agency-template (app) | gurjeetsinghgill8-web/gill-heart-clinic (website)

## Architecture
```
app.py                          → Main entry, routing, sidebar nav, auth, on-load cloud task checks
ui/gill_clinic.py (119KB)       → Gill Clinic Command Center (main UI, 1-Click Turbo, Telemetry Radar)
ui/auth.py                      → Login/Register
agents/*.py                     → Business logic (content, competitor, rank, reviews, gbp, etc.)
db/schema.py + operations.py    → SQLite (18 tables, 1 file)
utils/llm_client.py             → Multi-provider LLM: Groq → Gemini → DeepSeek fallback
utils/live_analytics_hub.py     → Live Multi-LLM Radar, SERP Timeline & Competitor Dominance Tower
harness/headless_runner.py      → Standalone autonomous engine for CLI, UI, and GitHub Actions
harness/scheduler.py            → Task scheduler & multi-mode runner
.github/workflows/auto_seo.yml  → 24/7 serverless cron (Runs daily at 9 AM & 6 PM IST)
```

## Key Session State Variables (gill_clinic.py)
- `gc_project_id` — Auto-created Gill Clinic project ID
- `gc_staged_weekly_drafts` — Dict[int, dict] for 7-day planner
- `gc_last_blog`, `gc_blog_title`, `gc_blog_content`, `gc_review_mode` — Blog editor
- `gc_quick_jump` — Section quick navigation
- `my_competitors` — User's custom competitor list
- `show_full_plan_checkbox` — Persists 50+ search plan visibility

## CRITICAL: Streamlit Cloud Session Limitations & Fix
- **Sessions recycle after ~5-10 min inactivity** → ALL `st.session_state` is LOST
- **MUST persist any user-generated content to DB** (`content_pieces` table)
- DB is at `/tmp/seo_agency.db` on Cloud, `seo_agency.db` locally
- Always reload from DB at function start as fallback for session state
- **24/7 Serverless Solution**: Headless runner (`harness/headless_runner.py`) triggered via GitHub Actions (`.github/workflows/auto_seo.yml`) operates completely independently of Streamlit Cloud sleep cycles.

## Major Upgrades & Bug Fixes

### Auto-Pilot Overhaul & Turbo Master-Run (18 Aug 2026)
1. **1-Click Dr. Gill AI Turbo Master-Run**:
   - Added 1-click execution engine in `ui/gill_clinic.py` and `harness/headless_runner.py`.
   - Automatically picks next unwritten high-intent query from 50+ local search queries -> Generates 100% NMC & GEO compliant article -> Pushes live to GitHub Pages (`blogs/slug.html`) -> Rebuilds master blog catalog (`blogs/index.html`), homepage (`index.html`), `sitemap.xml`, and `llms.txt`.
2. **Replaced All Hardcoded Fake Statuses with Live Telemetry**:
   - Eliminated static "2 hours ago" strings.
   - Built **Live Health Radar** showing real connection pills (Google Gemini LLM, Groq Llama LLM, GitHub API connection to `gurjeetsinghgill8-web/gill-heart-clinic`, and live website link).
   - Connected real SQLite agent execution logs (`get_agent_logs`).
3. **24/7 Serverless Autonomous Cron**:
   - Created `.github/workflows/auto_seo.yml` running twice daily (9:00 AM & 6:00 PM IST) on GitHub Actions.
   - Hooked `try_cloud_tasks()` into `app.py` on-load check.

### Earlier Fixes (Aug 2026)
1. **Language detection**: `"english" in "hinglish"` = True → Fixed: Check "hinglish" FIRST, then "hindi", then "english" in `content_agent.py` and `github_publisher.py`.
2. **Dual-language forced Hindi**: Fixed to target-language-only mandate.
3. **7-Day Planner resets to PENDING**: Persisted to SQLite DB with `content_type='weekly_planner'`.
4. **Blog generator review mode lost**: Auto-restores last `status='draft'` blog from DB on page load.
5. **View Full 50+ Plan disappeared**: Replaced button with persistent `st.checkbox`.
6. **Competitor shows ~8 not 62**: Imports 62 `DEFAULT_COMPETITORS` from `agents/competitor_agent.py`.
7. **Blog Gen missing HTML download**: Added `🌐 Save Web HTML File` via `utils/html_preview_generator`.

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
| `run_clinic_turbo_cycle()` | headless_runner.py:60 | 1-click end-to-end SEO pipeline |
| `render_autopilot_section()` | gill_clinic.py:1840 | Live telemetry + 1-Click Master Control |
| `render_blog_section()` | gill_clinic.py:620 | 3-step blog generator + manager |
| `render_local_search_engine()` | gill_clinic.py:1417 | 7-day content planner & 50+ search queries |
| `render_competitor_section()` | gill_clinic.py:1245 | Competitor intel table |
| `show_gill_clinic()` | gill_clinic.py:2030 | Main orchestrator with quick-jump |
| `auto_blog_task()` | github_publisher.py:600 | AI content generation + Git Push |

## Website Source Map & Schemas
- **Website source**: `C:\Users\pc\Desktop\gurjas ai\Dr G S GILL WEBSITE\index.html` (5,864 lines, single-page site)
- **Live**: https://gurjeetsinghgill8-web.github.io/gill-heart-clinic/
- **GitHub Repo**: gurjeetsinghgill8-web/gill-heart-clinic
- **Schemas**: Physician, MedicalClinic, FAQPage (10 FAQs), BreadcrumbList, JobPosting × 3
- **Compliance**: 100% NMC Registered Medical Practitioner Regulations (no superlatives like "Best/No. 1"), 15+ years experience verified.

## Deployment
- Streamlit Cloud auto-deploys on `git push origin master`
- Requires `GEMINI_API_KEY` in Streamlit Secrets
- Optional: `GITHUB_TOKEN`, `GROQ_API_KEY`, `SMTP_USER/PASS`

## Web PWA Dashboard (`web/`) — Security & Deploy (27 Aug 2026)
- **Keys are SERVER-ONLY.** The PWA never stores API keys in `localStorage`. All AI + GitHub actions go through the Netlify serverless function `netlify/functions/turbo-runner.js` (actions: `health`, `turbo_blog`, `review_reply`).
- **`netlify.toml` must keep `base = "."` + `publish = "web"` + `[functions] directory = "netlify/functions"`.** Setting `base = "web"` silently drops the function (Netlify would look in `web/netlify/functions`).
- **GitHub Pages deploy** (`deploy_web.yml`) uses `configure-pages` with `enablement: true` to auto-enable Pages; it serves only the static preview (backend shows OFFLINE). Netlify is the full experience.
- **No fabricated "live" metrics.** Citation %, Maps rank, and review data must be real or clearly labeled as estimates/samples (NMC compliance — no "Best"/"No. 1"/"#1 Rank").
- Canonical clinic facts live in `../Dr G S GILL WEBSITE/DOCTOR_CONFIG.txt` (15+ yrs, 50,000+ patients, 25,000+ ECGs, Sugar Mill Mohiuddinpur Meerut 250205, maps.app.goo.gl/SqhL69uBkRvEeRhD8).
