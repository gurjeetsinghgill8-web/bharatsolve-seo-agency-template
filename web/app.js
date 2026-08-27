/**
 * GILL HEART CLINIC — SEO COMMAND CENTER (MOBILE & WEB ENGINE)
 * Dr. Gurjeet Singh Gill | Meerut & Delhi NCR
 *
 * SECURITY NOTE: No API keys are stored in the browser. All AI generation
 * and GitHub publishing run through the secure Netlify serverless backend
 * (/.netlify/functions/turbo-runner), where keys live as server-side env vars.
 */

// ═══════════════════════════════════════════════════════════════════
// 1. DATA CONSTANTS & CLINIC PROFILE (canonical — DOCTOR_CONFIG.txt)
// ═══════════════════════════════════════════════════════════════════
const CLINIC = {
  name: "Gill Heart Clinic",
  doctor: "Dr. Gurjeet Singh Gill",
  title: "Cardiac Physician",
  qualifications: "MBBS, Diploma Cardiology (UN Mehta), PGDCCP, AI in Healthcare (IIT Kanpur)",
  specialty: "Non-Invasive Cardiology & Preventive Heart Care",
  tagline: "Ethical, affordable, evidence-based cardiac care — Meerut & Delhi NCR",
  address: "Sugar Mill, Mohiuddinpur, Meerut 250205, Uttar Pradesh",
  phone: "+91-9258879884",
  email: "gurjeetsinghgill8@gmail.com",
  website: "https://gurjeetsinghgill8-web.github.io/gill-heart-clinic/",
  github_repo: "gurjeetsinghgill8-web/gill-heart-clinic",
  google_maps: "https://maps.app.goo.gl/SqhL69uBkRvEeRhD8",
  rating: 4.8,
  reviews: 127,
  experience_years: "15+",
  patients: "50,000+",
  ecgs: "25,000+"
};

const DEFAULT_QUERIES = [
  "heart doctor near me",
  "Cardiac Physician in Meerut",
  "experienced heart doctor Meerut",
  "heart doctor near me open now",
  "Dr. Gurjeet Singh Gill Cardiac Physician",
  "Gill Heart Clinic Meerut appointment",
  "heart doctor emergency Meerut",
  "BP checkup Mohiuddinpur Meerut",
  "chest pain treatment Mohiuddinpur",
  "ECG test near me Mohiuddinpur",
  "cholesterol treatment Meerut",
  "preventive heart checkup Meerut",
  "heart clinic near Delhi Meerut expressway",
  "heart clinic Modinagar",
  "hypertension specialist Meerut",
  "high blood pressure diet plan Hindi",
  "heart attack warning signs Hindi",
  "2D Echo test cost Meerut"
];

