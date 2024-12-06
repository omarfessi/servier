from hamcrest import assert_that, equal_to, empty, contains_inanyorder, raises, calling
import pytest

from servier.utils.helpers import (
    get_all_journals_by_drug,
    get_all_drugs_by_journals,
    list_files_in_folder,
    read_raw_data,
)
from servier.config import PUBTRIALS_FILE_NAMES, PUBTRIALS_FIELD_NAMES


class TestGetAllJournalsByDrugs:
    def test_get_all_journals_by_drugs_must_return_set_of_journals(
        self, cross_reference_sample_data
    ):
        # Given
        specific_drug = "DIPHENHYDRAMINE"
        # When
        journals = get_all_journals_by_drug(cross_reference_sample_data, specific_drug)
        # Then
        assert_that(
            journals,
            equal_to(
                set(
                    (
                        "Journal of emergency nursing",
                        "The Journal of pediatrics",
                    )
                )
            ),
        )

    def test_get_all_journals_by_drugs_must_return_empty_set_when_drug_not_found(
        self, cross_reference_sample_data
    ):
        # Given
        specific_drug = "FAKE_DRUG"
        # When
        journals = get_all_journals_by_drug(cross_reference_sample_data, specific_drug)
        # Then
        assert_that(journals, empty())

    def test_get_all_journals_by_drugs_with_single_mention(
        self, cross_reference_sample_data
    ):
        # Given
        specific_drug = "ISOPRENALINE"
        # When
        journals = get_all_journals_by_drug(cross_reference_sample_data, specific_drug)
        # Then
        assert_that(
            journals,
            equal_to(set(("Journal of photochemistry and photobiology. B, Biology",))),
        )

    def test_get_all_journals_by_drugs_with_multiple_mentions(
        self, cross_reference_sample_data
    ):
        # Given
        specific_drug = "TETRACYCLINE"
        # When
        journals = get_all_journals_by_drug(cross_reference_sample_data, specific_drug)
        # Then
        assert_that(
            journals,
            equal_to(
                set(
                    (
                        "Journal of food protection",
                        "American journal of veterinary research",
                        "Psychopharmacology",
                    )
                )
            ),
        )

    def test_get_all_journals_by_drugs_with_no_mentions(
        self, cross_reference_sample_data
    ):
        # Given
        specific_drug = "UNKNOWN_DRUG"
        # When
        journals = get_all_journals_by_drug(cross_reference_sample_data, specific_drug)
        # Then
        assert_that(journals, empty())


class TestGetAllDrugsByJournals:
    @pytest.mark.parametrize(
        "journals, expected",
        [
            (["American journal of veterinary research"], ["TETRACYCLINE"]),
            (
                ["The journal of maternal-fetal & neonatal medicine"],
                ["ATROPINE", "BETAMETHASONE"],
            ),
            (["The Journal of pediatrics"], ["DIPHENHYDRAMINE"]),
            (
                ["Journal of back and musculoskeletal rehabilitation"],
                ["BETAMETHASONE"],
            ),
            (
                ["The journal of allergy and clinical immunology. In practice"],
                ["EPINEPHRINE"],
            ),
            (["Journal of food protection"], ["TETRACYCLINE"]),
            (
                ["Journal of emergency nursing"],
                ["EPINEPHRINE", "DIPHENHYDRAMINE"],
            ),
            (
                ["Journal of photochemistry and photobiology. B, Biology"],
                ["ISOPRENALINE"],
            ),
            (["Psychopharmacology"], ["ETHANOL", "TETRACYCLINE"]),
            (["Hôpitaux Universitaires de Genève"], ["BETAMETHASONE"]),
        ],
    )
    def test_get_all_drugs_by_journals_must_return_all_drugs_related(
        self, journals, expected, cross_reference_sample_data
    ):
        # When
        drugs = get_all_drugs_by_journals(
            cross_reference_sample_data, journals=journals
        )
        # Then
        assert_that(drugs, contains_inanyorder(*expected))

    def test_get_all_drugs_by_journals_with_source_file_filter(
        self, cross_reference_sample_data
    ):
        # Given
        journals = ["Journal of emergency nursing"]
        extra_filters = {"source_file": "clinical_trials"}
        expected = ["DIPHENHYDRAMINE", "EPINEPHRINE"]
        # When
        drugs = get_all_drugs_by_journals(
            cross_reference_sample_data, journals=journals, **extra_filters
        )
        # Then
        assert_that(drugs, contains_inanyorder(*expected))

    def test_get_all_drugs_by_journals_with_empty_journals_list(
        self, cross_reference_sample_data
    ):
        # Given
        journals = []
        # When
        drugs = get_all_drugs_by_journals(
            cross_reference_sample_data, journals=journals
        )
        # Then
        assert_that(drugs, empty())

    def test_get_all_drugs_by_journals_with_non_existent_journal(
        self, cross_reference_sample_data
    ):
        # Given
        journals = ["Non Existent Journal"]
        # When
        drugs = get_all_drugs_by_journals(
            cross_reference_sample_data, journals=journals
        )
        # Then
        assert_that(drugs, empty())


