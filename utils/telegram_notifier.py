"""
BHARATSOLVE SEO AGENCY — Telegram Notifier
🏥 Dr. Gurjeet Singh Gill — Gill Heart Clinic

Sends blog drafts / notifications directly to Dr. Gill's Telegram so he can
review content before (or after) it goes live.

Credential lookup order: environment variable → Streamlit secrets → secure vault.

This module NEVER raises on missing config — it returns a clear ``{"ok": False}``
dict so callers can fall back gracefully (e.g. auto-publish if Telegram is off).
"""
import html
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests

TELEGRAM_API = "https://api.telegram.org/bot"
# Telegram hard limit is 4096 chars — keep a safety margin.
TELEGRAM_MAX_CHARS = 3900

# Streamlit app used for the "Review & Publish" button.
STREAMLIT_APP_URL = "https://bharatsolve-seo-agency-template-d7c7gtbuaxpkxkya3dsmcz.streamlit.app/"


# ═══════════════════════════════════════════════════════════════════════
# CONFIG HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _get_secret(name: str) -> str:
    """Read a secret from env → Streamlit secrets → encrypted vault."""
    val = os.getenv(name, "")
    if val and str(val).strip():
        return str(val).strip()

    try:
        import streamlit as st
        if hasattr(st, "secrets") and name in st.secrets:
            v = st.secrets[name]
            if v:
                return str(v).strip()
    except Exception:
        pass

    try:
        from secure_vault import load_api_keys
        v = load_api_keys().get(name, "")
        if v:
            return str(v).strip()
    except Exception:
        pass

    return ""


def get_telegram_credentials() -> Tuple[str, str]:
    """Return (bot_token, chat_id)."""
    return _get_secret("TELEGRAM_BOT_TOKEN"), _get_secret("TELEGRAM_CHAT_ID")


def is_telegram_configured() -> bool:
    """True only when both token and chat_id are present."""
    token, chat_id = get_telegram_credentials()
    return bool(token and chat_id)


# ═══════════════════════════════════════════════════════════════════════
# LOW-LEVEL SENDING
# ═══════════════════════════════════════════════════════════════════════

def escape_html(text: str) -> str:
    """Escape text for Telegram HTML parse mode."""
    return html.escape(str(text or ""), quote=False)


def strip_html(text: str) -> str:
    """Very small HTML → text reducer for readable previews."""
    import re
    text = str(text or "")
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<br\s*/?>|</p>|</h[1-6]>|</li>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def send_telegram_message(
    text: str,
    reply_markup: Optional[dict] = None,
    disable_preview: bool = True,
) -> Dict:
    """
    Send one Telegram message (auto-splits if longer than Telegram's limit).

    Returns:
        {"ok": True, "message_ids": [...]} or {"ok": False, "error": "..."}
    """
    token, chat_id = get_telegram_credentials()
    if not token or not chat_id:
        return {"ok": False, "error": "Telegram not configured (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID missing)"}

    chunks = _split_message(text or "")
    if not chunks:
        return {"ok": False, "error": "Empty message"}

    message_ids: List[int] = []
    for idx, chunk in enumerate(chunks):
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "HTML",
            "disable_web_page_preview": disable_preview,
        }
        # Only the last chunk carries the buttons.
        if reply_markup and idx == len(chunks) - 1:
            payload["reply_markup"] = json.dumps(reply_markup)

        try:
            resp = requests.post(f"{TELEGRAM_API}{token}/sendMessage", data=payload, timeout=30)
            data = resp.json()
        except Exception as e:
            return {"ok": False, "error": f"Telegram request failed: {e}"}

        if not data.get("ok"):
            # Most common cause: bad HTML in parse_mode. Retry once as plain text.
            if "parse" in str(data.get("description", "")).lower():
                payload.pop("parse_mode", None)
                payload["text"] = strip_html(chunk)
                try:
                    resp = requests.post(f"{TELEGRAM_API}{token}/sendMessage", data=payload, timeout=30)
                    data = resp.json()
                except Exception as e:
                    return {"ok": False, "error": f"Telegram retry failed: {e}"}
            if not data.get("ok"):
                return {"ok": False, "error": f"Telegram API: {data.get('description', 'Unknown error')}"}

        message_ids.append(data.get("result", {}).get("message_id"))

    return {"ok": True, "message_ids": message_ids}