// Estimated competitor data (from agents/competitor_agent.py DEFAULT_COMPETITORS).
// Values are PUBLIC-DIRECTORY ESTIMATES, not verified claims.
const COMPETITORS = [
  { name: "Dr. Varad Gupta", hospital: "Metro Hospital and Heart Institute, Jawahar Nagar", location: "Meerut", exp: 40, reviews: 200, rating: 4.7 },
  { name: "Dr. Sanjeev Saxena", hospital: "Metro Hospital and Heart Institute, Jawahar Nagar", location: "Meerut", exp: 36, reviews: 180, rating: 4.6 },
  { name: "Dr. Hariraj Singh Tomar", hospital: "Nutema Hospital", location: "Meerut", exp: 28, reviews: 160, rating: 4.7 },
  { name: "Dr. Hariom Tyagi", hospital: "Lokpriya Hospital", location: "Meerut", exp: 26, reviews: 150, rating: 4.7 },
  { name: "Dr. Sajal Gupta", hospital: "Multi-Speciality Centers / Meerut Network", location: "Meerut", exp: 22, reviews: 140, rating: 4.6 },
  { name: "Dr. Md. Talha Khan Abid", hospital: "KMC Hospital, Malyana", location: "Meerut", exp: 20, reviews: 130, rating: 4.7 },
  { name: "Dr. Sanjeev Kumar Bansal", hospital: "Lokpriya Hospital", location: "Meerut", exp: 20, reviews: 120, rating: 4.7 },
  { name: "Dr. Rakesh Morya", hospital: "Jaswant Rai Speciality Hospital, Mansarovar Colony", location: "Meerut", exp: 18, reviews: 110, rating: 4.7 },
  { name: "Dr. Abhinav Rastogi", hospital: "Apusnova Hospital, Mawana Road", location: "Meerut", exp: 15, reviews: 100, rating: 4.8 },
  { name: "Dr. Md. Talha Khan", hospital: "KMC Hospital, Malyana", location: "Meerut", exp: 15, reviews: 95, rating: 4.8 },
  { name: "Dr. Vishal Singh", hospital: "Apusnova Hospital", location: "Meerut", exp: 12, reviews: 80, rating: 4.5 },
  { name: "Dr. Amit Kumar Jain", hospital: "Sirohi Hospital", location: "Meerut", exp: 15, reviews: 70, rating: 4.4 },
  { name: "Dr. P. K. Jain", hospital: "Sirohi Hospital", location: "Meerut", exp: 25, reviews: 65, rating: 4.3 },
  { name: "Dr. Mamtesh Gupta", hospital: "Dhanvantri Jeevan Rekha Hospital", location: "Meerut", exp: 18, reviews: 60, rating: 4.4 },
  { name: "Dr. Deepak", hospital: "Chhatrapati Shivaji Subharti Hospital", location: "Meerut", exp: 10, reviews: 55, rating: 4.2 },
  { name: "Dr. Rajeev Agarwal", hospital: "Jaswant Rai Speciality Hospital", location: "Meerut", exp: 20, reviews: 75, rating: 4.5 },
  { name: "Dr. Chand Bhusan Pandey", hospital: "LLRM Medical College", location: "Meerut", exp: 30, reviews: 90, rating: 4.3 },
  { name: "Dr. Shashank Pandey", hospital: "LLRM Medical College", location: "Meerut", exp: 15, reviews: 50, rating: 4.2 },
  { name: "Dr. Dheeraj Kumar Sony", hospital: "LLRM Medical College", location: "Meerut", exp: 12, reviews: 45, rating: 4.1 },
  { name: "Dr. Deeraj Kumar Soni", hospital: "IIMT Life Line Hospital", location: "Meerut", exp: 10, reviews: 40, rating: 4.0 },
  { name: "Dr. Vineet Bansal", hospital: "Navjeevan Hospital", location: "Meerut", exp: 14, reviews: 55, rating: 4.3 },
  { name: "Dr. Amit", hospital: "Chhatrapati Shivaji Subharti Hospital", location: "Meerut", exp: 10, reviews: 35, rating: 4.0 },
  { name: "Dr. Prashant Bendre", hospital: "Metro Hospital and Heart Institute", location: "Meerut", exp: 18, reviews: 85, rating: 4.5 },
  { name: "Dr. Gyanendra Singh", hospital: "Metro Hospital and Heart Institute", location: "Meerut", exp: 22, reviews: 80, rating: 4.5 },
  { name: "Dr. Vijay Narain Tyagi", hospital: "Metro Hospital and Heart Institute", location: "Meerut", exp: 25, reviews: 75, rating: 4.4 },
  { name: "Dr. Jitendra Sharma", hospital: "Metro Hospital and Heart Institute", location: "Meerut", exp: 15, reviews: 60, rating: 4.3 },
  { name: "Dr. Harimohan Choudhary", hospital: "Lokpriya Hospital", location: "Meerut", exp: 16, reviews: 55, rating: 4.3 },
  { name: "Dr. Oshin Bhardwaj", hospital: "Lokpriya Hospital", location: "Meerut", exp: 10, reviews: 40, rating: 4.2 },
  { name: "Dr. Jagadish J.", hospital: "Lokpriya Hospital", location: "Meerut", exp: 12, reviews: 45, rating: 4.2 },
  { name: "Dr. Rajendra Kumar Agarwal", hospital: "Max Network / Regional Consultation", location: "Delhi NCR", exp: 30, reviews: 200, rating: 4.6 },
  { name: "Dr. Amit Goel", hospital: "Max Network / Regional Consultation", location: "Delhi NCR", exp: 22, reviews: 180, rating: 4.6 },
  { name: "Dr. C. P. Vashisht", hospital: "Max Network / Regional Consultation", location: "Delhi NCR", exp: 25, reviews: 160, rating: 4.5 },
  { name: "Dr. Rajiv Agarwal", hospital: "Associated Heart Care Centers", location: "Delhi NCR", exp: 28, reviews: 150, rating: 4.5 },
  { name: "Dr. Ripen Gupta", hospital: "Associated Heart Care Centers", location: "Delhi NCR", exp: 20, reviews: 140, rating: 4.5 },
  { name: "Dr. Rajeev Rathi", hospital: "Associated Heart Care Centers", location: "Delhi NCR", exp: 18, reviews: 120, rating: 4.4 },
  { name: "Dr. Sunil Kumar Agarwal", hospital: "Associated Heart Care Centers", location: "Delhi NCR", exp: 22, reviews: 110, rating: 4.4 },
  { name: "Dr. Vijay Kumar Chopra", hospital: "Associated Heart Care Centers", location: "Delhi NCR", exp: 25, reviews: 100, rating: 4.3 },
  { name: "Dr. Anupam Goel", hospital: "Associated Heart Care Centers", location: "Delhi NCR", exp: 15, reviews: 90, rating: 4.3 },
  { name: "Dr. Sumeet Sethi", hospital: "Associated Heart Care Centers", location: "Delhi NCR", exp: 12, reviews: 80, rating: 4.2 },
  { name: "Dr. Arif Mustaqueem", hospital: "Associated Heart Care Centers", location: "Delhi NCR", exp: 10, reviews: 70, rating: 4.2 },
  { name: "Dr. Alok Kumar", hospital: "Meerut Clinical Cardiac Services", location: "Meerut", exp: 12, reviews: 50, rating: 4.1 },
  { name: "Dr. Manish Singhal", hospital: "Shanti Gopal Heart Centre", location: "Meerut", exp: 15, reviews: 55, rating: 4.2 },
  { name: "Dr. Pankaj Jain", hospital: "Jain Heart & General Clinic", location: "Meerut", exp: 18, reviews: 60, rating: 4.3 },
  { name: "Dr. Vineet Sharma", hospital: "Subharti Medical College Cardiology", location: "Meerut", exp: 12, reviews: 45, rating: 4.1 },
  { name: "Dr. Anurag Mittal", hospital: "Mittal Heart Care Clinic", location: "Meerut", exp: 10, reviews: 40, rating: 4.0 },
  { name: "Dr. Ashish Kumar Gupta", hospital: "Garh Road Cardiac Practice", location: "Meerut", exp: 15, reviews: 50, rating: 4.2 },
  { name: "Dr. R. K. Sharma", hospital: "Meerut City Heart Bureau", location: "Meerut", exp: 20, reviews: 55, rating: 4.2 },
  { name: "Dr. Neeraj Rastogi", hospital: "Rastogi Nursing Home & Heart Clinic", location: "Meerut", exp: 12, reviews: 45, rating: 4.1 },
  { name: "Dr. Manoj Kumar", hospital: "Delhi Road Cardiac Unit", location: "Meerut", exp: 10, reviews: 35, rating: 4.0 },
  { name: "Dr. Sandeep Singhal", hospital: "Singhal Hospital & Heart Care", location: "Meerut", exp: 20, reviews: 65, rating: 4.3 },
  { name: "Dr. Deepak", hospital: "GT Road, Raj Chopra ke paas", location: "Modinagar", exp: 15, reviews: 45, rating: 4.2 },
  { name: "Dr. Shanky Jain", hospital: "Bank Colony", location: "Modinagar", exp: 10, reviews: 30, rating: 4.0 },
  { name: "Dr. Lokesh Kumar", hospital: "Raj Chaupala ke paas", location: "Modinagar", exp: 8, reviews: 25, rating: 3.9 },
  { name: "Dr. Mahesh Mittal", hospital: "KN Modi Complex, PNB ke paas", location: "Modinagar", exp: 12, reviews: 30, rating: 4.0 },
  { name: "Aarogyam Heart & General Hospital", hospital: "Bisokhar", location: "Modinagar", exp: 10, reviews: 40, rating: 4.1 },
  { name: "Dr. Praveen Kumar Agrawal", hospital: "Sarvodaya Hospital, Kavi Nagar Industrial Area", location: "Ghaziabad", exp: 20, reviews: 120, rating: 4.5 },
  { name: "Dr. Ankul Gupta", hospital: "Shastri Nagar", location: "Ghaziabad", exp: 12, reviews: 70, rating: 4.3 },
  { name: "Dr. Asit Khanna", hospital: "Shastri Nagar", location: "Ghaziabad", exp: 15, reviews: 65, rating: 4.2 },
  { name: "Dr. Hariom Singh", hospital: "Patna Mor", location: "Hapur", exp: 10, reviews: 30, rating: 4.0 },
  { name: "Dr. Anuj Mudgal", hospital: "Avas Vikas Railway Station Road, Sanjay Vihar", location: "Hapur", exp: 8, reviews: 35, rating: 4.1 },
  { name: "DEV NANDINI HOSPITAL", hospital: "Morepura, Navjyoti Colony", location: "Hapur", exp: 15, reviews: 80, rating: 4.2 },
  { name: "Atmos Hospital", hospital: "Meerut Road, near JD School, Sanjay Colony", location: "Hapur", exp: 12, reviews: 70, rating: 4.2 }
];

