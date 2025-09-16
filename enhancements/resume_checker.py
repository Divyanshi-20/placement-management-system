import re
import os
import json

def extract_text_from_pdf(filepath):
    """Extract plain text from a PDF file."""
    try:
        from pdfminer.high_level import extract_text
    except Exception:
        return ""
    try:
        text = extract_text(filepath)
        return text or ""
    except Exception:
        return ""

def extract_text_from_docx(filepath):
    """Extract plain text from a DOCX file."""
    try:
        import docx
    except Exception:
        return ""
    try:
        doc = docx.Document(filepath)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception:
        return ""

def basic_checks(text):
    """Perform basic ATS-like checks and return suggestions + score."""
    suggestions = []
    score = 0
    s = (text or "").lower()

    # Contact info
    phone = re.search(r'(\+?\d{10,15})', text or "")
    email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text or "")
    if phone and email:
        score += 2
    else:
        suggestions.append("Add a clear email and phone number at the top of your resume.")

    # Section headings
    for sec in ["education", "experience", "skills", "projects"]:
        if sec in s:
            score += 1
        else:
            suggestions.append(f"Add a '{sec.capitalize()}' section if relevant.")

    # Keywords
    keywords = ["python", "java", "c++", "react", "flask", "django", "sql", "aws", "docker"]
    found_kw = [k for k in keywords if k in s]
    score += min(len(found_kw), 3)
    if len(found_kw) == 0:
        suggestions.append("Include relevant technical keywords (languages, frameworks) related to the role.")

    # Images/tables detection (heuristic)
    if re.search(r'<img|<table|\\bimage\\b|\\btable\\b', text or "", re.IGNORECASE):
        suggestions.append("Avoid using images or complex tables — ATS may not parse them correctly.")

    # Word count heuristic
    words = len((text or "").split())
    if words < 200:
        suggestions.append("Your resume looks short — aim for 1 page with meaningful achievements.")
    elif words > 2000:
        suggestions.append("Your resume is very long — try to keep it concise (1-2 pages).")
    else:
        score += 1

    # Final score
    total_possible = 8
    normalized = max(0, min(100, int((score / total_possible) * 100)))
    verdict = "good" if normalized >= 60 else "needs_improvement"

    return {
        "score_percent": normalized,
        "verdict": verdict,
        "keywords_found": found_kw,
        "suggestions": suggestions
    }

def analyze_resume(filepath):
    """
    Main entrypoint for resume analysis.
    Detects file type, extracts text, and runs basic checks.
    """
    ext = os.path.splitext(filepath)[1].lower()
    text = ""

    # Extract based on extension
    if ext == ".pdf":
        text = extract_text_from_pdf(filepath)
    elif ext in (".docx", ".doc"):
        text = extract_text_from_docx(filepath)
    else:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        except Exception:
            text = ""

    # Fallback: raw bytes preview if text empty
    if not text:
        try:
            with open(filepath, 'rb') as f:
                raw = f.read(4000)  # read first 4KB
                text = raw.decode("utf-8", errors="ignore")
        except Exception:
            text = ""

    return basic_checks(text)
