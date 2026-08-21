/**
 * 🔒 SECURE NETLIFY SERVERLESS BACKEND FUNCTION
 * Keeps all API keys (GEMINI_API_KEY, GITHUB_TOKEN, GROQ_API_KEY) hidden on the server!
 * Zero keys are exposed to the browser or client.
 */

exports.handler = async (event, context) => {
  // Only accept POST
  if (event.httpMethod !== "POST") {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: "Method not allowed" })
    };
  }

  // Parse request
  let body;
  try {
    body = JSON.parse(event.body);
  } catch (e) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: "Invalid JSON body" })
    };
  }

  const { query, lang, action, reviewText, patientName } = body;
  
  // Get Server-Side Environment Secrets (100% Hidden & Encrypted on Netlify)
  const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
  const GROQ_API_KEY = process.env.GROQ_API_KEY;
  const GITHUB_TOKEN = process.env.GITHUB_TOKEN;

  const REPO = "gurjeetsinghgill8-web/gill-heart-clinic";

  try {
    // ── ACTION 1: REVIEW AUTO-REPLY ──
    if (action === "review_reply") {
      const prompt = `Write a polite, warm, professional Hinglish reply to this patient Google review for Dr. Gurjeet Singh Gill at Gill Heart Clinic Mohiuddinpur Meerut. Patient Name: ${patientName || "Patient"}, Review: "${reviewText}". Thank them for trusting us with their heart health. Keep it 2-3 sentences.`;
      
      let replyText = "";
      if (GEMINI_API_KEY) {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEMINI_API_KEY}`;
        const res = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: { temperature: 0.7, maxOutputTokens: 256 }
          })
        });
        if (res.ok) {
          const data = await res.json();
          replyText = data.candidates[0].content.parts[0].text;
        }
      }
      if (!replyText) {
        replyText = `धन्यवाद ${patientName || ""} जी! 🙏 आपके कीमती feedback के लिए बहुत-बहुत शुक्रिया। हम हमेशा अपने patients की heart health के लिए committed हैं। ❤️`;
      }
      return {
        statusCode: 200,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ success: true, reply: replyText })
      };
    }

    // ── ACTION 2: TURBO BLOG GENERATION & GITHUB PUSH ──
    const targetQuery = query || "heart doctor near me";
    const targetLang = lang || "Hinglish";

    const prompt = `Write an authoritative, 100% NMC-compliant cardiology & heart health guide for Dr. Gurjeet Singh Gill (MBBS, Diploma Cardiology UN Mehta, PGDCCP, AI in Healthcare IIT Kanpur) at Gill Heart Clinic, Mohiuddinpur, Meerut. 
Target Query: "${targetQuery}". 
Language: ${targetLang}. 
Strict Guidelines: 
- 100% NMC Registered Medical Practitioner Regulations (do NOT use banned superlatives like 'Best' or 'No. 1').
- Detail diagnostic services: 12-Lead ECG, Blood Pressure Profiling, Preventive Heart Counseling.
- Clinic details: Mohiuddinpur, Meerut, UP | Phone: +91-9258879884.
- Include structured sections: Symptoms & Warning Signs, Preventive Strategies, Diagnostic Importance, and FAQs.`;

    let markdown = "";

    // 1. Server-side AI generation (Gemini primary)
    if (GEMINI_API_KEY) {
      try {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEMINI_API_KEY}`;
        const res = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: { temperature: 0.7, maxOutputTokens: 2048 }
          })
        });
        if (res.ok) {
          const data = await res.json();
          markdown = data.candidates[0].content.parts[0].text;
        }
      } catch (e) {
        console.error("Gemini server call error", e);
      }
    }

    // 2. Groq fallback
    if (!markdown && GROQ_API_KEY) {
      try {
        const url = "https://api.groq.com/openai/v1/chat/completions";
        const res = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${GROQ_API_KEY}`
          },
          body: JSON.stringify({
            model: "llama-3.1-8b-instant",
            messages: [{ role: "user", content: prompt }]
          })
        });
        if (res.ok) {
          const data = await res.json();
          markdown = data.choices[0].message.content;
        }
      } catch (e) {
        console.error("Groq server call error", e);
      }
    }

    // Fallback template if no AI keys configured
    if (!markdown) {
      markdown = `## ${targetQuery} — Complete Patient Guide by Dr. Gurjeet Singh Gill\n\nTimely cardiovascular assessment is vital for patients across Meerut and Delhi NCR. Visit Gill Heart Clinic, Mohiuddinpur for expert non-invasive cardiology care.`;
    }

    const slug = targetQuery.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    const title = `${targetQuery} — Dr. Gurjeet Singh Gill | Gill Heart Clinic Meerut`;

    const fullHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <meta name="description" content="Cardiology guide by Dr. Gurjeet Singh Gill at Gill Heart Clinic, Mohiuddinpur, Meerut.">
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
    <p>Dr. Gurjeet Singh Gill — Cardiac Physician | Mohiuddinpur, Meerut</p>
  </div>
  <div class="content">
    ${markdown.replace(/\n\n/g, '<br><br>')}
    <div class="cta">
      <h3>📍 Gill Heart Clinic — Contact & Appointment</h3>
      <p><b>Address:</b> Mohiuddinpur, Meerut, Uttar Pradesh<br>
      <b>Phone:</b> <a href="tel:+919258879884">+91-9258879884</a><br>
      <b>Website:</b> <a href="https://gurjeetsinghgill8-web.github.io/gill-heart-clinic/">Visit Clinic Website</a></p>
    </div>
  </div>
</body>
</html>`;

    // 3. Server-side GitHub Commit (Uses server GITHUB_TOKEN)
    let isPushedLive = false;
    let publishedUrl = "";

    if (GITHUB_TOKEN) {
      const path = `blogs/${slug}.html`;
      const url = `https://api.github.com/repos/${REPO}/contents/${path}`;

      let sha = null;
      const checkRes = await fetch(url, {
        headers: {
          "Authorization": `Bearer ${GITHUB_TOKEN}`,
          "Accept": "application/vnd.github.v3+json"
        }
      });
      if (checkRes.ok) {
        const data = await checkRes.json();
        sha = data.sha;
      }

      const contentEncoded = Buffer.from(fullHtml).toString('base64');
      const commitRes = await fetch(url, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${GITHUB_TOKEN}`,
          "Content-Type": "application/json",
          "Accept": "application/vnd.github.v3+json"
        },
        body: JSON.stringify({
          message: `🤖 Serverless Auto-SEO: Publish article '${title}'`,
          content: contentEncoded,
          sha: sha || undefined
        })
      });

      if (commitRes.ok) {
        isPushedLive = true;
        publishedUrl = `https://gurjeetsinghgill8-web.github.io/gill-heart-clinic/blogs/${slug}.html`;
      }
    }

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        success: true,
        title: title,
        query: targetQuery,
        url: publishedUrl || `#preview-${slug}`,
        isLive: isPushedLive,
        content: fullHtml
      })
    };

  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};