const SAMPLE_REVIEWS = [
  { name: "Sample Patient 1", rating: 5, text: "Doctor explained everything clearly and the ECG was done quickly. Very caring and honest approach.", reply: "धन्यवाद जी! 🙏 आपके कीमती feedback के लिए बहुत-बहुत शुक्रिया। हम हमेशा अपने patients की heart health के लिए committed हैं। ❤️" },
  { name: "Sample Patient 2", rating: 4, text: "Good consultation and affordable treatment. Waiting time could be improved.", reply: "Thank you for your honest feedback. We've noted your suggestion and will improve. Your heart health is our priority! ❤️" }
];

// ═══════════════════════════════════════════════════════════════════
// 2. STATE & STORAGE (no secrets — only non-sensitive UI data)
// ═══════════════════════════════════════════════════════════════════
let state = {
  publishedBlogs: JSON.parse(localStorage.getItem('GILL_PUBLISHED_BLOGS') || '[]'),
  logs: JSON.parse(localStorage.getItem('GILL_LOGS') || '[]'),
  health: null
};

const API_BASE = '/.netlify/functions/turbo-runner';

function addLog(msg) {
  const time = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const entry = `[${time}] ${msg}`;
  state.logs.unshift(entry);
  if (state.logs.length > 40) state.logs.pop();
  localStorage.setItem('GILL_LOGS', JSON.stringify(state.logs));
  renderLogs();
}