def _split_message(text: str) -> List[str]:
    """Split a long message on line boundaries."""
    if len(text) <= TELEGRAM_MAX_CHARS:
        return [text] if text.strip() else []

    chunks: List[str] = []
    current = ""
    for line in text.split("\n"):
        # A single oversized line gets hard-split.
        while len(line) > TELEGRAM_MAX_CHARS:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(line[:TELEGRAM_MAX_CHARS])
            line = line[TELEGRAM_MAX_CHARS:]

        if len(current) + len(line) + 1 > TELEGRAM_MAX_CHARS:
            chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line

    if current.strip():
        chunks.append(current)
    return chunks


# ═══════════════════════════════════════════════════════════════════════
# HIGH-LEVEL NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════

def _review_button(slug: str) -> dict:
    """Inline keyboard pointing to the app's review screen."""
    return {
        "inline_keyboard": [[
            {"text": "📲 Review & Publish", "url": f"{STREAMLIT_APP_URL}?draft={slug}"}
        ]]
    }


def send_blog_draft_for_review(draft: dict, preview_chars: int = 1500) -> Dict:
    """
    Send a generated blog draft to Telegram for Dr. Gill's review.

    `draft` is the dict stored by agents.draft_review.save_pending_draft().
    """
    slug = draft.get("slug", "")
    title = strip_html(draft.get("title", "Untitled"))
    topic = strip_html(draft.get("topic", ""))
    language = draft.get("language", "Hinglish")
    words = draft.get("word_count", 0)
    preview = strip_html(draft.get("content", ""))[:preview_chars]
    if len(strip_html(draft.get("content", ""))) > preview_chars:
        preview += "\n… (aage ka content app mein)"

    body = (
        "🫀 <b>NAYA BLOG DRAFT — AAPKE REVIEW KE LIYE</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 <b>Title:</b> {escape_html(title)}\n"
        f"🎯 <b>Topic:</b> {escape_html(topic)}\n"
        f"🗣️ <b>Language:</b> {escape_html(language)}\n"
        f"📊 <b>Words:</b> {escape_html(str(words))}\n"
        f"🕒 <b>Bana:</b> {escape_html(draft.get('created_at', '')[:16].replace('T', ' '))}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👁️ <b>PREVIEW:</b>\n\n"
        f"{escape_html(preview)}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✅ <b>Approve</b> karne par yeh live publish ho jayega.\n"
        "❌ <b>Reject</b> karne par publish nahi hoga.\n"
        "<i>(Neeche button dabayein → app khulega → Publish/Reject chunein)</i>"
    )

    return send_telegram_message(body, reply_markup=_review_button(slug))


def send_publish_confirmation(draft: dict, published_url: str) -> Dict:
    """Notify Dr. Gill that a reviewed draft is now LIVE."""
    body = (
        "✅ <b>BLOG LIVE HO GAYA!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 <b>{escape_html(strip_html(draft.get('title', '')))}</b>\n"
        f"🔗 <a href=\"{escape_html(published_url)}\">Yahan padhein</a>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🌐 Website homepage + sitemap + llms.txt bhi update ho gaye hain."
    )
    return send_telegram_message(body, disable_preview=False)


def send_review_reply_notification(reviewer: str, rating, reply: str, posted: bool) -> Dict:
    """Notify about a Google review reply (posted or pending manual posting)."""
    status_line = (
        "✅ Google par post ho gaya"
        if posted
        else "📋 Copy karke Google par paste karein (auto-post pending)"
    )
    body = (
        "⭐ <b>GOOGLE REVIEW REPLY</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Patient:</b> {escape_html(reviewer)}\n"
        f"⭐ <b>Rating:</b> {escape_html(str(rating))}/5\n"
        f"💬 <b>AI Reply:</b>\n{escape_html(reply)}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{status_line}"
    )
    return send_telegram_message(body, disable_preview=False)


def send_status_alert(title: str, detail: str, ok: bool = False) -> Dict:
    """Generic success/failure alert (used by the runner + scheduler)."""
    icon = "✅" if ok else "⚠️"
    body = (
        f"{icon} <b>{escape_html(title)}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{escape_html(detail)}"
    )
    return send_telegram_message(body)


def send_test_message() -> Dict:
    """Send a connectivity test message (used by the setup guide / UI)."""
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")
    return send_telegram_message(
        "🫀 <b>Gill Heart Clinic — Telegram Connected!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🕒 {escape_html(now)}\n"
        "Ab aapko roz blog drafts yahan milenge review ke liye. ✅"
    )