class TestListFilesInFolder:
    def test_list_files_in_folder_should_only_return_supported_file_names(
        self,
        tmp_path,
        temp_csv_file,
        temp_json_file,
        temp_random_text_file,
    ):
        # given
        data = [
            {
                "id": 1,
                "title": "FAKE_TITLE",
                "date": "2024-11-13",
                "journal": "Journal of emergency nursing",
            },
        ]
        csv_file = temp_csv_file("pubmed.csv", PUBTRIALS_FIELD_NAMES, data)
        json_file = temp_json_file("pubmed.json", data)
        txt_file = temp_random_text_file("dummy_file.txt", "FAKE_CONTENT")

        # When
        files = list_files_in_folder(tmp_path, PUBTRIALS_FILE_NAMES)

        # Assertions
        assert_that(txt_file, equal_to(tmp_path / "dummy_file.txt"))
        assert_that(files, contains_inanyorder(csv_file, json_file))

    def test_list_files_in_folder_should_return_empty_list_when_no_file_in_dir(
        self, tmp_path
    ):
        # When no file in the directory
        # Given
        files = list_files_in_folder(tmp_path, PUBTRIALS_FILE_NAMES)
        # Assertions
        assert_that(files, empty())


class TestReadRawData:
    def test_read_raw_data_should_raise_value_error_for_unsupported_file_format(
        self, tmp_path
    ):
        # Given
        unsupported_file = tmp_path / "unsupported_file.txt"
        unsupported_file.write_text("FAKE_CONTENT")

        # When / Then
        assert_that(
            calling(read_raw_data).with_args(unsupported_file),
            raises(ValueError, "Unsupported file format"),
        )

    def test_read_raw_data_should_return_csv_data(self, temp_csv_file):
        # Given
        data = [
            {
                "id": "1",
                "title": "FAKE_TITLE",
                "date": "2024-11-13",
                "journal": "Journal of emergency nursing",
            },
        ]
        csv_file = temp_csv_file("pubmed.csv", PUBTRIALS_FIELD_NAMES, data)
        expected_result = [
            {**row, "source_file": "pubmed", "source_file_type": "csv"} for row in data
        ]

        # When
        result = list(read_raw_data(csv_file))

        # Then
        assert_that(result, equal_to(expected_result))

    def test_read_raw_data_should_return_json_data(self, temp_json_file):
        # Given
        data = [
            {
                "id": "1",
                "title": "FAKE_TITLE",
                "date": "2024-11-13",
                "journal": "Journal of emergency nursing",
            },
        ]
        json_file = temp_json_file("pubmed.json", data)
        expected_result = [
            {**row, "source_file": "pubmed", "source_file_type": "json"} for row in data
        ]

        # When
        result = list(read_raw_data(json_file))

        # Then
        assert_that(result, equal_to(expected_result))