function renderLogs() {
  const logBox = document.getElementById('log-box');
  if (!logBox) return;
  if (state.logs.length === 0) {
    logBox.innerHTML = `<div class="log-entry" style="color: #94a3b8;">🌱 Ready. Run the 1-Click Turbo Engine or generate a review reply to view live logs!</div>`;
    return;
  }
  logBox.innerHTML = state.logs.map(l => `<div class="log-entry">● ${l}</div>`).join('');
}

// ═══════════════════════════════════════════════════════════════════
// 3. SECURE BACKEND CLIENT (no API keys ever in the browser)
// ═══════════════════════════════════════════════════════════════════
async function callBackend(payload) {
  try {
    const res = await fetch(API_BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      addLog(`⚠️ Backend responded with status ${res.status}`);
      return null;
    }
    return await res.json();
  } catch (e) {
    // Backend offline (e.g. running locally or on GitHub Pages without Netlify)
    return null;
  }
}

async function checkHealth(showLog = false) {
  const data = await callBackend({ action: 'health' });
  if (data && data.success) {
    state.health = data;
  } else {
    state.health = { backend: 'offline', gemini: false, groq: false, github: false, offline: true };
  }
  renderHealth();
  if (showLog) {
    addLog(state.health.offline
      ? '📡 Secure backend is offline (expected on local preview / GitHub Pages). Deploy to Netlify for full AI publishing.'
      : '✅ Secure backend connected. Connection status refreshed.');
  }
  return state.health;
}

