from pathlib import Path

import pytest
import tempfile
import json
import csv



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
        with open(csv_file, 'w', newline='') as csvfile:
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
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=indent)
        return json_file
    return _create_temp_json_file



