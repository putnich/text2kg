from src.config.config import logger, WIKIDATA_SPARQL_URL
from src.util.sparql_service import run_sparql
from src.config.query import build_class_query, build_superclass_query


superclass_cache = {}


def get_deeper_superclasses(qids):
    if not qids:
        return set()
    subclass_query = build_superclass_query(qids)
    data = run_sparql(WIKIDATA_SPARQL_URL, subclass_query, rotating_user_agent=False)

    new_superclasses = set()
    for item in data["results"]["bindings"]:
        if "superclass" in item:
            new_superclass = item["superclass"]["value"].split("/")[-1]
            if new_superclass not in qids:
                new_superclasses.add(new_superclass)

    return new_superclasses


def get_classes(qid):
    logger.info(f"Fetching classes for QID: {qid}")

    classes = set()

    sparql_query = build_class_query(qid)

    data = run_sparql(WIKIDATA_SPARQL_URL, sparql_query, rotating_user_agent=False)

    for item in data["results"]["bindings"]:
        if "class" in item:
            classes.add(item["class"]["value"].split("/")[-1])
    return list(classes)


def get_superclasses(qid, depth):
    logger.info(f"Fetching superclasses for QID: {qid} (depth={depth})")

    superclasses = set()

    # Direct expansion
    superclasses.update(get_deeper_superclasses([qid]))
    current_superclasses = set(superclasses)
    # Deeper expansions
    i = 1
    while i < depth:
        new_superclasses = get_deeper_superclasses(current_superclasses)
        # Remove already seen superclasses to avoid infinite loops due to cycles
        new_superclasses -= superclasses
        superclasses.update(new_superclasses)
        current_superclasses = new_superclasses
        i += 1

    logger.info(
        f"QID {qid} - Superclasses ({depth} levels): {len(superclasses)} found"
    )
    return list(superclasses)


def match_with_constraints(property_constraints, subject_classes, object_classes):
    matched_properties = []
    for prop, constraints in property_constraints.items():
        domain_classes = [
            cls.split("/")[-1] for cls in constraints.get("subjectConstraints", [])
        ]
        range_classes = [
            cls.split("/")[-1] for cls in constraints.get("valueConstraints", [])
        ]

        domain_match = any(cls in subject_classes for cls in domain_classes)
        range_match = any(cls in object_classes for cls in range_classes)

        if domain_match and range_match:
            matched_properties.append(prop)
    return matched_properties


def match_entities_to_properties(
    subject_qid, object_qid, property_constraints, max_depth
):

    subject_classes = [cls.split("/")[-1] for cls in get_classes(subject_qid)]
    object_classes = [cls.split("/")[-1] for cls in get_classes(object_qid)]

    matched_properties = match_with_constraints(
        property_constraints, subject_classes, object_classes
    )

    if not matched_properties:
        logger.warning(
            f"No matching properties found for direct Subject: {subject_classes} Object: {object_classes} classes"
        )
        logger.info("Expanding with superclasses...")
        subject_superclasses = [
            cls.split("/")[-1] for cls in get_superclasses(subject_qid, max_depth)
        ]
        object_superclasses = [
            cls.split("/")[-1] for cls in get_superclasses(object_qid, max_depth)
        ]
        matched_properties = match_with_constraints(
            property_constraints, subject_superclasses, object_superclasses
        )

    logger.info(f"Constraint matched properties: {matched_properties}")
    return matched_properties
