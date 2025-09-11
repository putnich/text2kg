import re

from src.steps import coreference_resolver
from src.steps import ner_processor
from src.util import qid_retriever
from src.util.data_loader import load_property_data, load_embedding_data
from src.steps.relationship_extraction import relationship_extractor

from src.config.config import logger

properties_data, constraints_data = load_property_data()
properties_with_emb, constraints_with_emb = load_embedding_data()

def extract_triples(text: str):

    coref_resolved_text = coreference_resolver.process(text)
    logger.info(f"Coreference Resolved Text: {coref_resolved_text}")

    tagged_spos = ner_processor.process(coref_resolved_text)
    logger.info(f"Extracted SPOS: {tagged_spos}")

    triples = []

    def strip_tags(texts):
        return [re.sub(r"</?[^>]+>", "", text) for text in texts]

    for spo in tagged_spos:
        logger.info(f"Processing SPO: {spo}")

        subj, pred, obj = strip_tags(spo)

        subj_qid = qid_retriever.get_wikidata_qid(subj)
        obj_qid = qid_retriever.get_wikidata_qid(obj)
        subj_uri = f"http://www.wikidata.org/entity/{subj_qid}" if subj_qid else None
        obj_uri = f"http://www.wikidata.org/entity/{obj_qid}" if obj_qid else None

        if subj_qid is None or obj_qid is None:
            logger.info("Skipping relationship extraction due to missing QID.")
            triples.append((subj_uri if subj_uri else subj, pred, obj_uri if obj_uri else obj))
            continue

        best_bert_property, constraints_matching_candidates = (
            relationship_extractor.extract_relationship(
                subj, subj_qid, obj, obj_qid, pred, properties_with_emb, constraints_with_emb
            )
        )

        triple = (subj_uri, best_bert_property, obj_uri)

        if best_bert_property and triple not in triples:
            triples.append(triple)
            logger.info(
                f"Extracted Triple: <{subj_uri}, {best_bert_property}, {obj_uri}>"
            )
        else:
            logger.info("No suitable property found for the entity pair.")

    logger.info(f"Final Extracted Triples: {triples}")

    return triples
