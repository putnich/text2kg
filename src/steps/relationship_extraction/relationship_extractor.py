from src.config.config import logger, MAX_DEPTH, TOP_K
from src.util.data_loader import load_property_data
from src.steps.relationship_extraction.constraints_matching import (
    match_entities_to_properties,
)
from src.steps.relationship_extraction.property_ranking import rank_properties_with_bert


def extract_relationship(subj_text, subject_qid, obj_text, object_qid, pred_text, properties, constraints):

    clause = f"{subj_text} {pred_text} {obj_text}"
    (
        bert_ranked_by_label,
        bert_ranked_by_description,
        bert_ranked_by_aliases,
        bert_ranked_by_statements,
    ) = rank_properties_with_bert(clause, pred_text, properties, constraints)

    logger.info(
        f"Top {TOP_K} BERT-ranked properties (by label): {bert_ranked_by_label}"
    )

    logger.info(
        f"Top {TOP_K} BERT-ranked properties (by description): {bert_ranked_by_description}"
    )

    logger.info(
        f"Top {TOP_K} BERT-ranked properties (by statements): {bert_ranked_by_statements}"
    )

    logger.info(
        f"Top {TOP_K} BERT-ranked properties (by aliases): {bert_ranked_by_aliases}"
    )

    constraint_matched_properties = match_entities_to_properties(
        subject_qid, object_qid, constraints, MAX_DEPTH
    )

    candidates = (
        bert_ranked_by_label
        + bert_ranked_by_description
        + bert_ranked_by_statements
        + bert_ranked_by_aliases
    )
    if not candidates:
        logger.warning("No BERT-ranked properties available; skipping.")
        return None, constraint_matched_properties

    best_bert_property = max(candidates, key=lambda x: x[1])[0]

    logger.info(f"Final selected property (BERT): {best_bert_property}")
    logger.info(f"Domain/range matching properties: {constraint_matched_properties}")

    return best_bert_property, constraint_matched_properties
