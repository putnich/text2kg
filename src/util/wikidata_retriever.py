import os
import csv
import time


from src.util.sparql_service import run_sparql
from src.config.query import PROPERTIES_QUERY, build_constraints_query
from src.config.config import (
    logger,
    PROPERTIES_FILE,
    CONSTRAINTS_FILE,
    WIKIDATA_SPARQL_URL,
    BATCH_SIZE,
)


properties_results = run_sparql(
    WIKIDATA_SPARQL_URL, PROPERTIES_QUERY, rotating_user_agent=True
)

if properties_results:
    properties = {}
    with open(PROPERTIES_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=["property", "label", "description", "aliases"]
        )
        writer.writeheader()
        for result in properties_results["results"]["bindings"]:
            prop_id = result["property"]["value"]
            properties[prop_id] = {
                "property": prop_id,
                "label": result["propertyLabel"]["value"],
                "description": result.get("propertyDescription", {}).get("value", ""),
                "aliases": result.get("aliases", {}).get("value", ""),
            }
        writer.writerows(properties.values())

    logger.info(f"Properties saved to {PROPERTIES_FILE}")

existing_constraints = set()

if os.path.exists(CONSTRAINTS_FILE):
    with open(CONSTRAINTS_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            existing_constraints.add(row["property"])


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


new_constraint_entries = []
properties_to_query = [prop for prop in properties if prop not in existing_constraints]

for batch in chunks(properties_to_query, BATCH_SIZE):
    values_clause = " ".join(f"wd:{prop.split('/')[-1]}" for prop in batch)
    constraints_query = build_constraints_query(values_clause)

    properties_results = run_sparql(
        WIKIDATA_SPARQL_URL, constraints_query, rotating_user_agent=True
    )
    if properties_results:
        for res in properties_results["results"]["bindings"]:
            prop_id = res["property"]["value"]
            new_constraint_entries.append(
                {
                    "property": prop_id,
                    "statements": res.get("statementsLabels", {}).get("value", ""),
                    "subjectConstraints": res.get("subjectConstraints", {}).get(
                        "value", ""
                    ),
                    "valueConstraints": res.get("valueConstraints", {}).get(
                        "value", ""
                    ),
                }
            )

    with open(CONSTRAINTS_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "property",
                "statements",
                "subjectConstraints",
                "valueConstraints",
            ],
        )
        if (
            not os.path.exists(CONSTRAINTS_FILE)
            or os.stat(CONSTRAINTS_FILE).st_size == 0
        ):
            writer.writeheader()
        logger.info(
            f"Writing {len(new_constraint_entries)} new entries to {CONSTRAINTS_FILE}"
        )
        writer.writerows(new_constraint_entries)
    new_constraint_entries.clear()

    time.sleep(5)

logger.info(f"Finished storing data to {CONSTRAINTS_FILE}")
