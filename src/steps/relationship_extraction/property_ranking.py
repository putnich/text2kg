import numpy as np
import pandas as pd


from src.config.config import (
    logger,
    BERT_MODEL,
    TOP_K,
)
from sentence_transformers import SentenceTransformer


bert_model = SentenceTransformer(BERT_MODEL)


def rank_properties_with_bert(clause, pred_text, properties_df, constraints_df):
    logger.info("Ranking candidate properties using BERT.")

    label_embs = np.vstack(properties_df["label_emb"].to_numpy())

    description_embs = np.vstack(properties_df["description_emb"].to_numpy())

    clause_emb = bert_model.encode(clause, convert_to_numpy=True)

    pred_emb = bert_model.encode(pred_text, convert_to_numpy=True)

    sims_by_label = label_embs @ pred_emb
    sims_by_description = description_embs @ clause_emb

    sorted_idx_by_label = np.argsort(-sims_by_label)
    ranked_by_label = [
        (properties_df.iloc[i]["property"], float(sims_by_label[i]))
        for i in sorted_idx_by_label
    ]

    sorted_idx_by_description = np.argsort(-sims_by_description)
    ranked_by_description = [
        (properties_df.iloc[i]["property"], float(sims_by_description[i]))
        for i in sorted_idx_by_description
    ]

    ranked_by_statements = []

    for _, row in constraints_df.iterrows():
        embs = row["statements_emb"]

        if embs is None or len(embs) == 0:
            continue
        sims = embs @ clause_emb
        max_sim = float(np.max(sims))
        ranked_by_statements.append((row["property"], max_sim))
    ranked_by_statements.sort(key=lambda x: x[1], reverse=True)

    ranked_by_aliases = []
    for _, row in properties_df.iterrows():
        embs = row["aliases_emb"]

        if embs is None or len(embs) == 0:
            continue
        sims = embs @ pred_emb
        max_sim = float(np.max(sims))
        ranked_by_aliases.append((row["property"], max_sim))
    ranked_by_aliases.sort(key=lambda x: x[1], reverse=True)

    return (
        ranked_by_label[:TOP_K],
        ranked_by_description[:TOP_K],
        ranked_by_aliases[:TOP_K],
        ranked_by_statements[:TOP_K],
    )
