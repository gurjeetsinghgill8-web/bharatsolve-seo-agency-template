"""
BHARATSOLVE SEO AGENCY — PDF Export Generator
Generates clean, professional PDF documents for blogs and research reports.
Uses fpdf2 library. Supports Hindi/Unicode text fallback cleanly.
"""

import os
import re
import html
from fpdf import FPDF

DEV_WORD_MAP = {
    'डॉक्टर': 'Doctor', 'हृदय': 'Heart', 'लक्षण': 'Symptoms', 'उपचार': 'Treatment',
    'सलाह': 'Advice', 'मेरठ': 'Meerut', 'गिल': 'Gill', 'क्लीनिक': 'Clinic', 'क्लिनिक': 'Clinic',
    'दर्द': 'Pain', 'सीने': 'Chest', 'संकेत': 'Warning Signs', 'चेतावनी': 'Warning',
    'कारण': 'Causes', 'बचाव': 'Prevention', 'जांच': 'Tests', 'आहार': 'Diet',
    'जीवनशैली': 'Lifestyle', 'रोग': 'Disease', 'हमला': 'Heart Attack', 'उच्च': 'High',
    'रक्तचाप': 'Blood Pressure', 'सर्वश्रेष्ठ': 'Best', 'विकल्प': 'Option', 'जानकारी': 'Information',
    'समस्या': 'Problem', 'परामर्श': 'Consultation', 'नियमित': 'Regular', 'स्वस्थ': 'Healthy',
    'निष्कर्ष': 'Conclusion', 'कुंजी': 'Key', 'तथ्य': 'Facts', 'के': 'ke', 'का': 'ka',
    'की': 'ki', 'में': 'mein', 'और': 'aur', 'या': 'ya', 'है': 'hai', 'हैं': 'hain',
    'से': 'se', 'को': 'ko', 'पर': 'par', 'तो': 'toh', 'भी': 'bhi', 'लिए': 'liye',
    'आप': 'aap', 'अगर': 'agar', 'तुरंत': 'turant', 'पास': 'paas', 'मेरी': 'meri', 'चाहते': 'chahte',
    'योग्य': 'Qualified', 'अस्पताल': 'Hospital', 'जांचें': 'Tests'
}

DEV_CHAR_MAP = {
    'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo', 'ऋ': 'ri', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'अं': 'an', 'अः': 'ah',
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng', 'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'n',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n', 'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'f', 'ब': 'b', 'भ': 'bh', 'म': 'm', 'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h',
    'ा': 'aa', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo', 'ृ': 'ri', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', '्': '', 'ं': 'n', 'ः': 'h', '़': '', 'ॉ': 'o', 'ॅ': 'e'
}

def transliterate_devanagari(text: str) -> str:
    """Convert Devanagari Hindi text to clean readable Romanized text so PDF never shows ????."""
    if not text:
        return ""
    # Word level replacement
    for dev, rom in DEV_WORD_MAP.items():
        text = text.replace(dev, rom)
    # Character level replacement for remaining Devanagari chars
    res = []
    for ch in text:
        if ch in DEV_CHAR_MAP:
            res.append(DEV_CHAR_MAP[ch])
        elif ord(ch) >= 0x0900 and ord(ch) <= 0x097F:
            continue  # strip unmapped devanagari diacritics
        else:
            res.append(ch)
    return "".join(res)

def sanitize_unicode_for_pdf(text: str) -> str:
    """Replace unicode characters and transliterate Devanagari to latin-1 ASCII equivalents."""
    if not text:
        return ""
    # Transliterate Devanagari first
    if any(0x0900 <= ord(c) <= 0x097F for c in text):
        text = transliterate_devanagari(text)

    replacements = {
        '—': '-', '–': '-', '“': '"', '”': '"', '‘': "'", '’': "'",
        '•': '*', '…': '...', '™': '(TM)', '©': '(C)', '®': '(R)',
        '₹': 'Rs.'
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text.encode('latin-1', 'replace').decode('latin-1')


def get_devanagari_fonts():
    font_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "fonts")
    reg_p = os.path.join(font_dir, "HindiDevanagari.ttf")
    bold_p = os.path.join(font_dir, "HindiDevanagariBold.ttf")
    
    if os.path.exists(reg_p):
        return reg_p, bold_p if os.path.exists(bold_p) else reg_p
    elif os.path.exists(r"C:\Windows\Fonts\Nirmala.ttf"):
        return r"C:\Windows\Fonts\Nirmala.ttf", r"C:\Windows\Fonts\NirmalaB.ttf"
    return None, None


