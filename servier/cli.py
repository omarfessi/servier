import click
import pathlib

from .config import (
    DISPLAY_PATHS,
    PUBLICATIONS,
    DRUGS,
    SILVER_ZONE,
    GOLD_ZONE,
    CORRUPTED_DATA_ZONE,
)
from .main import (
    _main_pipeline,
    _journal_with_max_drugs,
    _get_drugs_from_journals_that_mention_a_specific_drug,
)


@click.group()
def cli():
    pass


@click.command()
@click.option(
    "--raw-pubclinical-data",
    type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path),
    default=PUBLICATIONS,
    show_default=f"'{DISPLAY_PATHS['PUBLICATIONS']}'",
    help="Path to the raw pubclinical data.",
)
@click.option(
    "--raw-drug-data",
    type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path),
    default=DRUGS,
    show_default=f"'{DISPLAY_PATHS['DRUGS']}'",
    help="Path to the raw drug data.",
)
@click.option(
    "--silver_zone_path",
    type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path),
    default=SILVER_ZONE,
    show_default=f"'{DISPLAY_PATHS['SILVER_ZONE']}'",
    help="Path to the silver zone.",
)
@click.option(
    "--trash_zone_path",
    type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path),
    default=CORRUPTED_DATA_ZONE,
    show_default=f"'{DISPLAY_PATHS['CORRUPTED_DATA_ZONE']}'",
    help="Path to the trash zone for corrupted data.",
)
def main_pipeline(
    raw_pubclinical_data, raw_drug_data, silver_zone_path, trash_zone_path
) -> None:
    """Main pipeline to process data."""
    click.echo(f"Processing pubclinical data from {raw_pubclinical_data}")
    click.echo(f"Processing drug data from {raw_drug_data}")
    click.echo(f"Storing results in {silver_zone_path}")

    _main_pipeline(
        raw_pubclinical_data, raw_drug_data, silver_zone_path, trash_zone_path
    )


@click.command()
@click.option(
    "--silver-zone-path",
    type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path),
    default=SILVER_ZONE,
    show_default=f"'{DISPLAY_PATHS['SILVER_ZONE']}'",
    help="Path to the silver zone.",
)
@click.option(
    "--gold-zone-path",
    type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path),
    default=GOLD_ZONE,
    show_default=f"'{DISPLAY_PATHS['GOLD_ZONE']}'",
    help="Path to the gold zone.",
)
def journal_with_max_drugs(
    silver_zone_path: pathlib.Path, gold_zone_path: pathlib.Path
) -> None:
    _journal_with_max_drugs(silver_zone_path, gold_zone_path)


@click.command()
@click.argument("drug_name", type=str)
@click.option(
    "--silver-zone-path",
    type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path),
    default=SILVER_ZONE,
    show_default=f"'{DISPLAY_PATHS['SILVER_ZONE']}'",
    help="Path to the silver zone.",
)
@click.option(
    "--gold-zone-path",
    type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path),
    default=GOLD_ZONE,
    show_default=f"'{DISPLAY_PATHS['GOLD_ZONE']}'",
    help="Path to the gold zone.",
)
def get_drugs_from_journals_that_mention_a_specific_drug(
    silver_zone_path: pathlib.Path, gold_zone_path: pathlib.Path, drug_name: str
) -> None:
    _get_drugs_from_journals_that_mention_a_specific_drug(
        silver_zone_path, gold_zone_path, drug_name
    )


cli.add_command(main_pipeline)
cli.add_command(journal_with_max_drugs)
cli.add_command(get_drugs_from_journals_that_mention_a_specific_drug)
