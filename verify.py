import re
from rapidfuzz import fuzz
from utils import normalize

# ---------- NAME MATCHING FUNCTION ----------

def strict_name_match(input_name, candidates):
    """
    Stricter fuzzy matching (case-insensitive).
    Compares only against PERSON entity candidates.
    """
    # Normalize input once
    inp = normalize(input_name)

    if not inp or not candidates:
        return 0

    scores = []
    for cand in candidates:
        cand_norm = normalize(cand)
        # Use token_sort_ratio for more robust matching
        score = fuzz.token_sort_ratio(inp, cand_norm)
        scores.append(score)

    return max(scores) if scores else 0


# ---------- EXTRACT DATES ----------

def extract_dates(text):
    """
    Returns all date strings in DD/MM/YYYY or with - or . separators.
    """
    return re.findall(r"\b\d{2}[\/\-.]\d{2}[\/\-.]\d{4}\b", text)


# ---------- EXTRACT CERTIFICATE NUMBERS ----------

def extract_certificate_numbers(text):
    """
    Returns all 8-digit numbers in the full text.
    """
    return re.findall(r"\b\d{8}\b", text)


# ---------- MAIN VERIFY FUNCTION ----------

def verify(form_data, extracted_entities, full_text=""):
    """
    Compare user input (name, dob, certificate_no) with what was extracted.
    Return:
        - issues: list of mismatch or low confidence messages
        - confidence: dict of confidence scores
    """

    issues = []
    confidence = {}

    # ---------- NAME VERIFICATION ----------
    name = form_data.get("name", "").strip()
    # Only PERSON entities from entity extraction — no full_text fallback
    name_candidates = list(extracted_entities.get("PERSON", []))

    # Compute confidence
    name_conf = strict_name_match(name, name_candidates)
    confidence["Name"] = name_conf

    # Threshold (tuneable; 85 is stricter than 80)
    if name and name_conf < 85:
        issues.append("Candidate name mismatch or low confidence")

    # ---------- DATE OF BIRTH VERIFICATION ----------
    dob = form_data.get("dob", "").strip()
    extracted_dobs = extract_dates(full_text)
    # Simple exact match check for dob
    dob_conf = 100 if (dob and dob in extracted_dobs) else 0
    confidence["Date of Birth"] = dob_conf

    if dob and dob_conf == 0:
        issues.append("Date of birth mismatch or not found")

    # ---------- CERTIFICATE NUMBER VERIFICATION ----------
    cert = form_data.get("certificate_no", "").strip()
    extracted_certs = extract_certificate_numbers(full_text)
    cert_conf = 100 if (cert and cert in extracted_certs) else 0
    confidence["Certificate Number"] = cert_conf

    if cert and cert_conf == 0:
        issues.append("Certificate number mismatch or not found")

    return issues, confidence