// ═══════════════════════════════════════════════════════════════════
// 4. 1-CLICK TURBO MASTER-RUN (serverless — keys hidden on server)
// ═══════════════════════════════════════════════════════════════════
async function runTurboCycle() {
  const btn = document.getElementById('turbo-btn');
  const querySelect = document.getElementById('turbo-query');
  const langSelect = document.getElementById('turbo-lang');

  const query = querySelect.value || DEFAULT_QUERIES[0];
  const lang = langSelect.value || "Hinglish";

  btn.disabled = true;
  btn.innerHTML = `<span>⏳ Running Secure Serverless AI Engine…</span>`;
  addLog(`⚡ Starting 1-Click Dr. Gill AI Turbo Master-Run for: "${query}" (${lang})`);

  try {
    const serverRes = await callBackend({ query, lang, action: 'turbo_blog' });

    if (serverRes && serverRes.success) {
      const newBlog = {
        title: serverRes.title,
        query: query,
        date: new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }),
        url: serverRes.url,
        isLive: serverRes.isLive
      };
      state.publishedBlogs.unshift(newBlog);
      localStorage.setItem('GILL_PUBLISHED_BLOGS', JSON.stringify(state.publishedBlogs));
      renderPublishedBlogs();

      if (serverRes.isLive) {
        addLog(`🚀 Published live to GitHub Pages: ${serverRes.url}`);
        const rb = serverRes.rebuild;
        if (rb && rb.summary) {
          addLog(`📚 Site rebuilt — ${rb.summary.articles} articles in catalog · homepage · sitemap.xml · llms.txt · robots.txt updated.`);
        }
        const rbMsg = (rb && rb.summary)
          ? `\n\n📚 Full site rebuilt:\n• Master catalog: ${rb.summary.articles} articles\n• Homepage articles section\n• sitemap.xml\n• llms.txt + llms-full.txt\n• robots.txt`
          : '';
        alert(`🎉 Success! Article for "${query}" is now LIVE on GitHub Pages.${rbMsg}`);
      } else {
        addLog(`📝 Article generated, but NOT published. ${serverRes.note || 'GITHUB_TOKEN missing on server.'}`);
        alert(`📝 Article generated but not published. ${serverRes.note || 'Set GITHUB_TOKEN in Netlify env vars to enable live publishing.'}`);
      }
      return;
    }

    // Backend offline → honest local preview (no fake "live" publish)
    addLog(`🔌 Secure backend offline. Building a local offline preview instead (no publish).`);
    const preview = generateOfflineMedicalArticle(query, lang);
    downloadHtml(preview.title, preview.html);
    addLog(`✅ Offline preview generated and downloaded locally.`);
    alert(`🔌 Secure backend is offline, so no live publish happened.\n\nI generated an offline preview and downloaded it as an HTML file instead.\n\nTo enable AI + live publishing, deploy this dashboard to Netlify (see ⚙️ Setup).`);

  } catch (err) {
    addLog(`❌ Turbo run error: ${err.message}`);
    alert(`Error: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>⚡ Run 1-Click Turbo Master-Run Now</span>`;
  }
}

