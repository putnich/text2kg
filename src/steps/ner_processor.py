import spacy
from transformers import pipeline

from src.config.config import logger, NER_MODEL, SPACY_MODEL

ner = pipeline(
    "ner",
    model=NER_MODEL,
    grouped_entities=True,
)

nlp = spacy.load(SPACY_MODEL)

def extract_spos(sent_doc):
    spos = []
    root = next((t for t in sent_doc if t.dep_ == "ROOT"), None)
    if not root:
        return spos

    # subjects
    subjects = [t for t in root.lefts if t.dep_ in ("nsubj", "nsubjpass")]

    # objects
    objects = []
    for t in root.rights:
        if t.dep_ in ("dobj", "attr"):
            objects.append(t)
        elif t.dep_ == "prep":
            objects.extend([c for c in t.children if c.dep_ == "pobj"])
        elif t.dep_ == "agent":
            objects.extend([c for c in t.children if c.dep_ == "pobj"])

    for subj in subjects:
        subj_text = " ".join([t.text for t in subj.subtree])
        for obj in objects:
            obj_text = " ".join([t.text for t in obj.subtree])
            # only keep if they look like arguments
            if any(t.pos_ in ("NOUN", "PROPN") for t in subj.subtree) and \
               any(t.pos_ in ("NOUN", "PROPN") for t in obj.subtree):
                spos.append((subj_text.strip(), root.lemma_, obj_text.strip()))

    return spos

def process(text: str):
    # First perform NER on the entire text for better context
    named_entities = [
        (ent["word"], ent["entity_group"], ent["start"], ent["end"])
        for ent in ner(text)
    ]
    logger.info(f"Extracted Entities: {named_entities}")
    doc = nlp(text)
    extracted_spos = []

    for sent in doc.sents:
        extracted_spos.extend(extract_spos(sent))
    
    def _add_label(entity):
        for (ent_text, ent_label, start, end) in named_entities:
            if ent_text in entity:
                return f"<{ent_label}>{ent_text}</{ent_label}>"
        return entity

    tagged_spos = []
    for subj, pred, obj in extracted_spos:
        subj_tagged = _add_label(subj)
        obj_tagged = _add_label(obj)
        tagged_spos.append((subj_tagged, pred, obj_tagged))

    return tagged_spos