"""
BHARATSOLVE SEO AGENCY — WhatsApp & Telegram 1-Click Share Utility
Generates direct web links to open WhatsApp or Telegram pre-loaded with article text,
lead summaries, or review replies. Requires zero API keys or bot setups!
"""

import urllib.parse

def get_whatsapp_share_url(text: str, phone: str = None) -> str:
    """
    Generate WhatsApp 1-Click direct share URL.
    If phone is provided, opens chat directly with that number (e.g. +91-9258879884).
    Otherwise opens WhatsApp share selector.
    """
    encoded_text = urllib.parse.quote(text)
    if phone:
        # Clean phone number digits
        clean_phone = ''.join(filter(str.isdigit, str(phone)))
        return f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_text}"
    return f"https://api.whatsapp.com/send?text={encoded_text}"


def get_telegram_share_url(text: str, url: str = None) -> str:
    """
    Generate Telegram 1-Click direct share URL.
    """
    encoded_text = urllib.parse.quote(text)
    if url:
        encoded_url = urllib.parse.quote(url)
        return f"https://t.me/share/url?url={encoded_url}&text={encoded_text}"
    return f"https://t.me/share/url?url=&text={encoded_text}"
