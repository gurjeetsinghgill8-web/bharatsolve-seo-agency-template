/**
 * 🔒 SECURE NETLIFY SERVERLESS BACKEND FUNCTION
 * Keeps all API keys (GEMINI_API_KEY, DEEPSEEK_API_KEY, GROQ_API_KEY, GITHUB_TOKEN)
 * hidden on the server! Zero keys are exposed to the browser or client.
 *
 * Actions:
 *   - "health"        → report which providers are configured (no key values leak)
 *   - "turbo_blog"    → generate + publish article, then REBUILD the whole site:
 *                       blogs/index.html (catalog) · index.html (homepage) ·
 *                       sitemap.xml · llms.txt · llms-full.txt · robots.txt
 *   - "review_reply"  → generate a warm Hinglish/English reply for a patient review
 */

const REPO = "gurjeetsinghgill8-web/gill-heart-clinic";
const BRANCH = "gh-pages"; // the clinic site is published from the gh-pages branch
const CLINIC_SITE = "https://gurjeetsinghgill8-web.github.io/gill-heart-clinic/";
const CLINIC_NAME = "Gill Heart Clinic";
const DOCTOR = "Dr. Gurjeet Singh Gill";
const ADDRESS = "Sugar Mill, Mohiuddinpur, Meerut, Uttar Pradesh 250205";
const PHONE = "+91-9258879884";

const CORS_HEADERS = {
  "Content-Type": "application/json",
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type"
};

function ok(body) {
  return { statusCode: 200, headers: CORS_HEADERS, body: JSON.stringify(body) };
}

function fail(statusCode, message) {
  return { statusCode, headers: CORS_HEADERS, body: JSON.stringify({ error: message }) };
}

