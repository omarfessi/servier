import pathlib
import pytest
from pydantic import ValidationError
from servier.main import (
    curate_pubclinical_data,
    curate_drugs_data,
    cross_reference_models,
)
from servier.models import PubClinical, Drug, CrossReference
from servier.utils.helpers import read_raw_data


def test_curate_pubclinical_data_valid(mocker):
    mock_read_raw_data = mocker.patch("servier.main.read_raw_data")
    mock_read_raw_data.side_effect = [
        [
            {
                "title": "DIPHENHYDRAMINE",
                "date": "2020-01-01",
                "journal": "Journal of emergency nursing",
                "source_file": "clinical_trials",
                "source_file_type": "csv",
            }
        ]
    ]
    raw_pubtrials_data_files = [pathlib.Path("test_pubtrials_valid.csv")]
    valid_pubtrials_data, errors = curate_pubclinical_data(raw_pubtrials_data_files)
    assert len(valid_pubtrials_data) > 0
    assert len(errors) == 0


def test_curate_pubclinical_data_invalid(mocker):
    mock_read_raw_data = mocker.patch("servier.main.read_raw_data")
    mock_read_raw_data.side_effect = [
        [
            {
                "title": "",
                "journal": "Heart Journal",
                "date": "2023-01-01",
                "source_file": "file1.csv",
            }
        ],
        [
            {
                "title": "",
                "journal": "Pain Journal",
                "date": "2023-01-02",
                "source_file": "file2.csv",
            }
        ],
    ]
    raw_pubtrials_data_files = [
        pathlib.Path("test_pubtrials_invalid.csv"),
        pathlib.Path("test_pubtrials_invalid_2.csv"),
    ]
    valid_pubtrials_data, errors = curate_pubclinical_data(raw_pubtrials_data_files)
    assert len(valid_pubtrials_data) == 0
    assert len(errors) > 0


def test_curate_drugs_data_valid(mocker):
    mock_read_raw_data = mocker.patch("servier.main.read_raw_data")
    mock_read_raw_data.side_effect = [
        [
            {
                "title": "Aspirin in heart disease",
                "journal": "Heart Journal",
                "date": "2023-01-01",
                "source_file": "file1.csv",
            }
        ],
        [
            {
                "title": "Ibuprofen in pain management",
                "journal": "Pain Journal",
                "date": "2023-01-02",
                "source_file": "file2.csv",
            }
        ],
    ]
    raw_drugs_data_files = [
        pathlib.Path("test_drugs_valid.csv"),
        pathlib.Path("test_drugs_valid_2.csv"),
    ]
    valid_drugs_data, errors = curate_drugs_data(raw_drugs_data_files)
    assert len(valid_drugs_data) > 0
    assert len(errors) == 0


def test_curate_drugs_data_invalid(mocker):
    mock_read_raw_data = mocker.patch("servier.utils.helpers.read_raw_data")
    mock_read_raw_data.side_effect = [
        [
            {
                "title": "",
                "journal": "Heart Journal",
                "date": "2023-01-01",
                "source_file": "file1.csv",
            }
        ],
        [
            {
                "title": "",
                "journal": "Pain Journal",
                "date": "2023-01-02",
                "source_file": "file2.csv",
            }
        ],
    ]
    raw_drugs_data_files = [
        pathlib.Path("test_drugs_invalid.csv"),
        pathlib.Path("test_drugs_invalid_2.csv"),
    ]
    valid_drugs_data, errors = curate_drugs_data(raw_drugs_data_files)
    assert len(valid_drugs_data) == 0
    assert len(errors) > 0


def test_cross_reference_models():
    pubclinical_data = [
        PubClinical(
            title="Aspirin in heart disease",
            journal="Heart Journal",
            date="2023-01-01",
            source_file="file1.csv",
        ),
        PubClinical(
            title="Ibuprofen in pain management",
            journal="Pain Journal",
            date="2023-01-02",
            source_file="file2.csv",
        ),
    ]
    drugs_data = [
        Drug(atccode="A01", drug="Aspirin"),
        Drug(atccode="A02", drug="Ibuprofen"),
    ]
    cross_reference_data, errors = cross_reference_models(pubclinical_data, drugs_data)
    assert len(cross_reference_data) == 2
    assert len(errors) == 0
