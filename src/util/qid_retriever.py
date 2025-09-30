import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from src.config.config import logger, WIKIDATA_API_URL, BERT_MODEL
from src.util.sparql_service import execute_request_with_retries

bert_model = SentenceTransformer(BERT_MODEL)

def _cos(a: np.ndarray, b: np.ndarray) -> float:
    return float(cosine_similarity(a.reshape(1, -1), b.reshape(1, -1))[0, 0])

def _encode(texts):
    return bert_model.encode(texts, convert_to_numpy=True)

def _fetch_candidates(term: str, language: str, limit: int):
    params = {
        "action": "wbsearchentities",
        "search": term,
        "language": language,
        "format": "json",
        "limit": limit,
    }
    search = execute_request_with_retries(
        url=WIKIDATA_API_URL, params=params, rotating_user_agent=False
    )
    items = search.get("search", [])
    if not items:
        return []

    qids = [it["id"] for it in items]
    params = {
        "action": "wbgetentities",
        "ids": "|".join(qids),
        "props": "aliases|labels",
        "languages": language,
        "format": "json",
    }
    entities = execute_request_with_retries(
        url=WIKIDATA_API_URL, params=params, rotating_user_agent=False
    ).get("entities", {})

    out = []
    for item in items:
        qid = item["id"]
        ent = entities.get(qid, {})
        label = ent.get("labels", {}).get(language, {}).get("value", item.get("label", ""))
        aliases = [a["value"] for a in ent.get("aliases", {}).get(language, [])]
        out.append({"id": qid, "label": label, "aliases": aliases})
    return out

def get_wikidata_qid(entity_label, language="en", threshold=0.9):
    logger.info(f"Fetching QID for entity: {entity_label}")

    candidates = _fetch_candidates(entity_label, language=language, limit=10)
    if not candidates:
        logger.warning("No candidates found.")
        return None

    logger.info("Candidates from search: " + ", ".join(c.get("label", "") for c in candidates))

    entity_label = entity_label.lower().strip()

    for candidate in candidates:
        label_norm = candidate.get("label", "").lower().strip()
        if label_norm == entity_label:
            logger.info(f"Exact label match for '{entity_label}': {candidate['id']}")
            return candidate["id"]
        for alias in candidate.get("aliases", []):
            if alias.lower().strip() == entity_label:
                logger.info(f"Exact alias match for '{entity_label}': {candidate['id']}")
                return candidate["id"]

    entity_emb = _encode([entity_label])[0]
    scored = []
    for candidate in candidates:
        cand_label = candidate.get("label", "")
        aliases = candidate.get("aliases", [])

        label_sim = 0.0
        if cand_label:
            label_vec = _encode([cand_label])[0]
            label_sim = _cos(entity_emb, label_vec)

        alias_sims = []
        if aliases:
            alias_vecs = _encode(aliases)
            alias_sims = [_cos(entity_emb, av) for av in alias_vecs]

        alias_avg_sim = float(np.mean(alias_sims)) if alias_sims else 0.0

        scored.append(
            {
                "id": candidate["id"],
                "label": cand_label,
                "aliases": aliases,
                "label_sim": label_sim,
                "alias_avg_sim": alias_avg_sim
            }
        )

    scored.sort(key=lambda x: (x["alias_avg_sim"], x["label_sim"]), reverse=True)
    best_candidate = scored[0]

    if best_candidate["label_sim"] >= threshold:
        if best_candidate["alias_avg_sim"] == 0:
            logger.info(
                f"QID for {entity_label}: {best_candidate['id']} (label match)"
            )
            return best_candidate["id"]
        else:
            label_aliases_sim = np.mean(
                [best_candidate["label_sim"], best_candidate["alias_avg_sim"]]
            )
            if label_aliases_sim >= threshold:
                logger.info(
                    f"QID for {entity_label}: {best_candidate['id']} (label+alias match)"
                )
                return best_candidate["id"]

    logger.warning(f"No QID found for {entity_label}")
    return None