exports.handler = async (event) => {
  if (event.httpMethod === "OPTIONS") {
    return { statusCode: 204, headers: CORS_HEADERS, body: "" };
  }
  if (event.httpMethod !== "POST") {
    return fail(405, "Method not allowed");
  }

  let body;
  try {
    body = JSON.parse(event.body);
  } catch (e) {
    return fail(400, "Invalid JSON body");
  }

  const { query, lang, action, reviewText, patientName } = body;

  // Server-side secrets (100% hidden from the browser)
  const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
  const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY;
  const GROQ_API_KEY = process.env.GROQ_API_KEY;
  const GITHUB_TOKEN = process.env.GITHUB_TOKEN;

  try {
    // ── ACTION: HEALTH CHECK ──
    if (action === "health") {
      return ok({
        success: true,
        backend: "secure-serverless",
        gemini: !!GEMINI_API_KEY,
        deepseek: !!DEEPSEEK_API_KEY,
        groq: !!GROQ_API_KEY,
        github: !!GITHUB_TOKEN
      });
    }

    // ── ACTION 1: REVIEW AUTO-REPLY ──
    if (action === "review_reply") {
      const review = (reviewText || "").trim();
      if (!review) return fail(400, "reviewText is required");

      const prompt = `Write a polite, warm, professional Hinglish reply to this patient Google review for ${DOCTOR} at ${CLINIC_NAME} Mohiuddinpur Meerut. Patient Name: ${patientName || "Patient"}, Review: "${review}". Thank them for trusting us with their heart health. Keep it 2-3 sentences. Do NOT use banned superlatives like 'Best' or 'No. 1'.`;

      let replyText = await geminiGenerate(prompt, GEMINI_API_KEY, 256);
      if (!replyText) replyText = await deepseekGenerate(prompt, DEEPSEEK_API_KEY, 256);
      if (!replyText) replyText = await groqGenerate(prompt, GROQ_API_KEY, 256);
      if (!replyText) {
        replyText = `धन्यवाद ${patientName || ""} जी! 🙏 आपके कीमती feedback के लिए बहुत-बहुत शुक्रिया। हम हमेशा अपने patients की heart health के लिए committed हैं। ❤️`;
      }
      return ok({ success: true, reply: replyText });
    }

    // ── ACTION 2: TURBO BLOG GENERATION + PUBLISH + FULL SITE REBUILD ──
    const targetQuery = query || "heart doctor near me";
    const targetLang = lang || "Hinglish";

    const prompt = `Write an authoritative, 100% NMC-compliant cardiology & heart health guide for ${DOCTOR} (MBBS, Diploma Cardiology UN Mehta, PGDCCP, AI in Healthcare IIT Kanpur) at ${CLINIC_NAME}, ${ADDRESS}. 
Target Query: "${targetQuery}". 
Language: ${targetLang}. 
Strict Guidelines: 
- 100% NMC Registered Medical Practitioner Regulations (do NOT use banned superlatives like 'Best' or 'No. 1').
- Detail diagnostic services: 12-Lead ECG, 2D Echo, Blood Pressure Profiling, Preventive Heart Counseling.
- Clinic details: ${ADDRESS} | Phone: ${PHONE}.
- Include structured sections: Symptoms & Warning Signs, Preventive Strategies, Diagnostic Importance, and FAQs.`;

    let markdown = await geminiGenerate(prompt, GEMINI_API_KEY, 2048);
    if (!markdown) markdown = await deepseekGenerate(prompt, DEEPSEEK_API_KEY, 2048);
    if (!markdown) markdown = await groqGenerate(prompt, GROQ_API_KEY, 2048);
    if (!markdown) {
      markdown = `## ${targetQuery} — Complete Patient Guide by ${DOCTOR}\n\nTimely cardiovascular assessment is vital for patients across Meerut and Delhi NCR. Visit ${CLINIC_NAME}, ${ADDRESS} for expert non-invasive cardiology care.`;
    }

    const slug = targetQuery.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
    const title = `${targetQuery} — ${DOCTOR} | ${CLINIC_NAME} Meerut`;

    const fullHtml = buildArticleHtml(title, markdown);

    // 1) Publish the article (server GITHUB_TOKEN — never the browser)
    let isPushedLive = false;
    let publishedUrl = "";
    if (GITHUB_TOKEN) {
      const result = await putFile(`blogs/${slug}.html`, fullHtml, `🤖 Serverless Auto-SEO: Publish article '${title}'`, GITHUB_TOKEN);
      isPushedLive = result.success;
      publishedUrl = result.success ? `${CLINIC_SITE}blogs/${slug}.html` : "";
    }

    // 2) Rebuild master catalog, homepage, sitemap, llms.txt, robots.txt
    let rebuild = null;
    if (isPushedLive && GITHUB_TOKEN) {
      rebuild = await rebuildWebsite(GITHUB_TOKEN);
    }

    return ok({
      success: true,
      title,
      query: targetQuery,
      url: publishedUrl || `#preview-${slug}`,
      isLive: isPushedLive,
      content: fullHtml,
      note: isPushedLive
        ? "Published live + full site (catalog, homepage, sitemap, llms.txt) rebuilt."
        : "Generated, but not published (GITHUB_TOKEN is not configured on the server).",
      rebuild
    });

  } catch (error) {
    console.error("turbo-runner error:", error);
    return fail(500, error.message);
  }
};

// ═══════════════════════════════════════════════════════════════════
// AI GENERATION HELPERS
// ═══════════════════════════════════════════════════════════════════

async function geminiGenerate(prompt, key, maxTokens) {
  if (!key) return "";
  try {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${key}`;
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { temperature: 0.7, maxOutputTokens: maxTokens }
      })
    });
    if (!res.ok) return "";
    const data = await res.json();
    return data.candidates?.[0]?.content?.parts?.[0]?.text || "";
  } catch (e) {
    console.error("Gemini call error", e);
    return "";
  }
}

async function deepseekGenerate(prompt, key, maxTokens) {
  if (!key) return "";
  try {
    const url = "https://api.deepseek.com/chat/completions";
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${key}`
      },
      body: JSON.stringify({
        model: "deepseek-chat",
        messages: [
          { role: "system", content: "You are an expert, NMC-compliant medical SEO copywriter for Dr. Gurjeet Singh Gill." },
          { role: "user", content: prompt }
        ],
        temperature: 0.7,
        max_tokens: maxTokens
      })
    });
    if (!res.ok) return "";
    const data = await res.json();
    return data.choices?.[0]?.message?.content || "";
  } catch (e) {
    console.error("DeepSeek call error", e);
    return "";
  }
}