class CleanPDF(FPDF):
    def __init__(self, use_font="Helvetica"):
        super().__init__()
        self.use_font = use_font

    def header(self):
        self.set_font(self.use_font, 'B' if self.use_font == 'Helvetica' else '', 10)
        self.set_text_color(0, 119, 182)
        h_text = 'Gill Heart Clinic — Medical & SEO Content Document' if self.use_font != 'Helvetica' else sanitize_unicode_for_pdf('Gill Heart Clinic - Medical & SEO Content Document')
        self.cell(0, 8, h_text, 0, 1, 'R')
        self.set_draw_color(200, 220, 240)
        self.line(10, 18, 200, 18)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.use_font, '' if self.use_font != 'Helvetica' else 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


def clean_text_for_pdf(text: str, force_ascii: bool = False) -> str:
    """Strip HTML tags and unescape text for basic PDF rendering."""
    if not text:
        return ""
    
    # Replace breaks and headings with newlines
    text = re.sub(r'<h[1-6][^>]*>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</h[1-6]>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<p[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<li[^>]*>', '\n* ', text, flags=re.IGNORECASE)
    
    # Strip remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    
    lines = [line.strip() for line in text.split('\n')]
    cleaned = '\n'.join([l for l in lines if l])
    
    if force_ascii:
        return sanitize_unicode_for_pdf(cleaned)
    return cleaned


def create_blog_pdf(title: str, content: str, doctor_name: str = "Dr. Gurjeet Singh Gill", output_path: str = None) -> str:
    """
    Generate PDF file for a blog post or medical article with native Hindi Devanagari font support.
    Returns the absolute path to the generated PDF file.
    """
    reg_font, bold_font = get_devanagari_fonts()
    use_native_font = reg_font is not None
    
    use_font_name = "Devanagari" if use_native_font else "Helvetica"
    pdf = CleanPDF(use_font=use_font_name)
    
    if use_native_font:
        try:
            pdf.add_font("Devanagari", "", reg_font)
            pdf.add_font("Devanagari", "B", bold_font)
        except Exception as e:
            print(f"Font add note: {e}")
            use_font_name = "Helvetica"
            pdf.use_font = "Helvetica"
    
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font(use_font_name, 'B' if use_font_name == 'Helvetica' else '', 16)
    pdf.set_text_color(0, 119, 182)
    safe_title = title if use_font_name != 'Helvetica' else sanitize_unicode_for_pdf(title)
    pdf.multi_cell(0, 10, safe_title, 0, 'L')
    pdf.ln(3)
    
    # Subtitle / Author
    pdf.set_font(use_font_name, '' if use_font_name != 'Helvetica' else 'I', 10)
    pdf.set_text_color(100, 100, 100)
    author_str = f"Author: {doctor_name} | Gill Heart Clinic, Mohiuddinpur, Meerut"
    safe_author = author_str if use_font_name != 'Helvetica' else sanitize_unicode_for_pdf(author_str)
    pdf.cell(0, 6, safe_author, 0, 1, 'L')
    pdf.set_draw_color(0, 180, 216)
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(8)
    
    # Body text
    pdf.set_font(use_font_name, '', 11)
    pdf.set_text_color(40, 40, 40)
    
    cleaned_body = clean_text_for_pdf(content, force_ascii=(use_font_name == 'Helvetica'))
    
    for paragraph in cleaned_body.split('\n\n'):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        pdf.multi_cell(0, 7, paragraph, 0, 'L')
        pdf.ln(3)
    
    # Medical Disclaimer
    pdf.ln(5)
    pdf.set_fill_color(254, 243, 199)
    pdf.set_font(use_font_name, '' if use_font_name != 'Helvetica' else 'B', 9)
    pdf.set_text_color(133, 100, 4)
    disc_text = "Medical Disclaimer: This document is for informational purposes. Consult Dr. Gurjeet Singh Gill, Cardiac Physician, before acting on any medical advice."
    pdf.multi_cell(0, 6, disc_text, 1, 'L', True)
    
    if not output_path:
        tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
        os.makedirs(tmp_dir, exist_ok=True)
        safe_filename = re.sub(r'[^a-zA-Z0-9_]', '_', title[:30]) + ".pdf"
        output_path = os.path.join(tmp_dir, safe_filename)
    
    pdf.output(output_path)
    return output_path
