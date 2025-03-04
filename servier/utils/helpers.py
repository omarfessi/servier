import csv
import itertools
import json
import logging
import pathlib
from typing import (
    Iterable,
    Iterator,
    List,
)

from ..config import (
    PUBTRIALS_FIELD_NAMES,
    SUPPORTED_EXTENSIONS,
)


def list_files_in_folder(
    landing_zone: pathlib.Path, supported_file_names: list[str]
) -> list[pathlib.Path]:
    """
    List specific files in a given folder.
    This function iterates through all files in the specified landing zone directory,
    checks if each file is a regular file and if its name is in the PUBTRIALS list.
    Args:
        landing_zone (pathlib.Path): The path to the directory to be scanned.
        supported_file_names (list[str]): A list of file names to be searched for.
    Returns:
        list[pathlib.Path]: A list of pathlib.Path objects representing the files
                            that meet the specified conditions.
    """
    files = []
    for file in landing_zone.iterdir():
        if file.is_file() and file.name in supported_file_names:
            files.append(file)
    return files


def read_csv(file: pathlib.Path, field_names: list[str]) -> Iterator[dict[str, str]]:
    """
    Reads a CSV file and yields each row as a dictionary with additional metadata.
    Args:
        file (pathlib.Path): The path to the CSV file.
        field_names (list[str]): A list of field names for the CSV columns.
    Yields:
        Iterator[dict[str, str]]: An iterator of dictionaries, each representing a row in the CSV file.
                                  Each dictionary contains the row data and additional metadata:
                                  - "source_file": The stem of the file name (without extension).
                                  - "source_file_type": The type of the source file ("csv").
    """

    with open(file, "r") as f:
        data = csv.DictReader(f, field_names)
        next(data)
        for row in data:
            yield ({**row, "source_file": file.stem, "source_file_type": "csv"})


def read_json(file: pathlib.Path) -> Iterator[dict[str, str]]:
    """
    Reads a JSON file and yields each row as a dictionary with additional metadata.
    Args:
        file (pathlib.Path): The path to the JSON file.
    Yields:
        Iterator[dict[str, str]]: An iterator of dictionaries, each representing a row in the JSON file,
                                  with added keys 'source_file' and 'source_file_type'.
                                  - "source_file": The stem of the file name (without extension).
                                  - "source_file_type": The type of the source file ("json").
    """

    with open(file, "r") as f:
        data = json.load(f)
        for row in data:
            yield ({**row, "source_file": file.stem, "source_file_type": "json"})


def read_raw_data(
    raw_data_file: pathlib.Path, field_names: list[str] = PUBTRIALS_FIELD_NAMES
) -> Iterator[dict[str, str]]:
    """
    Reads raw data from a file and returns an iterator of dictionaries.
    Args:
        raw_data_file (pathlib.Path): The path to the raw data file.
        field_names (list[str], optional): The list of field names for CSV files. Defaults to PUBTRIALS_FIELD_NAMES.
    Returns:
        Iterator[dict[str, str]]: An iterator of dictionaries containing the data.
    Raises:
        ValueError: If the file format is not supported.
        FileNotFoundError: If the file does not exist.
    """
    if raw_data_file.suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError("Unsupported file format")
    if not raw_data_file.is_file():
        raise FileNotFoundError(f"The file {raw_data_file} is not a file.")
    if raw_data_file.suffix == ".csv":
        return read_csv(raw_data_file, field_names)
    elif raw_data_file.suffix == ".json":
        return read_json(raw_data_file)


def save_file_as_json(dest_location: pathlib.Path, data: Iterable) -> None:
    """
    Save the given data to a JSON file at the specified destination location.
    Args:
        dest_location (pathlib.Path): The path where the JSON file will be saved.
        data (Iterable): The data to be saved in the JSON file.
    Returns:
        None
    """

    with open(dest_location, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, default=str, ensure_ascii=False)


def sort_and_group_by_journal(cross_reference_data: List[dict[str, str]]) -> Iterable:
    """
    Sorts a list of dictionaries by the 'journal' key and groups the dictionaries by the 'journal' key.
    Args:
        cross_reference_data (List[dict[str, str]]): A list of dictionaries where each dictionary contains a 'journal' key.
    Returns:
        Iterable: An iterable of tuples where the first element is the journal name and the second element is an iterator over the dictionaries grouped by that journal.
    """
    # sort by key is necessary because groupby generates a break or new group every time the value of the key function changes.
    cross_reference_data.sort(key=lambda x: x["journal"])
    groups = itertools.groupby(
        cross_reference_data,
        key=lambda x: x["journal"],
    )
    return groups


def journal_with_max_distinct_drugs(sorted_groups: Iterable) -> str:
    """
    Determines the journal that mentions the maximum number of distinct drugs.
    Args:
        sorted_groups (Iterable): An iterable of tuples where each tuple contains a journal name and a list of dictionaries.
                                  Each dictionary represents a drug entry with a "drug" key.
    Returns:
        str: The name of the journal that mentions the maximum number of distinct drugs.
    """

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
    """
    Retrieve a set of unique journal names that mention a specific drug.
    Args:
        data (list[dict[str, str]]): A list of dictionaries where each dictionary represents a document containing drug and journal information.
        drug (str): The name of the drug to search for in the documents.
    Returns:
        set[str]: A set of unique journal names that mention the specified drug.
    """

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
    """
    Retrieve a set of drugs mentioned in specified journals from the provided data.
    Args:
        data (List[dict[str, str]]): A list of dictionaries containing drug information.
        journals (List[str]): A list of journal names to filter the drugs by.
        **extra_filters: Additional filters to apply. Currently supports:
            - source_file (str): If provided, only include drugs from entries that match this source file (publication or clinical trials).
    Returns:
        set[str]: A set of drug names that are mentioned in the specified journals.
    """
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