async function groqGenerate(prompt, key, maxTokens) {
  if (!key) return "";
  try {
    const url = "https://api.groq.com/openai/v1/chat/completions";
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${key}`
      },
      body: JSON.stringify({
        model: "llama-3.1-8b-instant",
        messages: [
          { role: "system", content: "You are an expert, NMC-compliant medical SEO copywriter for Dr. Gurjeet Singh Gill." },
          { role: "user", content: prompt }
        ],
        temperature: 0.7,
        max_tokens: maxTokens
      })
    });
    if (!res.ok) return "";
    const data = await res.json();
    return data.choices?.[0]?.message?.content || "";
  } catch (e) {
    console.error("Groq call error", e);
    return "";
  }
}

// ═══════════════════════════════════════════════════════════════════
// GITHUB HELPERS (create/update any file + list blogs)
// ═══════════════════════════════════════════════════════════════════

async function putFile(path, content, message, token) {
  const url = `https://api.github.com/repos/${REPO}/contents/${path}`;
  const headers = {
    Authorization: `Bearer ${token}`,
    Accept: "application/vnd.github.v3+json"
  };
  try {
    // Get SHA if file exists (for update)
    let sha = null;
    const checkRes = await fetch(`${url}?ref=${BRANCH}`, { headers });
    if (checkRes.ok) {
      const data = await checkRes.json();
      sha = data.sha;
    }

    const commitRes = await fetch(url, {
      method: "PUT",
      headers: { ...headers, "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        content: Buffer.from(content, "utf-8").toString("base64"),
        branch: BRANCH,
        sha: sha || undefined
      })
    });

    if (commitRes.ok) {
      return { success: true, path };
    }
    const err = await commitRes.json().catch(() => ({}));
    return { success: false, path, error: err.message || `HTTP ${commitRes.status}` };
  } catch (e) {
    return { success: false, path, error: e.message };
  }
}

async function listBlogs(token) {
  const url = `https://api.github.com/repos/${REPO}/contents/blogs?ref=${BRANCH}`;
  const headers = { Authorization: `Bearer ${token}`, Accept: "application/vnd.github.v3+json" };
  try {
    const res = await fetch(url, { headers });
    if (!res.ok) return [];
    const files = await res.json();
    if (!Array.isArray(files)) return [];
    return files
      .filter((f) => f.name.endsWith(".html") && f.name !== "index.html")
      .map((f) => ({
        filename: f.name,
        slug: f.name.replace(".html", ""),
        title: f.name.replace(".html", "").replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
        url: `${CLINIC_SITE}blogs/${f.name}`
      }));
  } catch (e) {
    console.error("listBlogs error", e);
    return [];
  }
}

async function getFileContent(path, token) {
  const url = `https://api.github.com/repos/${REPO}/contents/${path}?ref=${BRANCH}`;
  const headers = { Authorization: `Bearer ${token}`, Accept: "application/vnd.github.v3+json" };
  const res = await fetch(url, { headers });
  if (!res.ok) return null;
  const data = await res.json();
  if (!data.content) return null;
  return Buffer.from(data.content, "base64").toString("utf-8");
}

// ═══════════════════════════════════════════════════════════════════
// REBUILD GENERATORS (catalog · homepage · sitemap · llms.txt · robots)
// ═══════════════════════════════════════════════════════════════════