function generateOfflineMedicalArticle(query, lang) {
  const title = `${query} — Dr. Gurjeet Singh Gill | Gill Heart Clinic Meerut`;
  const body = `<h1>${title}</h1>
<p><strong>Dr. Gurjeet Singh Gill</strong> (MBBS, Diploma Cardiology UN Mehta, PGDCCP, AI in Healthcare IIT Kanpur)<br>
Gill Heart Clinic, Sugar Mill, Mohiuddinpur, Meerut 250205</p>
<hr>
<h2>Introduction & Heart Health Overview</h2>
<p>Preventive cardiology is essential for every individual across Meerut and Delhi NCR. When experiencing symptoms or planning routine cardiovascular wellness, timely assessment by an experienced cardiac physician is crucial.</p>
<h2>Key Warning Signs You Must Not Ignore</h2>
<ol>
<li><strong>Chest Discomfort or Pressure</strong> — radiating pain to jaw, neck, back, or left arm.</li>
<li><strong>Breathlessness</strong> — shortness of breath during exertion or resting.</li>
<li><strong>Palpitations & Irregular Pulse</strong> — rapid or fluttery heartbeats.</li>
<li><strong>Unexplained Fatigue & Swelling in Feet</strong> — potential indicators of circulatory strain.</li>
</ol>
<h2>Diagnostic & Preventive Checkups at Gill Heart Clinic</h2>
<ul>
<li>Comprehensive 12-Lead Diagnostic ECG</li>
<li>2D Echo & Blood Pressure / Hypertension Profiling</li>
<li>Lifestyle, Diet & Non-Invasive Cardiac Counseling</li>
</ul>
<h2>When to Seek Medical Consultation</h2>
<p>If symptoms persist or worsen, book a consultation at <strong>Gill Heart Clinic, Sugar Mill, Mohiuddinpur, Meerut</strong>. Call <a href="tel:+919258879884">+91-9258879884</a>.</p>`;
  return {
    title,
    html: `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>${title}</title><style>body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.7;max-width:800px;margin:0 auto;padding:20px;color:#1e293b}</style></head><body>${body}</body></html>`
  };
}

