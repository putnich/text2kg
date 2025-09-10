import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer
from src.config.config import BERT_MODEL, PROPERTIES_FILE, CONSTRAINTS_FILE, logger

bert_model = SentenceTransformer(BERT_MODEL)


def normalize(emb):
    if emb is None:
        return None
    emb = np.asarray(emb)
    if emb.ndim == 1:
        return emb / np.linalg.norm(emb)
    return emb / np.linalg.norm(emb, axis=1, keepdims=True)


def get_list_embs(text_list, sep):
    if pd.isna(text_list):
        return None
    text_list = [s.strip() for s in text_list.split(sep) if s.strip()]
    if not text_list:
        return None
    emb = bert_model.encode(text_list, convert_to_numpy=True)
    return normalize(emb)


logger.info("Loading properties from %s", PROPERTIES_FILE)
properties = pd.read_csv(PROPERTIES_FILE)

logger.info("Encoding and normalizing property labels.")
properties["label_emb"] = normalize(
    bert_model.encode(properties["label"].fillna("").astype(str), convert_to_numpy=True)
).tolist()

logger.info("Encoding and normalizing property descriptions.")
properties["description_emb"] = normalize(
    bert_model.encode(
        properties["description"].fillna("").astype(str), convert_to_numpy=True
    )
).tolist()

logger.info("Encoding and normalizing property aliases.")
properties["aliases_emb"] = properties["aliases"].apply(get_list_embs, sep=",")

logger.info("Saving properties with embeddings to properties_with_emb.pkl")
properties.to_pickle("properties_with_emb.pkl")

logger.info("Loading constraints from %s", CONSTRAINTS_FILE)
constraints = pd.read_csv(CONSTRAINTS_FILE)

logger.info("Encoding and normalizing constraint statements.")
constraints["statements_emb"] = constraints["statements"].apply(get_list_embs, sep=".")

logger.info("Saving constraints with embeddings to constraints_with_emb.pkl")
constraints.to_pickle("constraints_with_emb.pkl")