function buildCatalogHtml(articles) {
  const cards = articles.map((a) => `
        <div style="background:#fff; border:1px solid #d4edff; border-radius:12px; padding:1.2rem; margin:1rem 0; box-shadow:0 2px 8px rgba(0,119,182,0.08);">
            <h3 style="color:#0077b6; margin:0 0 0.5rem;"><a href="${a.url}" style="color:#0077b6; text-decoration:none;">${a.title}</a></h3>
            <p style="color:#666; font-size:0.9rem; margin:0.3rem 0;">Expert heart health guide by ${DOCTOR}, Cardiac Physician.</p>
            <a href="${a.url}" style="display:inline-block; background:#0077b6; color:white; padding:0.4rem 1rem; border-radius:8px; text-decoration:none; font-weight:bold; font-size:0.85rem; margin-top:0.5rem;">Read Article →</a>
        </div>`).join("");

  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Heart Health Articles & Blogs | ${DOCTOR}</title>
    <meta name="description" content="NMC-compliant heart health articles and patient guides by ${DOCTOR} at ${CLINIC_NAME}, ${ADDRESS}.">
    <style>
        body { font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif; background:#f4f9fc; color:#333; line-height:1.6; margin:0; padding:20px; }
        .container { max-width:900px; margin:0 auto; background:white; padding:30px; border-radius:16px; box-shadow:0 4px 20px rgba(0,119,182,0.1); }
        h1 { color:#0077b6; border-bottom:2px solid #00b4d8; padding-bottom:10px; }
        .back-link { color:#0077b6; text-decoration:none; font-weight:bold; display:inline-block; margin-bottom:15px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="${CLINIC_SITE}" class="back-link">← Back to ${CLINIC_NAME} Website</a>
        <h1>🫀 Heart Health Articles & Patient Guides</h1>
        <p>Expert medical guidance written by <strong>${DOCTOR}</strong> (Cardiac Physician, ${ADDRESS}).</p>
        <div class="articles-grid">
            ${cards}
        </div>
    </div>
</body>
</html>`;
}

function buildSitemapXml(slugs) {
  let urls = `  <url>
    <loc>${CLINIC_SITE}</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>${CLINIC_SITE}blogs/index.html</loc>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>`;
  for (const s of slugs) {
    urls += `
  <url>
    <loc>${CLINIC_SITE}blogs/${s}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>`;
  }
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>`;
}

function buildRobotsTxt() {
  return `User-agent: *
Allow: /

# AI Engine Search Crawlers (Generative Engine Optimization - GEO)
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Bytespider
Allow: /

Sitemap: ${CLINIC_SITE}sitemap.xml
`;
}

function buildLlmsTxt(articles) {
  const blogLinks = articles.map((a) => `- ${a.title}: ${a.url}`).join("\n");
  return `# ${DOCTOR} — ${CLINIC_NAME}, Mohiuddinpur, Meerut 250205
# Cardiac Physician | Non-Invasive Cardiology | 15+ Years | 50,000+ Patients
# Website: ${CLINIC_SITE}

> ${DOCTOR} is a qualified Cardiac Physician (MBBS, Diploma Cardiology UN Mehta, PGDCCP, AI in Healthcare IIT Kanpur) providing comprehensive non-invasive cardiac care, hypertension management, chest pain evaluation, and preventive cardiology at ${CLINIC_NAME}, ${ADDRESS}.

## Doctor Profile
- Name: ${DOCTOR} (Dr. GS Gill)
- Title: Cardiac Physician & Non-Invasive Heart Care Specialist
- Experience: 15+ Years in Clinical Cardiology & Critical Care
- Patients Treated: 50,000+
- MBBS: Govt Medical College MPSMC
- Diploma in Cardiology: UN Mehta Institute of Cardiology, Ahmedabad
- PGDCCP (NI): Post Graduate Diploma in Clinical Cardiology & Critical Care
- AI in Healthcare: Certification from IIT Kanpur
- Associate Consultant: Yashoda Superspeciality Hospital, Ghaziabad
- Google Rating: 4.8★ (127+ Reviews)
- Phone: ${PHONE}

## Clinic Address & Hours
- ${CLINIC_NAME}
- ${ADDRESS}
- Near Metro Pillar No. 1375, 1.5 km from Meerut South RRTS Station
- Hours: 9:00 AM – 7:00 PM | All Days | By Appointment

## Service Cities & Catchment Areas
${DOCTOR} serves patients from Meerut, Modinagar, Ghaziabad, Hapur, and Delhi NCR, plus nearby areas (Mawana, Hastinapur, Sardhana, Daurala, Kharkhauda).

## Core Services
- Cardiac OPD Consultation & Clinical Assessment
- High Blood Pressure (Hypertension) Diagnosis & Management
- Chest Pain Evaluation & Early Cardiac Warning Signs
- Diabetes & Cardiovascular Risk Assessment
- Cholesterol & Lipid Disorder Management
- Heart Failure & Ischemic Heart Disease Management
- ECG, 2D Echo, TMT Interpretation & Referral Guidance
- Preventive Cardiology & Lifestyle Modification Counseling
- Indian Heart-Healthy Diet Planning & Exercise Guidance
- Generic Medicine Consultation (PM Jan Aushadhi Kendra)

## Published Heart Health Articles
${blogLinks}

## Important Disclaimers
- ${DOCTOR} is a CARDIAC PHYSICIAN specializing in non-invasive cardiology. He is NOT an interventional cardiologist or cardiac surgeon.
- In compliance with NMC (National Medical Commission) regulations, no superlative claims (like "Best Doctor" or "No. 1") are made.
- All medical information is for educational purposes. Patients must consult the doctor in person for diagnosis and treatment.

## Contact
- Website: ${CLINIC_SITE}
- Blog Catalog: ${CLINIC_SITE}blogs/index.html
- Phone: ${PHONE}
`;
}

function buildLlmsFullTxt(articles) {
  const blogDetails = articles.map((a, i) => `### ${i + 1}. ${a.title}\n- URL: ${a.url}\n- Author: ${DOCTOR}, Cardiac Physician\n- Topic: ${a.title}`).join("\n\n");
  return `${buildLlmsTxt(articles)}

## Full Article Directory
${blogDetails}
`;
}

function buildHomepageArticlesSection(articles) {
  const cards = articles.map((a) => `
        <div style="background:#ffffff; border:1px solid #d4edff; border-radius:12px; padding:1.2rem; margin:1rem 0; box-shadow:0 2px 8px rgba(0,119,182,0.08);">
            <span style="background:#e63946; color:white; font-size:0.75rem; font-weight:bold; padding:2px 8px; border-radius:6px;">🫀 Heart Health Article</span>
            <h3 style="color:#0077b6; margin:0.5rem 0 0.4rem; font-size:1.15rem;">
                <a href="${a.url}" target="_blank" style="color:#0077b6; text-decoration:none;">${a.title}</a>
            </h3>
            <p style="color:#555; font-size:0.9rem; margin:0.3rem 0;">Expert heart health guide by ${DOCTOR}, Cardiac Physician (Mohiuddinpur, Meerut).</p>
            <a href="${a.url}" target="_blank" style="display:inline-block; background:#0077b6; color:white; padding:0.4rem 1rem; border-radius:8px; text-decoration:none; font-weight:bold; font-size:0.85rem; margin-top:0.5rem;">Read Article →</a>
        </div>`).join("");

  return `<!-- START DYNAMIC AI BLOGS SECTION -->
<div id="latest-published-blogs" style="background:#f4f9fc; padding:40px 20px; border-radius:16px; margin:30px 0; border:1px solid #d4edff;">
    <div style="max-width:900px; margin:0 auto; text-align:center;">
        <span style="background:#0077b6; color:white; padding:4px 12px; border-radius:12px; font-size:0.85rem; font-weight:bold;">📚 Patient Education Articles</span>
        <h2 style="color:#1a1a2e; margin:10px 0 5px; font-size:1.6rem;">Heart Health Articles by ${DOCTOR}</h2>
        <p style="color:#666; font-size:0.95rem; margin-bottom:20px;">Simple, expert-written medical guides in Hindi & English for your heart health.</p>
        <div style="text-align:left;">
            ${cards}
        </div>
        <div style="margin-top:25px;">
            <a href="${CLINIC_SITE}blogs/index.html" target="_blank" style="background:#0077b6; color:white; padding:12px 24px; border-radius:10px; text-decoration:none; font-weight:bold; font-size:1rem; display:inline-block; box-shadow:0 4px 12px rgba(0,119,182,0.2);">
                🌐 View All Articles in Master Catalog →
            </a>
        </div>
    </div>
</div>
<!-- END DYNAMIC AI BLOGS SECTION -->`;
}

async function rebuildHomepage(articles, token) {
  const raw = await getFileContent("index.html", token);
  if (!raw) return { success: false, path: "index.html", error: "Could not fetch index.html" };

  // Scrub non-compliant superlatives (NMC ethics)
  let html = raw;
  html = html.replace(/Best heart doctor in Meerut/gi, "Experienced Cardiac Physician in Meerut");
  html = html.replace(/Best Cardiologist in Meerut/gi, "Experienced Cardiac Physician in Meerut");
  html = html.replace(/best heart doctor/gi, "experienced heart doctor");
  html = html.replace(/best cardiologist/gi, "cardiac physician");

  const section = buildHomepageArticlesSection(articles);
  const START = "<!-- START DYNAMIC AI BLOGS SECTION -->";
  const END = "<!-- END DYNAMIC AI BLOGS SECTION -->";

  let updated;
  if (html.includes(START) && html.includes(END)) {
    const si = html.indexOf(START);
    const ei = html.indexOf(END) + END.length;
    updated = html.slice(0, si) + section + html.slice(ei);
  } else if (html.includes("</body>")) {
    updated = html.replace("</body>", section + "\n</body>");
  } else {
    updated = html + section;
  }

  return putFile("index.html", updated, `📰 Update Homepage Articles Section (${articles.length} articles live) [BHARATSOLVE AI]`, token);
}

// ═══════════════════════════════════════════════════════════════════
// FULL SITE REBUILD ORCHESTRATOR
// ═══════════════════════════════════════════════════════════════════

async function rebuildWebsite(token) {
  const articles = await listBlogs(token);
  const slugs = articles.map((a) => `${a.slug}.html`);

  const results = {};

  results.catalog = await putFile("blogs/index.html", buildCatalogHtml(articles), `📚 Rebuild master blogs/index.html catalog (${articles.length} articles) [BHARATSOLVE AI]`, token);
  results.sitemap = await putFile("sitemap.xml", buildSitemapXml(slugs), "🌐 Update sitemap.xml [BHARATSOLVE AI]", token);
  results.llms = await putFile("llms.txt", buildLlmsTxt(articles), "🤖 Update llms.txt AI Knowledge Blueprint [BHARATSOLVE AI]", token);
  results.llmsFull = await putFile("llms-full.txt", buildLlmsFullTxt(articles), "🤖 Update llms-full.txt Comprehensive AI Blueprint [BHARATSOLVE AI]", token);
  results.robots = await putFile("robots.txt", buildRobotsTxt(), "🤖 Update robots.txt for AI Search Crawlers [BHARATSOLVE AI]", token);
  results.homepage = await rebuildHomepage(articles, token);

  const failed = Object.values(results).filter((r) => r && !r.success).length;
  results.summary = {
    articles: articles.length,
    allSucceeded: failed === 0,
    failedCount: failed
  };
  return results;
}

// ═══════════════════════════════════════════════════════════════════
// ARTICLE HTML BUILDER
// ═══════════════════════════════════════════════════════════════════

function buildArticleHtml(title, markdown) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <meta name="description" content="NMC-compliant cardiology guide by ${DOCTOR} at ${CLINIC_NAME}, ${ADDRESS}.">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; background: #f8fafc; color: #1e293b; }
    .header { background: #0077b6; color: white; padding: 25px; border-radius: 12px; margin-bottom: 25px; }
    .content { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    .cta { background: #e0f2fe; border-left: 4px solid #0077b6; padding: 15px; margin-top: 25px; border-radius: 4px; }
    a { color: #0077b6; text-decoration: none; font-weight: bold; }
  </style>
</head>
<body>
  <div class="header">
    <h1>${title}</h1>
    <p>${DOCTOR} — Cardiac Physician | ${ADDRESS}</p>
  </div>
  <div class="content">
    ${markdown.replace(/\n\n/g, "<br><br>")}
    <div class="cta">
      <h3>📍 ${CLINIC_NAME} — Contact & Appointment</h3>
      <p><b>Address:</b> ${ADDRESS}<br>
      <b>Phone:</b> <a href="tel:+919258879884">${PHONE}</a><br>
      <b>Website:</b> <a href="${CLINIC_SITE}">Visit Clinic Website</a></p>
    </div>
  </div>
</body>
</html>`;
}
