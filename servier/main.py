import datetime
import json
import logging
import pathlib

from pydantic import ValidationError

from .config import (
    DRUGS_FILE_NAMES,
    PUBTRIALS_FILE_NAMES,
)
from .models import (
    CrossReference,
    Drug,
    PubClinical,
)
from .utils.helpers import (
    get_all_drugs_by_journals,
    get_all_journals_by_drug,
    journal_with_max_distinct_drugs,
    list_files_in_folder,
    read_raw_data,
    save_file_as_json,
    sort_and_group_by_journal,
)

now = datetime.datetime.now().strftime("%Y_%m_%d")


def curate_pubclinical_data(
    raw_pubtrials_data_files: list[pathlib.Path],
) -> tuple[list[PubClinical], list[str]]:
    """
    Curates raw clinical trial data from a list of files.

    This function reads raw clinical trial data from the provided list of file paths,
    validates each row, and returns a tuple containing a list of valid PubClinical
    objects and a list of rows that failed validation.

    Args:
        raw_pubtrials_data_files (list[pathlib.Path]): A list of file paths containing
            raw clinical trial data.

    Returns:
        tuple[list[PubClinical], list[str]]: A tuple where the first element is a list
            of valid PubClinical objects and the second element is a list of rows that
            failed validation.
    """
    valid_pubtrials_data = []
    errors = []
    for file in raw_pubtrials_data_files:
        for row in read_raw_data(file):
            try:
                valid_pubtrials_data.append(PubClinical(**row))
            except ValidationError as e:
                logging.error(f"Pubtrials row {row} failed validation: {e}")
                errors.append(row)
    return valid_pubtrials_data, errors


def curate_drugs_data(
    raw_drugs_data_files: list[pathlib.Path],
) -> tuple[list[Drug], list[str]]:
    """
    Curates raw drugs data from a list of file paths.

    This function reads raw drug data from the provided list of file paths,
    validates each row, and returns a tuple containing a list of valid Drug
    objects and a list of rows that failed validation.

    Args:
        raw_drugs_data_files (list[pathlib.Path]): A list of file paths containing raw drug data.

    Returns:
        tuple[list[Drug], list[str]]: A tuple where the first element is a list of valid Drug objects,
                                      and the second element is a list of rows that failed validation.
    """
    valid_drugs_data = []
    errors = []
    for file in raw_drugs_data_files:
        for row in read_raw_data(file, ["atccode", "drug"]):
            try:
                valid_drugs_data.append(Drug(**row))
            except ValidationError as e:
                logging.error(f"Drug row {row} failed validation: {e}")
                errors.append(row)
    return valid_drugs_data, errors


def cross_reference_models(
    pubclinical_data: list[PubClinical], drugs_data: list[Drug]
) -> tuple[list[CrossReference], list[str]]:
    """
    Cross-references clinical publications with drug data.
    This function takes a list of clinical publication data and a list of drug data,
    and cross-references them to find mentions of drugs in the publication titles.
    It returns a list of cross-referenced data and a list of errors encountered during the process.
    Args:
        pubclinical_data (list[PubClinical]): A list of PubClinical objects containing publication data.
        drugs_data (list[Drug]): A list of Drug objects containing drug data.
    Returns:
        tuple[list[CrossReference], list[str]]: A tuple containing two lists:
            - A list of CrossReference objects representing the cross-referenced data.
            - A list of strings representing errors encountered during the cross-referencing process.
    """

    cross_reference = []
    cross_reference_errors = []
    for drug in drugs_data:
        for pubclinical in pubclinical_data:
            if drug.drug.lower() in pubclinical.title.lower():
                row = {
                    "drug": drug.drug,
                    "journal": pubclinical.journal,
                    "mention_date": pubclinical.date,
                    "source_file": pubclinical.source_file,
                }
                try:
                    cross_reference.append(CrossReference(**row))
                except ValidationError as e:
                    logging.error(
                        f"Cross Reference Row with {row} failed validation: {e}"
                    )
                    cross_reference_errors.append(row)

    return cross_reference, cross_reference_errors


