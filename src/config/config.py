import logging

# Configuration variables
SPACY_MODEL = "en_core_web_sm"
BERT_MODEL = "all-MiniLM-L6-v2"
NER_MODEL = "dslim/bert-large-NER"
PROPERTIES_FILE = "src/data/wikidata_properties.csv"
CONSTRAINTS_FILE = "src/data/wikidata_constraints.csv"
PROPERTIES_WITH_EMB_FILE = "src/data/properties_with_emb.pkl"
CONSTRAINTS_WITH_EMB_FILE = "src/data/constraints_with_emb.pkl"

MAX_DEPTH = 3
TOP_K = 5

WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"
WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"

DEFAULT_USER_AGENT = "Text2KG/1.0 (contact: marko.putnikovic@gmail.com)"
USER_AGENTS = [
    DEFAULT_USER_AGENT,
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) Firefox/115.0",
]

TIMEOUT = 30
MAX_RETRIES = 3
BASE_DELAY = 5  # seconds
BATCH_SIZE = 25
SLEEP_BETWEEN_BATCHES = 5  # seconds

# Logger configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("aied")