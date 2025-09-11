import numpy as np
from sentence_transformers import SentenceTransformer

from src.config.config import logger, WIKIDATA_API_URL, BERT_MODEL
from src.util.sparql_service import execute_request_with_retries

bert_model = SentenceTransformer(BERT_MODEL)

def _label_similarity(entity_label: str, candidate_label: str) -> float:
    if not entity_label or not candidate_label:
        return 0.0
    entity_emb = bert_model.encode(entity_label, convert_to_numpy=True)
    candidate_emb = bert_model.encode(candidate_label, convert_to_numpy=True)
    similarity = float((entity_emb @ candidate_emb) / (np.linalg.norm(entity_emb) * np.linalg.norm(candidate_emb)))
    return similarity

def get_wikidata_qid(entity_label, language="en", threshold=0.7):
    logger.info(f"Fetching QID for entity: {entity_label}")
    params = {
        "action": "wbsearchentities",
        "search": entity_label,
        "language": language,
        "format": "json",
    }

    data = execute_request_with_retries(
        url=WIKIDATA_API_URL, params=params, rotating_user_agent=False
    )

    if "search" in data and len(data["search"]) > 0:
        result = data["search"][0]
        qid_candidate = result["id"]
        candidate_label = result.get("label", "")
        similarity = _label_similarity(entity_label, candidate_label)

        if similarity >= threshold:
            logger.info(f"QID for {entity_label}: {qid_candidate}")
            return qid_candidate
        else:
            logger.warning(f"No QID found for {entity_label}")
            return None
