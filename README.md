# Automated Knowledge Graph Construction from Text

This project extracts structured knowledge triples from unstructured text using NLP and knowledge graph technologies. It combines coreference resolution, named entity recognition, Wikidata entity linking, and property matching/prediction to build subject-predicate-object (SPO) triples suitable for knowledge graph construction.

## Pipeline Overview

- **Input:** Raw text (e.g., `"Marie Curie and Albert Einstein were both awarded Nobel Prizes."`)
- **Coreference Resolution:** Replaces pronouns and references with their corresponding named entities using [fastcoref](https://github.com/allenai/fastcoref) and spaCy libraries.
- **Named Entity Recognition & Clause Extraction:** Identifies entities and extracts SPO clauses using HuggingFace Transformers and spaCy dependency parsing.
- **Wikidata Entity Linking:** Maps extracted entity labels to Wikidata QIDs via the Wikidata API by using exact label/alias matching and embedding similarity with thresholding.
- **Relationship Extraction:** Finds the best Wikidata property for each subject-object pair using BERT-based semantic similarity and Wikidata property constraint matching.
- **Output:** List of triples: `<subject_uri, property, object_uri>`

## File Structure

- `main.py` — Entry point for running the pipeline.
- `src/pipeline.py` — Main pipeline orchestrating all steps.
- `src/steps/coreference_resolver.py` — Coreference resolution logic.
- `src/steps/ner_processor.py` — NER and clause extraction.
- `src/util/qid_retriever.py` — Wikidata entity linking.
- `src/steps/relationship_extraction/relationship_extractor.py` — Property prediction and triple extraction.
- `src/util/precompute_embeddings.py` — Embedding precomputation for properties and constraints.
- `src/util/sparql_service.py` — SPARQL queries for Wikidata property metadata.
- `src/config/config.py` — Central configuration and logger setup.

## Setup

### 1. Create Conda Environment

```bash
conda env create -f environment.yml
conda activate aied
```

### 2. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### 3. Prepare Data

- Run `src/util/sparql_service.py` to download Wikidata property metadata and constraints.
- Run `src/util/precompute_embeddings.py` to generate property and constraint embeddings.

### 4. Run the Pipeline

Edit `main.py` and provide your input text:

```python
from src import pipeline

text = "Marie Curie and Albert Einstein were both awarded Nobel Prizes."
triples = pipeline.extract_triples(text)
```

Then run:

```bash
python main.py
```

## Requirements

See [`environment.yml`](environment.yml) for dependencies.

## Output

Extracted triples are logged and can be used for downstream knowledge graph construction or analysis.