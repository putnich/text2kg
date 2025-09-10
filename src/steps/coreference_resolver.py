import spacy
from fastcoref import spacy_component
from src.config.config import logger, SPACY_MODEL


def process(text: str):
    # Load spacy with fastcoref
    nlp = spacy.load(SPACY_MODEL)
    nlp.add_pipe("fastcoref")

    doc = nlp(text)

    replacements = []

    for cluster in doc._.coref_clusters:
        name = text[cluster[0][0] : cluster[0][1]]
        logger.info(f"Name: {name}")
        logger.info(f"Coreference cluster: {cluster}")

        for i in range(1, len(cluster)):
            start, end = cluster[i][0], cluster[i][1]
            replacements.append((start, end, name))

    logger.info(f"Replacements: {replacements}")
    for start, end, name in sorted(replacements, key=lambda x: x[0], reverse=True):
        text = text[:start] + name + text[end:]
    return text
