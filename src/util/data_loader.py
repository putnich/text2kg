import csv
import pandas as pd
from src.config.config import (
    logger,
    PROPERTIES_FILE,
    CONSTRAINTS_FILE,
    PROPERTIES_WITH_EMB_FILE,
    CONSTRAINTS_WITH_EMB_FILE,
)


def parse_constraints(constraint_string):
    constraints = []
    for item in constraint_string.split("; "):
        if "#" in item:
            qid = item.split("#")[-1].split("/")[-1]  # Extract only the QID
            constraints.append(qid)
    return constraints


def load_property_data():
    logger.info("Loading property data from CSV files.")

    properties = {}
    constraints = {}

    with open(PROPERTIES_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            properties[row["property"].split("/")[-1]] = {
                "label": row["label"],
                "description": row.get("description", ""),
                "aliases": row.get("aliases", "").split(", "),
            }

    with open(CONSTRAINTS_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            constraints[row["property"].split("/")[-1]] = {
                "subjectConstraints": parse_constraints(row["subjectConstraints"]),
                "valueConstraints": parse_constraints(row["valueConstraints"]),
                "statements": row.get("statements", ""),
            }

    logger.info(
        f"Loaded {len(properties)} properties and {len(constraints)} constraints."
    )
    return properties, constraints


def load_embedding_data():
    logger.info("Loading precomputed embedding data.")

    properties_df = pd.read_pickle(PROPERTIES_WITH_EMB_FILE)
    constraints_df = pd.read_pickle(CONSTRAINTS_WITH_EMB_FILE)

    logger.info(
        f"Loaded {len(properties_df)} properties and {len(constraints_df)} constraints with embeddings."
    )
    return properties_df, constraints_df
