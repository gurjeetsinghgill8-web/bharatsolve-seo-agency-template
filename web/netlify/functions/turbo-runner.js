/**
 * 🔒 SECURE NETLIFY SERVERLESS BACKEND FUNCTION
 * Keeps all API keys (GEMINI_API_KEY, GROQ_API_KEY, GITHUB_TOKEN) hidden on the server!
 * Zero keys are exposed to the browser or client.
 *
 * Actions:
 *   - "health"        → report which providers are configured (no key values leak)
 *   - "turbo_blog"    → generate + publish an NMC/GEO-compliant article to GitHub Pages
 *   - "review_reply"  → generate a warm Hinglish/English reply for a patient review
 */

const REPO = "gurjeetsinghgill8-web/gill-heart-clinic";
const CLINIC_SITE = "https://gurjeetsinghgill8-web.github.io/gill-heart-clinic/";

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
  // CORS preflight
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

      const prompt = `Write a polite, warm, professional Hinglish reply to this patient Google review for Dr. Gurjeet Singh Gill at Gill Heart Clinic Mohiuddinpur Meerut. Patient Name: ${patientName || "Patient"}, Review: "${review}". Thank them for trusting us with their heart health. Keep it 2-3 sentences. Do NOT use banned superlatives like 'Best' or 'No. 1'.`;

      let replyText = await geminiGenerate(prompt, GEMINI_API_KEY, 256);
      if (!replyText) replyText = await deepseekGenerate(prompt, DEEPSEEK_API_KEY, 256);
      if (!replyText) replyText = await groqGenerate(prompt, GROQ_API_KEY, 256);
      if (!replyText) {
        replyText = `धन्यवाद ${patientName || ""} जी! 🙏 आपके कीमती feedback के लिए बहुत-बहुत शुक्रिया। हम हमेशा अपने patients की heart health के लिए committed हैं। ❤️`;
      }
      return ok({ success: true, reply: replyText });
    }

    // ── ACTION 2: TURBO BLOG GENERATION & GITHUB PUSH ──
    const targetQuery = query || "heart doctor near me";
    const targetLang = lang || "Hinglish";

    const prompt = `Write an authoritative, 100% NMC-compliant cardiology & heart health guide for Dr. Gurjeet Singh Gill (MBBS, Diploma Cardiology UN Mehta, PGDCCP, AI in Healthcare IIT Kanpur) at Gill Heart Clinic, Sugar Mill, Mohiuddinpur, Meerut 250205. 
Target Query: "${targetQuery}". 
Language: ${targetLang}. 
Strict Guidelines: 
- 100% NMC Registered Medical Practitioner Regulations (do NOT use banned superlatives like 'Best' or 'No. 1').
- Detail diagnostic services: 12-Lead ECG, 2D Echo, Blood Pressure Profiling, Preventive Heart Counseling.
- Clinic details: Sugar Mill, Mohiuddinpur, Meerut, UP 250205 | Phone: +91-9258879884.
- Include structured sections: Symptoms & Warning Signs, Preventive Strategies, Diagnostic Importance, and FAQs.`;

    let markdown = await geminiGenerate(prompt, GEMINI_API_KEY, 2048);
    if (!markdown) markdown = await deepseekGenerate(prompt, DEEPSEEK_API_KEY, 2048);
    if (!markdown) markdown = await groqGenerate(prompt, GROQ_API_KEY, 2048);
    if (!markdown) {
      markdown = `## ${targetQuery} — Complete Patient Guide by Dr. Gurjeet Singh Gill\n\nTimely cardiovascular assessment is vital for patients across Meerut and Delhi NCR. Visit Gill Heart Clinic, Sugar Mill, Mohiuddinpur for expert non-invasive cardiology care.`;
    }

    const slug = targetQuery.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
    const title = `${targetQuery} — Dr. Gurjeet Singh Gill | Gill Heart Clinic Meerut`;

    const fullHtml = buildArticleHtml(title, markdown);

    // Server-side GitHub commit (uses server GITHUB_TOKEN — never the browser)
    let isPushedLive = false;
    let publishedUrl = "";
    if (GITHUB_TOKEN) {
      const result = await publishToGitHub(slug, title, fullHtml, GITHUB_TOKEN);
      isPushedLive = result.success;
      publishedUrl = result.url;
    }

    return ok({
      success: true,
      title,
      query: targetQuery,
      url: publishedUrl || `#preview-${slug}`,
      isLive: isPushedLive,
      content: fullHtml,
      note: isPushedLive
        ? "Published live to GitHub Pages."
        : "Generated, but not published (GITHUB_TOKEN is not configured on the server)."
    });

  } catch (error) {
    console.error("turbo-runner error:", error);
    return fail(500, error.message);
  }
};

// ── Helpers ──

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

async function publishToGitHub(slug, title, htmlContent, token) {
  const path = `blogs/${slug}.html`;
  const url = `https://api.github.com/repos/${REPO}/contents/${path}`;
  const headers = {
    Authorization: `Bearer ${token}`,
    Accept: "application/vnd.github.v3+json"
  };

  try {
    // Check for existing file to get SHA (for update)
    let sha = null;
    const checkRes = await fetch(url, { headers });
    if (checkRes.ok) {
      const data = await checkRes.json();
      sha = data.sha;
    }

    const contentEncoded = Buffer.from(htmlContent).toString("base64");
    const commitRes = await fetch(url, {
      method: "PUT",
      headers: { ...headers, "Content-Type": "application/json" },
      body: JSON.stringify({
        message: `🤖 Serverless Auto-SEO: Publish article '${title}'`,
        content: contentEncoded,
        sha: sha || undefined
      })
    });

    if (commitRes.ok) {
      return {
        success: true,
        url: `${CLINIC_SITE}blogs/${slug}.html`
      };
    }
    const err = await commitRes.json().catch(() => ({}));
    console.error("GitHub commit error:", err.message);
    return { success: false, url: "" };
  } catch (e) {
    console.error("GitHub network error:", e.message);
    return { success: false, url: "" };
  }
}

function buildArticleHtml(title, markdown) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <meta name="description" content="NMC-compliant cardiology guide by Dr. Gurjeet Singh Gill at Gill Heart Clinic, Sugar Mill, Mohiuddinpur, Meerut.">
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
    <p>Dr. Gurjeet Singh Gill — Cardiac Physician | Sugar Mill, Mohiuddinpur, Meerut 250205</p>
  </div>
  <div class="content">
    ${markdown.replace(/\n\n/g, "<br><br>")}
    <div class="cta">
      <h3>📍 Gill Heart Clinic — Contact & Appointment</h3>
      <p><b>Address:</b> Sugar Mill, Mohiuddinpur, Meerut, Uttar Pradesh 250205<br>
      <b>Phone:</b> <a href="tel:+919258879884">+91-9258879884</a><br>
      <b>Website:</b> <a href="${CLINIC_SITE}">Visit Clinic Website</a></p>
    </div>
  </div>
</body>
</html>`;
}
