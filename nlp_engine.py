import spacy
import re

# Load once at module level
nlp = spacy.load("en_core_web_sm")

def normalize_case(text):
    """
    Normalize text for better NLP recognition.
    """
    # Lowercase everything then Title-case
    return text.lower().title()

def extract_name_by_pattern(block):
    """
    Try to extract name patterns when NER fails.
    We look for lines with only letters (no digits) that could be names.
    """
    lines = block.split("\n")
    names = []
    for line in lines:
        clean = line.strip()
        # Only letters and spaces; length > 2
        if re.fullmatch(r"[A-Za-z ]{3,30}", clean):
            # Avoid common label words
            if clean.upper() not in ["DATE OF BIRTH", "DOB", "CERTIFICATE", "NAME"]:
                names.append(clean.title())
    return names

def extract_entities(blocks):
    entities = {
        "PERSON": set(),
        "ORG": set(),
        "DATE": set(),
        "GPE": set()
    }

    for block in blocks:
        if not block.strip():
            continue

        # Normalize text before NLP
        normalized = normalize_case(block)

        # spaCy NER pass
        doc = nlp(normalized)
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].add(ent.text.strip())

        # Fallback pattern for names
        pattern_names = extract_name_by_pattern(block)
        for n in pattern_names:
            entities["PERSON"].add(n)

    return entities
