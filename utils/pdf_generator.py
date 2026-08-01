"""
BHARATSOLVE SEO AGENCY — PDF Export Generator
Generates clean, professional PDF documents for blogs and research reports.
Uses fpdf2 library. Supports Hindi/Unicode text fallback cleanly.
"""

import os
import re
import html
from fpdf import FPDF

def sanitize_unicode_for_pdf(text: str) -> str:
    """Replace common unicode characters with latin-1 ASCII equivalents."""
    if not text:
        return ""
    replacements = {
        '—': '-', '–': '-', '“': '"', '”': '"', '‘': "'", '’': "'",
        '•': '*', '…': '...', '™': '(TM)', '©': '(C)', '®': '(R)',
        '₹': 'Rs.'
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text.encode('latin-1', 'replace').decode('latin-1')


class CleanPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(0, 119, 182)
        header_text = sanitize_unicode_for_pdf('Gill Heart Clinic - Medical & SEO Content Document')
        self.cell(0, 8, header_text, 0, 1, 'R')
        self.set_draw_color(200, 220, 240)
        self.line(10, 18, 200, 18)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


def clean_text_for_pdf(text: str) -> str:
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
    
    # Normalize spaces
    lines = [line.strip() for line in text.split('\n')]
    cleaned = '\n'.join([l for l in lines if l])
    
    return sanitize_unicode_for_pdf(cleaned)


def create_blog_pdf(title: str, content: str, doctor_name: str = "Dr. Gurjeet Singh Gill", output_path: str = None) -> str:
    """
    Generate PDF file for a blog post or medical article.
    Returns the absolute path to the generated PDF file.
    """
    pdf = CleanPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(0, 119, 182)
    safe_title = sanitize_unicode_for_pdf(title)
    pdf.multi_cell(0, 10, safe_title, 0, 'L')
    pdf.ln(3)
    
    # Subtitle / Author
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(100, 100, 100)
    safe_author = sanitize_unicode_for_pdf(f"Author: {doctor_name} | Gill Heart Clinic, Meerut")
    pdf.cell(0, 6, safe_author, 0, 1, 'L')
    pdf.set_draw_color(0, 180, 216)
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(8)
    
    # Body text
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(40, 40, 40)
    
    cleaned_body = clean_text_for_pdf(content)
    
    for paragraph in cleaned_body.split('\n\n'):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        pdf.multi_cell(0, 7, paragraph, 0, 'L')
        pdf.ln(3)
    
    # Medical Disclaimer
    pdf.ln(5)
    pdf.set_fill_color(254, 243, 199)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(133, 100, 4)
    pdf.multi_cell(0, 6, "Medical Disclaimer: This document is for informational purposes only. Consult Dr. Gurjeet Singh Gill before acting on any medical information.", 1, 'L', True)
    
    if not output_path:
        tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
        os.makedirs(tmp_dir, exist_ok=True)
        safe_filename = re.sub(r'[^a-zA-Z0-9_]', '_', title[:30]) + ".pdf"
        output_path = os.path.join(tmp_dir, safe_filename)
    
    pdf.output(output_path)
    return output_path