function downloadHtml(title, htmlContent) {
  const blob = new Blob([htmlContent], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') + '.html';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ═══════════════════════════════════════════════════════════════════
// 5. UI RENDERING
// ═══════════════════════════════════════════════════════════════════
function pillHtml(label, ok) {
  const color = ok ? '#10b981' : '#ef4444';
  return `<span class="status-pill" style="background: rgba(255,255,255,0.12);">
    <span class="status-dot" style="background:${color}; box-shadow:0 0 8px ${color};"></span> ${label}
  </span>`;
}

function renderHealth() {
  const h = state.health;
  if (!h) return;

  const offline = !!h.offline;

  // Turbo hero pills
  const pills = document.getElementById('turbo-pills');
  if (pills) {
    pills.innerHTML = [
      pillHtml(`🔐 Secure Backend: ${offline ? 'OFFLINE' : 'CONNECTED'}`, !offline),
      pillHtml(`🤖 Gemini: ${h.gemini ? 'READY' : 'NOT SET'}`, !!h.gemini),
      pillHtml(`🧠 DeepSeek: ${h.deepseek ? 'READY' : 'NOT SET'}`, !!h.deepseek),
      pillHtml(`⚡ Groq: ${h.groq ? 'READY' : 'NOT SET'}`, !!h.groq),
      pillHtml(`🐙 GitHub Pages: ${h.github ? 'CONNECTED' : 'NOT SET'}`, !!h.github)
    ].join('');
  }

  // System status section
  const list = document.getElementById('engine-status-list');
  if (list) {
    const rows = [
      { label: 'Secure Serverless Backend', sub: offline ? 'Not reachable — deploy to Netlify' : 'Connected & serving requests', ok: !offline },
      { label: 'DeepSeek Chat', sub: h.deepseek ? 'Primary AI configured' : 'No key on server (fallback content used)', ok: !!h.deepseek },
      { label: 'Google Gemini AI', sub: h.gemini ? 'API key configured' : 'No key on server (optional)', ok: !!h.gemini },
      { label: 'Groq Llama-3', sub: h.groq ? 'Optional fallback configured' : 'No fallback key (optional)', ok: !!h.groq },
      { label: 'GitHub Pages Publishing', sub: h.github ? 'Direct publish enabled' : 'No GITHUB_TOKEN (articles save as preview only)', ok: !!h.github }
    ];
    list.innerHTML = rows.map(r => `
      <div class="llm-bar-card" style="display:flex; justify-content:space-between; align-items:center; gap:0.6rem;">
        <div>
          <b>${r.label}</b><br>
          <span style="font-size:0.75rem; color: var(--text-muted);">${r.sub}</span>
        </div>
        <span class="status-dot" style="background:${r.ok ? '#10b981' : '#ef4444'}; box-shadow:0 0 8px ${r.ok ? '#10b981' : '#ef4444'};"></span>
      </div>
    `).join('');
  }

  // Modal status list
  const modal = document.getElementById('modal-status-list');
  if (modal) {
    modal.innerHTML = (offline
      ? `<div style="color:#b91c1c; font-weight:700;">🔌 Secure backend not reachable from this URL.</div>`
      : `<div style="color:#166534; font-weight:700;">✅ Secure backend connected.</div>`);
  }
}

function renderPublishedBlogs() {
  const container = document.getElementById('published-blogs-list');
  const countBadge = document.getElementById('blog-count-badge');
  if (!container) return;

  if (countBadge) countBadge.innerText = `${state.publishedBlogs.length} Published`;

  if (state.publishedBlogs.length === 0) {
    container.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 1.5rem;">📝 No articles generated on this device yet. Click 'Run 1-Click Turbo' above to publish your first live article!</div>`;
    return;
  }

  container.innerHTML = state.publishedBlogs.map((b, idx) => `
    <div class="review-item" style="border-left: 4px solid var(--primary);">
      <div class="review-header">
        <span class="reviewer-name">#${idx + 1} — ${b.title}</span>
        <span class="review-time">${b.date}</span>
      </div>
      <div style="margin-top: 0.4rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
        ${b.isLive ? `<a href="${b.url}" target="_blank" class="btn btn-sm btn-primary">🌐 View Live Article →</a>` : `<span class="btn btn-sm btn-secondary" style="cursor: default;">📝 Preview Only</span>`}
        <span class="status-pill"><span class="status-dot"></span> ${b.isLive ? 'Live on GitHub Pages' : 'Not Published'}</span>
      </div>
    </div>
  `).join('');
}

function renderCompetitors() {
  const tbody = document.getElementById('competitors-tbody');
  const badge = document.getElementById('competitor-count-badge');
  if (!tbody) return;

  if (badge) badge.innerText = `${COMPETITORS.length} Tracked`;

  // "You" row (clinic's own verified stats) + tracked competitors
  const youRow = `
    <tr class="highlight-row">
      <td><b>${CLINIC.doctor}</b><br><span style="font-size:0.72rem; color:#0369a1;">${CLINIC.name} — You</span></td>
      <td>Mohiuddinpur, Meerut</td>
      <td><b>${CLINIC.experience_years}</b></td>
      <td><b>${CLINIC.reviews}</b></td>
      <td><b>${CLINIC.rating}★</b></td>
    </tr>`;

  const rows = COMPETITORS.map(c => `
    <tr>
      <td>${c.name}<br><span style="font-size:0.72rem; color: var(--text-muted);">${c.hospital}</span></td>
      <td>${c.location}</td>
      <td>${c.exp}</td>
      <td>~${c.reviews}</td>
      <td>${c.rating}★</td>
    </tr>
  `).join('');

  tbody.innerHTML = youRow + rows;
}

function renderReviews() {
  const container = document.getElementById('reviews-list');
  if (!container) return;
  container.innerHTML = SAMPLE_REVIEWS.map(r => `
    <div class="review-item">
      <div class="review-header">
        <span class="reviewer-name">${r.name}</span>
        <span class="review-time">Sample</span>
      </div>
      <div class="stars">${'★'.repeat(r.rating)}${'☆'.repeat(5 - r.rating)}</div>
      <div class="review-text">"${r.text}"</div>
      <div class="ai-reply-box">
        <b>🤖 AI Reply:</b> ${r.reply}
      </div>
    </div>
  `).join('');
}

async function generateReviewReply() {
  const input = document.getElementById('review-input');
  const output = document.getElementById('review-reply-output');
  const reviewText = (input.value || '').trim();

  if (!reviewText) {
    output.innerHTML = `<div style="color:#b91c1c;">Please paste a review first.</div>`;
    return;
  }

  output.innerHTML = `<div style="color: var(--text-muted);">⏳ Generating compliant AI reply…</div>`;

  const res = await callBackend({ action: 'review_reply', reviewText });

  if (res && res.success) {
    output.innerHTML = `<div class="ai-reply-box" style="margin-top:0.5rem;"><b>🤖 AI Reply:</b> ${res.reply}</div>`;
    addLog(`💬 Generated AI reply for a patient review.`);
  } else {
    output.innerHTML = `<div style="color:#b45309;">🔌 Secure backend offline — cannot generate reply. Deploy to Netlify to enable AI replies.</div>`;
    addLog(`⚠️ Review reply failed: backend offline.`);
  }
}

// ═══════════════════════════════════════════════════════════════════
// 6. SETTINGS & PWA HANDLERS
// ═══════════════════════════════════════════════════════════════════
function openSettingsModal() {
  renderHealth();
  document.getElementById('settings-modal').classList.add('active');
}

function closeSettingsModal() {
  document.getElementById('settings-modal').classList.remove('active');
}

// PWA Install Prompt handling
let deferredInstallPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredInstallPrompt = e;
  const installBtn = document.getElementById('install-pwa-btn');
  if (installBtn) installBtn.style.display = 'inline-flex';
});

function triggerInstallPWA() {
  if (deferredInstallPrompt) {
    deferredInstallPrompt.prompt();
    deferredInstallPrompt.userChoice.then(() => {
      deferredInstallPrompt = null;
    });
  } else {
    alert("📲 To install this app on your phone:\n\n1. On iPhone/Safari: Tap Share → 'Add to Home Screen'\n2. On Android/Chrome: Tap 3 dots menu → 'Install App' / 'Add to Home screen'");
  }
}

// ═══════════════════════════════════════════════════════════════════
// 7. INITIALIZATION ON DOM READY
// ═══════════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  // Populate query dropdown
  const querySelect = document.getElementById('turbo-query');
  if (querySelect) {
    querySelect.innerHTML = DEFAULT_QUERIES.map(q => `<option value="${q}">${q}</option>`).join('');
  }

  // Render components
  renderCompetitors();
  renderReviews();
  renderPublishedBlogs();
  renderLogs();

  // Check live connection status
  checkHealth();

  // Register PWA service worker
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./sw.js').catch(err => console.log('SW register failed', err));
  }
});
