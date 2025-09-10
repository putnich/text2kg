import spacy, claucy
from transformers import pipeline

from src.config.config import logger, NER_MODEL, SPACY_MODEL

ner = pipeline(
    "ner",
    model=NER_MODEL,
    grouped_entities=True,
)

nlp = spacy.load(SPACY_MODEL)
claucy.add_to_pipe(nlp)


def _to_text(x):
    if isinstance(x, (list, tuple)):
        return " ".join(_to_text(y) for y in x)
    if hasattr(x, "lemma_"):
        return x.lemma_
    if hasattr(x, "text"):
        return x.text
    return str(x)


def extract_clauses(sent_text: str, sent_entities: list):
    doc = nlp(sent_text)
    # Workaround for clausie's recognizing non-verbal predicates
    verbs = {t.lemma_ for t in doc if t.pos_ == "VERB"}
    clauses = []

    # Helper function to filter only named entity subjects/objects
    def _ner_filter(text):
        for ent_text, ent_label, _, _ in sent_entities:
            if ent_text in text:
                return ent_label
        return None

    for c in doc._.clauses:
        for spans in c.to_propositions(as_text=False):
            subj, pred, *args = spans
            pred_text = _to_text(pred)
            subj_text = _to_text(subj)
            obj_text = " ".join(_to_text(a) for a in args) if args else ""
            # Filter out clauses without verbs (non-verbal predicates)
            if pred_text not in verbs:
                continue
            # Filter out clauses without named entity subjects/objects
            subj_label = _ner_filter(subj_text)
            obj_label = _ner_filter(obj_text)

            # Keep clauses with SPO structure where both subject and object are named entities
            if subj_label and obj_label:
                clauses.append((subj_text, pred.text, obj_text))
    return clauses


def process(text: str):
    # First perform NER on the entire text for better context
    entities = [
        (ent["word"], ent["entity_group"], ent["start"], ent["end"])
        for ent in ner(text)
    ]
    logger.info(f"Extracted Entities: {entities}")
    doc = nlp(text)
    tagged_clauses = []

    # Split text into sentences using spacy
    for sent in doc.sents:
        sent_start = sent.start_char
        sent_end = sent.end_char
        sent_text = sent.text

        sent_entities = []
        for word, label, start, end in entities:
            if start >= sent_start and end <= sent_end:
                # adjust indices relative to the sentence
                rel_start = start - sent_start
                rel_end = end - sent_start
                sent_entities.append((word, label, rel_start, rel_end))

        clauses = extract_clauses(sent_text, sent_entities)
        logger.info(f"Extracted Clauses for sentence '{sent_text}': {clauses}")

        # Helper function to tag entities in the clauses with NER tags
        def _tag_entity(text, entities):
            for ent_text, ent_label, _, _ in entities:
                if ent_text in text:
                    text = f"<{ent_label}>{ent_text}</{ent_label}>"
            return text

        for subj, pred, obj in clauses:
            subj_tagged = _tag_entity(subj, sent_entities)
            obj_tagged = _tag_entity(obj, sent_entities)
            tagged_clauses.append((subj_tagged, pred, obj_tagged))

    return tagged_clauses
