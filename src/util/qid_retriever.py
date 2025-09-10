from src.config.config import logger, WIKIDATA_API_URL
from src.util.sparql_service import execute_request_with_retries


def get_wikidata_qid(entity_label, language="en"):
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
        qid = data["search"][0]["id"]
        logger.info(f"QID for {entity_label}: {qid}")
        return qid, f"http://www.wikidata.org/entity/{qid}"

    logger.warning(f"No QID found for {entity_label}")
    return None, None