def _main_pipeline(
    raw_pubclinical_data, raw_drug_data, silver_zone_path, trash_zone_path
) -> None:
    """
    Executes the main data processing pipeline.
    This function performs the following steps:
    1. Lists and curates public clinical trial data files.
    2. Saves valid public clinical trial data to the silver zone.
    3. Saves any validation errors to the trash zone.
    4. Lists and curates drug data files.
    5. Saves valid drug data to the silver zone.
    6. Saves any validation errors to the trash zone.
    7. Cross-references the curated publication/clinical trial data with the curated drug data.
    8. Saves the cross-referenced data to the silver zone.
    9. Saves any cross-referencing errors to the trash zone.
    Args:
        raw_pubclinical_data (str): Path to the raw public clinical trial data.
        raw_drug_data (str): Path to the raw drug data.
        silver_zone_path (str): Path to the directory where valid data should be saved.
        trash_zone_path (str): Path to the directory where error data should be saved.
    Returns:
        None
    """
    pubtrials_data_files = list_files_in_folder(
        raw_pubclinical_data, PUBTRIALS_FILE_NAMES
    )
    valid_pubtrials_data, errors = curate_pubclinical_data(pubtrials_data_files)
    save_file_as_json(
        silver_zone_path / f"pubclinical_data_{now}.json",
        [item.model_dump() for item in valid_pubtrials_data],
    )
    if errors:
        save_file_as_json(
            trash_zone_path / f"pubclinical_validation_errors_{now}.json",
            errors,
        )
        del errors

    drugs_data_files = list_files_in_folder(raw_drug_data, DRUGS_FILE_NAMES)
    valid_drugs_data, errors = curate_drugs_data(drugs_data_files)

    save_file_as_json(
        silver_zone_path / f"drugs_data_{now}.json",
        [item.model_dump() for item in valid_drugs_data],
    )
    if errors:
        save_file_as_json(
            trash_zone_path / f"drugs_validation_errors_{now}.json",
            errors,
        )
        del errors

    cross_reference_data, errors = cross_reference_models(
        valid_pubtrials_data, valid_drugs_data
    )
    cross_reference_data_as_dict = [item.model_dump() for item in cross_reference_data]
    save_file_as_json(
        silver_zone_path / f"cross_reference_data_{now}.json",
        cross_reference_data_as_dict,
    )
    if errors:
        save_file_as_json(
            trash_zone_path / f"cross_reference_errors_{now}.json",
            errors,
        )
        del errors


def _journal_with_max_drugs(
    silver_zone_path: pathlib.Path, gold_zone_path: pathlib.Path
) -> None:
    """
    Identifies the journal with the maximum number of distinct drugs from the cross-reference data
    and saves the result to a JSON file in the gold zone path.
    Args:
        silver_zone_path (pathlib.Path): Path to the directory containing the silver zone data.
        gold_zone_path (pathlib.Path): Path to the directory where the result JSON file will be saved.
    Returns:
        None
    Logs:
        - Error if no cross-reference data is found in the silver zone path.
        - Error if the silver data format is unexpected.
    """
    try:
        file = list(silver_zone_path.glob("cross_reference_data_*.json"))[0]
    except IndexError:
        logging.error(
            "No cross reference data found, please run the main pipeline first"
        )
        return
    with open(file, "r") as f:
        data = json.load(f)
    try:
        sorted_groups_by_journal = sort_and_group_by_journal(data)
    except (TypeError, KeyError) as e:
        logging.error(f"Unexpected silver data format {e}")
    the_journal = journal_with_max_distinct_drugs(sorted_groups_by_journal)
    if the_journal:
        save_file_as_json(gold_zone_path / f"the_journal_{now}.json", the_journal)


def _get_drugs_from_journals_that_mention_a_specific_drug(
    silver_zone_path: pathlib.Path, gold_zone_path: pathlib.Path, drug_name: str
) -> None:
    """
    Extracts and saves a list of drugs mentioned in journals that reference a specified drug.
    This function reads cross-reference data from a JSON file in the silver zone directory,
    identifies journals that mention the specified drug, and then finds all drugs mentioned
    in those journals. The resulting list of drugs is saved as a JSON file in the gold zone directory.
    Args:
        silver_zone_path (pathlib.Path): Path to the directory containing the silver zone data.
        gold_zone_path (pathlib.Path): Path to the directory where the output JSON file will be saved.
        drug_name (str): The name of the drug to search for in the journals.
    Returns:
        None
    Logs:
        Error: If no cross-reference data is found or if there is an unexpected data format.
        Warning: If the specified drug is not mentioned in any journal.
    """
    try:
        file = list(silver_zone_path.glob("cross_reference_data_*.json"))[0]
    except IndexError:
        logging.error(
            "No cross reference data found, please run the main pipeline first"
        )
        return
    with open(file, "r") as f:
        data = json.load(f)
    try:
        journals = get_all_journals_by_drug(data, drug_name)
    except (TypeError, KeyError) as e:
        logging.error(f"Unexpected silver data format {e}")
    if not journals:
        logging.warning(f"DRUG : {drug_name} is not mentionned in any journal")
        return
    drugs_by_journals = get_all_drugs_by_journals(
        data, journals, **{"source_file": "pubmed"}
    )
    save_file_as_json(
        gold_zone_path / f"drugs_by_journals_by_{drug_name}_{now}.json",
        list(drugs_by_journals),
    )
