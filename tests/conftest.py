import csv
import json

import pytest


@pytest.fixture
def temp_random_text_file(tmp_path):
    """Fixture to create a temporary text file with random content."""

    def _create_temp_random_text_file(file_name, content):
        text_file = tmp_path / file_name
        text_file.write_text(content)
        return text_file

    return _create_temp_random_text_file


@pytest.fixture
def temp_csv_file(tmp_path):
    """Fixture to create a temporary CSV file with sample data."""

    def _create_temp_csv_file(file_name, fieldnames, data):
        csv_file = tmp_path / file_name
        with open(csv_file, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        return csv_file

    return _create_temp_csv_file


@pytest.fixture
def temp_json_file(tmp_path):
    """Fixture to create a temporary JSON file with sample data."""

    def _create_temp_json_file(file_name, data, indent=4):
        json_file = tmp_path / file_name
        with open(json_file, "w") as f:
            json.dump(data, f, indent=indent)
        return json_file

    return _create_temp_json_file


@pytest.fixture
def silver_and_gold_paths(tmp_path):
    silver_zone_path = tmp_path / "silver_zone"
    silver_zone_path.mkdir()

    gold_zone_path = tmp_path / "gold_zone"
    gold_zone_path.mkdir()

    return silver_zone_path, gold_zone_path


@pytest.fixture
def cross_reference_sample_data():
    return [
        {
            "drug": "DIPHENHYDRAMINE",
            "journal": "Journal of emergency nursing",
            "mention_date": "2020-01-01",
            "source_file": "clinical_trials",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "DIPHENHYDRAMINE",
            "journal": "Journal of emergency nursing",
            "mention_date": "2020-01-01",
            "source_file": "clinical_trials",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "DIPHENHYDRAMINE",
            "journal": "Journal of emergency nursing",
            "mention_date": "2020-01-01",
            "source_file": "clinical_trials",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "DIPHENHYDRAMINE",
            "journal": "Journal of emergency nursing",
            "mention_date": "2019-01-01",
            "source_file": "pubmed",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "DIPHENHYDRAMINE",
            "journal": "Journal of emergency nursing",
            "mention_date": "2019-01-01",
            "source_file": "pubmed",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "DIPHENHYDRAMINE",
            "journal": "The Journal of pediatrics",
            "mention_date": "2019-02-01",
            "source_file": "pubmed",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "TETRACYCLINE",
            "journal": "Journal of food protection",
            "mention_date": "2020-01-01",
            "source_file": "pubmed",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "TETRACYCLINE",
            "journal": "American journal of veterinary research",
            "mention_date": "2020-02-01",
            "source_file": "pubmed",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "TETRACYCLINE",
            "journal": "Psychopharmacology",
            "mention_date": "2020-01-01",
            "source_file": "pubmed",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "ETHANOL",
            "journal": "Psychopharmacology",
            "mention_date": "2020-01-01",
            "source_file": "pubmed",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "ATROPINE",
            "journal": "The journal of maternal-fetal & neonatal medicine",
            "mention_date": "2020-01-03",
            "source_file": "pubmed",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "EPINEPHRINE",
            "journal": "Journal of emergency nursing",
            "mention_date": "2020-04-27",
            "source_file": "clinical_trials",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "EPINEPHRINE",
            "journal": "The journal of allergy and clinical immunology. In practice",
            "mention_date": "2020-01-02",
            "source_file": "pubmed",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "EPINEPHRINE",
            "journal": "The journal of allergy and clinical immunology. In practice",
            "mention_date": "2020-01-03",
            "source_file": "pubmed",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "ISOPRENALINE",
            "journal": "Journal of photochemistry and photobiology. B, Biology",
            "mention_date": "2020-01-01",
            "source_file": "pubmed",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "BETAMETHASONE",
            "journal": "Hôpitaux Universitaires de Genève",
            "mention_date": "2020-01-01",
            "source_file": "clinical_trials",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "BETAMETHASONE",
            "journal": "The journal of maternal-fetal & neonatal medicine",
            "mention_date": "2020-01-01",
            "source_file": "pubmed",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "BETAMETHASONE",
            "journal": "Journal of back and musculoskeletal rehabilitation",
            "mention_date": "2020-01-01",
            "source_file": "pubmed",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
        {
            "drug": "BETAMETHASONE",
            "journal": "The journal of maternal-fetal & neonatal medicine",
            "mention_date": "2020-01-03",
            "source_file": "pubmed",
            "ingestion_timestamp": "2024-11-11 03:10:01.566374",
        },
    ]
