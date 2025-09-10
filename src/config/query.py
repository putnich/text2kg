PROPERTIES_QUERY = """
        SELECT ?property ?propertyLabel ?propertyDescription 
        (GROUP_CONCAT(DISTINCT ?alias; separator=", ") AS ?aliases)
        WHERE {
        ?property a wikibase:Property .
        OPTIONAL { ?property schema:description ?propertyDescription FILTER(LANG(?propertyDescription) = "en"). }
        OPTIONAL { ?property skos:altLabel ?alias FILTER(LANG(?alias) = "en"). }
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
        }
        GROUP BY ?property ?propertyLabel ?propertyDescription
    """

CONSTRAINTS_QUERY_TEMPLATE = """
        SELECT ?property
               (GROUP_CONCAT(DISTINCT CONCAT(?subjectLabel, " ", ?propertyLabel, " ", ?objectLabel); separator=". ") AS ?statementsLabels)
               (GROUP_CONCAT(DISTINCT CONCAT(CONCAT(?subjectConstraintLabel), "#", STR(?subjectConstraint)); separator="; ") AS ?subjectConstraints)
               (GROUP_CONCAT(DISTINCT CONCAT(CONCAT(?valueConstraintLabel), "#", STR(?valueConstraint)); separator="; ") AS ?valueConstraints)
        WHERE {{
          VALUES ?property {{ {values_clause} }}
          
          OPTIONAL {{ 
            ?property p:P1855 ?statement. 
            ?statement ps:P1855 ?subject.
            BIND(IRI(REPLACE(STR(?property), "http://www.wikidata.org/entity/P", "http://www.wikidata.org/prop/qualifier/P")) AS ?qualifierProp).
            ?statement ?qualifierProp ?object.
          }}
          
           OPTIONAL {{
            ?property p:P2302 ?subjectConstraintStatement.  
            ?subjectConstraintStatement ps:P2302 wd:Q21503250.
            OPTIONAL {{ ?subjectConstraintStatement pq:P2308 ?subjectConstraint. }}
          }}
          
          OPTIONAL {{
            ?property p:P2302 ?valueConstraintStatement.  
            ?valueConstraintStatement ps:P2302 wd:Q21510865.
            OPTIONAL {{ ?valueConstraintStatement pq:P2308 ?valueConstraint. }}
          }}
          
          SERVICE wikibase:label {{ 
            bd:serviceParam wikibase:language "en".
            ?property rdfs:label ?propertyLabel.
            ?subject rdfs:label ?subjectLabel.
            ?object rdfs:label ?objectLabel.
            ?subjectConstraint rdfs:label ?subjectConstraintLabel.
            ?valueConstraint rdfs:label ?valueConstraintLabel.
          }}
        }}
        GROUP BY ?property
    """

CLASS_QUERY_TEMPLATE = """
        SELECT ?class WHERE {{
        wd:{qid} wdt:P31 ?class .
        }}
    """

SUPERCLASS_QUERY_TEMPLATE = """
    SELECT ?superclass WHERE {{
        VALUES ?class {{ {qids} }}
        ?class wdt:P279 ?superclass .
    }}
"""

def build_constraints_query(values_clause: str) -> str:
    return CONSTRAINTS_QUERY_TEMPLATE.format(values_clause=values_clause)

def build_class_query(qid: str) -> str:
    return CLASS_QUERY_TEMPLATE.format(qid=qid)

def build_superclass_query(qids: list) -> str:
    qids_str = ' '.join(f'wd:{q}' for q in qids)
    return SUPERCLASS_QUERY_TEMPLATE.format(qids=qids_str)