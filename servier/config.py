import pathlib

ROOT_DIR = pathlib.Path(__file__).parents[1]
LANDING_ZONE = ROOT_DIR / "data" / "landing_zone"
SILVER_ZONE = ROOT_DIR / "data" / "silver_zone"
GOLD_ZONE = ROOT_DIR / "data" / "gold_zone"
CORRUPTED_DATA_ZONE = ROOT_DIR / "data" / "corrupted_data"
PUBLICATIONS = LANDING_ZONE / "publications_data"
DRUGS = LANDING_ZONE / "referential_data"
PUBTRIALS_FILE_NAMES = ["clinical_trials.csv", "pubmed.csv", "pubmed.json"]
SUPPORTED_EXTENSIONS = [".csv", ".json"]
DRUGS_FILE_NAMES = ["drugs.csv"]
PUBTRIALS_FIELD_NAMES = ["id", "title", "date", "journal"]
HEX_PATTERN = r"(\\x[0-9a-fA-F]{2})+"

# Custom paths for display in CLI help
DISPLAY_PATHS = {
    "PUBLICATIONS": "data/landing_zone/publications_data",
    "DRUGS": "data/landing_zone/referential_data",
    "SILVER_ZONE": "data/silver_zone",
    "GOLD_ZONE": "data/gold_zone",
    "CORRUPTED_DATA_ZONE": "data/corrupted_data",
}
