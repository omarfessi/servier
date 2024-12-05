import pathlib
from typing import List, Iterator, Iterable
import csv, json
import itertools
from ..config import PUBTRIALS_FIELD_NAMES, SUPPORTED_EXTENSIONS
import logging


def list_files_in_folder(
    landing_zone: pathlib.Path, supported_file_names: list[str]
) -> list[pathlib.Path]:
    """
    List specific files in a given folder.
    This function iterates through all files in the specified landing zone directory,
    checks if each file is a regular file and if its name is in the PUBTRIALS list.
    Args:
        landing_zone (pathlib.Path): The path to the directory to be scanned.
    Returns:
        list[pathlib.Path]: A list of pathlib.Path objects representing the files
                            that meet the specified conditions.
    """
    files = []
    for file in landing_zone.iterdir():
        if file.is_file() and file.name in supported_file_names:
            files.append(file)
    return files


def read_csv(file: pathlib.Path) -> Iterator[dict[str, str]]:
    with open(file, "r") as f:
        data = csv.DictReader(f, PUBTRIALS_FIELD_NAMES)
        next(data)
        for row in data:
            yield ({**row, "source_file": file.stem, "source_file_type": "csv"})


def read_json(file: pathlib.Path) -> Iterator[dict[str, str]]:
    with open(file, "r") as f:
        data = json.load(f)
        for row in data:
            yield ({**row, "source_file": file.stem, "source_file_type": "json"})


def read_raw_data(raw_data_file: pathlib.Path) -> Iterator[dict[str, str]]:
    if raw_data_file.suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError("Unsupported file format")
    if not raw_data_file.is_file():
        raise
    if raw_data_file.suffix == ".csv":
        return read_csv(raw_data_file)
    elif raw_data_file.suffix == ".json":
        return read_json(raw_data_file)


def save_file_as_json(dest_location: pathlib.Path, data: Iterable) -> None:
    with open(dest_location, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, default=str, ensure_ascii=False)


def sort_and_group_by_journal(cross_reference_data: List[dict[str, str]]) -> Iterable:
    # sort by key is necessary because groupby generates a break or new group every time the value of the key function changes.

    cross_reference_data.sort(key=lambda x: x["journal"])
    groups = itertools.groupby(
        cross_reference_data,
        key=lambda x: x["journal"],
    )
    return groups


def journal_with_max_distinct_drugs(sorted_groups: Iterable) -> str:
    journals_with_distinct_drugs_count = []
    max_of_disctinct_drugs_mentionned_by_any_journal = 0
    for journal, data_grouped_by_journal in sorted_groups:
        list_of_drugs = [item["drug"] for item in data_grouped_by_journal]
        count_of_distinct_drugs_per_journal = len(set(list_of_drugs))
        if (
            count_of_distinct_drugs_per_journal
            > max_of_disctinct_drugs_mentionned_by_any_journal
        ):
            max_of_disctinct_drugs_mentionned_by_any_journal = (
                count_of_distinct_drugs_per_journal
            )
            journals_with_distinct_drugs_count.append(
                (journal, count_of_distinct_drugs_per_journal)
            )
    max = filter(
        lambda x: x[1] == max_of_disctinct_drugs_mentionned_by_any_journal,
        journals_with_distinct_drugs_count,
    )
    return list(max)[0]


def journal_with_most_distinct_drug_mentions(
    cross_reference_data_as_dict: List[dict[str, str]]
) -> dict:
    sorted_groups_by_journal = sort_and_group_by_journal(cross_reference_data_as_dict)
    the_journal = journal_with_max_distinct_drugs(sorted_groups_by_journal)
    return the_journal


def get_all_journals_by_drug(data: list[dict[str, str]], drug: str) -> set[str]:
    journals = []
    for doc in data:
        try:
            if doc["drug"].lower() == drug.lower().strip():
                journals.append(doc["journal"])
        except KeyError as e:
            logging.error(f"KeyError: {e}")
            continue

    return set(journals)


def get_all_drugs_by_journals(
    data: List[dict[str, str]], journals: List[str], **extra_filters
) -> set[str]:
    drugs = set()
    source_file = extra_filters.get("source_file")

    for doc in data:
        try:
            if doc["journal"] in journals:
                if source_file:
                    if doc.get("source_file") == source_file:
                        drugs.add(doc["drug"])
                else:
                    drugs.add(doc["drug"])
        except KeyError as e:
            logging.error(f"KeyError: {e}")
            continue

    return drugs
