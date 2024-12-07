import pathlib
import json
import logging
from pydantic import ValidationError
import datetime

from .utils.helpers import (
    list_files_in_folder,
    read_raw_data,
    save_file_as_json,
    sort_and_group_by_journal,
    journal_with_max_distinct_drugs,
    get_all_journals_by_drug,
    get_all_drugs_by_journals,
)
from .config import (
    PUBTRIALS_FILE_NAMES,
    DRUGS_FILE_NAMES,
)
from .models import PubClinical, Drug, CrossReference

now = datetime.datetime.now().strftime("%Y_%m_%d")


def curate_pubclinical_data(
    raw_pubtrials_data_files: list[pathlib.Path],
) -> tuple[list[PubClinical], list[str]]:
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
    valid_drugs_data = []
    errors = []
    for file in raw_drugs_data_files:
        for row in read_raw_data(file, fieldnames=["atccode", "drug"]):
            try:
                valid_drugs_data.append(Drug(**row))
            except ValidationError as e:
                logging.error(f"Drug row {row} failed validation: {e}")
                errors.append(row)
    return valid_drugs_data, errors


def cross_reference_models(
    pubclinical_data: list[PubClinical], drugs_data: list[Drug]
) -> tuple[list[CrossReference], list[str]]:
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
