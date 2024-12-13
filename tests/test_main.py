import json
import pathlib

from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
    has_length,
)

from servier.main import (
    _get_drugs_from_journals_that_mention_a_specific_drug,
    cross_reference_models,
    curate_drugs_data,
    curate_pubclinical_data,
)
from servier.models import (
    Drug,
    PubClinical,
)


def test_curate_pubclinical_data_valid(mocker):
    valid_pubclinical_data = {
        "title": "DIPHENHYDRAMINE",
        "date": "2020-01-01",
        "journal": "Journal of emergency nursing",
        "source_file": "clinical_trials",
        "source_file_type": "csv",
    }
    expected = PubClinical(**valid_pubclinical_data)
    mock_read_raw_data = mocker.patch("servier.main.read_raw_data")
    mock_read_raw_data.return_value = [valid_pubclinical_data]
    raw_pubtrials_data_files = [pathlib.Path("test_pubtrials_valid.csv")]
    valid_pubtrials_data, errors = curate_pubclinical_data(raw_pubtrials_data_files)
    assert_that(valid_pubtrials_data, has_length(1))
    assert_that(valid_pubtrials_data[0], equal_to(expected))
    assert_that(errors, has_length(0))


def test_curate_pubclinical_data_not_all_valid(mocker):
    valid_pubtrials_data_list = [
        {
            "title": "",
            "journal": "Heart Journal",
            "date": "2023-01-01",
            "source_file": "file1",
            "source_file_type": "csv",
        },
        {
            "title": "random title 2",
            "journal": "Pain Journal",
            "date": "2023-01-02",
            "source_file": "file2",
            "source_file_type": "csv",
        },
    ]
    expected_list = [PubClinical(**valid_pubtrials_data_list[1])]
    mock_read_raw_data = mocker.patch("servier.main.read_raw_data")
    mock_read_raw_data.return_value = valid_pubtrials_data_list
    raw_pubtrials_data_files = [pathlib.Path("test_pubtrials.csv")]
    valid_pubtrials_data, errors = curate_pubclinical_data(raw_pubtrials_data_files)
    assert_that(valid_pubtrials_data, contains_inanyorder(*expected_list))
    assert_that(errors, has_length(1))


def test_curate_drugs_data_valid(mocker):
    valid_drugs_data_list = [
        {
            "atccode": "A04AD",
            "drug": "DIPHENHYDRAMINE",
            "source_file": "file1",
            "source_file_type": "csv",
        },
        {
            "atccode": "R01AD",
            "drug": "BETAMETHASONE",
            "source_file": "file2",
            "source_file_type": "csv",
        },
    ]

    expected_list = [Drug(**drug) for drug in valid_drugs_data_list]

    mock_read_raw_data = mocker.patch("servier.main.read_raw_data")
    mock_read_raw_data.return_value = valid_drugs_data_list
    raw_drugs_data_files = [pathlib.Path("test_drugs_valid.csv")]
    valid_drugs_data, errors = curate_drugs_data(raw_drugs_data_files)
    assert_that(valid_drugs_data, contains_inanyorder(*expected_list))
    assert_that(errors, has_length(0))


def test_curate_drugs_data_not_all_valid(mocker):
    expected_list = [
        {
            "atccode": "",
            "drug": "DRUGNAME",
            "source_file": "file1",
            "source_file_type": "csv",
        },
        {
            "atccode": "ABCD",
            "drug": "DRUGNAME",
            "source_file": "file2",
            "source_file_type": "csv",
        },
    ]
    mock_read_raw_data = mocker.patch("servier.main.read_raw_data")
    mock_read_raw_data.return_value = expected_list
    raw_drugs_data_files = [
        pathlib.Path("test_drugs.csv"),
    ]
    expected_list = [Drug(**expected_list[1])]
    valid_drugs_data, errors = curate_drugs_data(raw_drugs_data_files)
    assert_that(valid_drugs_data, contains_inanyorder(*expected_list))
    assert_that(errors, has_length(1))


def test_cross_reference_models():
    pubclinical_data = [
        PubClinical(
            title="Aspirin in heart disease",
            journal="Heart Journal",
            date="2023-01-01",
            source_file="file1v",
            source_file_type="csv",
        ),
        PubClinical(
            title="Ibuprofen in pain management",
            journal="Pain Journal",
            date="2023-01-02",
            source_file="file2",
            source_file_type="json",
        ),
    ]
    drugs_data = [
        Drug(atccode="A01", drug="Aspirin"),
        Drug(atccode="A02", drug="Ibuprofen"),
    ]
    cross_reference_data, errors = cross_reference_models(pubclinical_data, drugs_data)
    assert_that(cross_reference_data, has_length(2))
    assert_that(errors, has_length(0))


class TestGetDrugsFromJournalsThatMentionASpecificDrug:
    def test_get_drugs_from_journals_that_mention_a_specific_drug(
        self,
        temp_json_file,
        cross_reference_sample_data,
        silver_and_gold_paths,
    ):
        # Given
        json_file_name = "cross_reference_data_test.json"
        silver_zone_path, gold_zone_path = silver_and_gold_paths

        specific_drug = "DIPHENHYDRAMINE"
        expected_drugs = ["DIPHENHYDRAMINE"]

        temp_json_file(silver_zone_path / json_file_name, cross_reference_sample_data)
        # When
        _get_drugs_from_journals_that_mention_a_specific_drug(
            silver_zone_path, gold_zone_path, specific_drug
        )
        # Then
        output_files = list(
            gold_zone_path.glob(f"drugs_by_journals_by_{specific_drug}_*.json")
        )
        assert len(output_files) == 1

        with open(output_files[0], "r") as f:
            drugs = json.load(f)

        assert_that(drugs, equal_to(expected_drugs))

    def test_get_drugs_from_journals_that_mention_a_specific_drug_with_unknown_drug(
        self,
        temp_json_file,
        cross_reference_sample_data,
        silver_and_gold_paths,
    ):
        # Given
        specific_drug = "UNKNOWN_DRUG"
        json_file_name = "cross_reference_data_test.json"
        silver_zone_path, gold_zone_path = silver_and_gold_paths

        temp_json_file(silver_zone_path / json_file_name, cross_reference_sample_data)

        # When
        _get_drugs_from_journals_that_mention_a_specific_drug(
            silver_zone_path, gold_zone_path, specific_drug
        )
        # Then
        output_files = list(
            gold_zone_path.glob(f"drugs_by_journals_by_{specific_drug}_*.json")
        )
        assert len(output_files) == 0

    def test_get_drugs_from_journals_that_mention_a_specific_drug_with_multiple_mentions(
        self, temp_json_file, cross_reference_sample_data, silver_and_gold_paths
    ):
        # Given
        specific_drug = "BETAMETHASONE"
        expected_drugs = ["BETAMETHASONE", "ATROPINE"]
        json_file_name = "cross_reference_data_test.json"
        silver_zone_path, gold_zone_path = silver_and_gold_paths
        temp_json_file(silver_zone_path / json_file_name, cross_reference_sample_data)

        # When
        _get_drugs_from_journals_that_mention_a_specific_drug(
            silver_zone_path, gold_zone_path, specific_drug
        )
        # Then
        output_files = list(
            gold_zone_path.glob(f"drugs_by_journals_by_{specific_drug}_*.json")
        )
        with open(output_files[0], "r") as f:
            drugs = json.load(f)

        assert_that(expected_drugs, contains_inanyorder(*drugs))
