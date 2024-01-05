# -*- coding: utf-8 -*-
import io
import json
import os
from glob import glob
from typing import Any, Dict, List

import click
from chaoslib import convert_vars, merge_vars
from chaoslib.configuration import load_configuration
from chaoslib.secret import load_secrets

from chaosreport import generate_report, generate_report_header, save_report

__all__ = ["report"]


def validate_vars(
    ctx: click.Context, param: click.Option, value: List[str]
) -> Dict[str, Any]:
    """
    Process all `--var key=value` and return a dictionary of them with the
    value converted to the appropriate type.
    """
    try:
        return convert_vars(value)
    except ValueError as x:
        raise click.BadParameter(str(x))


@click.command()
@click.option(
    "--title",
    help="Title to use in the header of the report",
)
@click.option(
    "--export-format",
    default="markdown",
    help="Format to export the report to: html, markdown, pdf.",
)
@click.option(
    "--var",
    multiple=True,
    callback=validate_vars,
    help="Specify substitution values for configuration only. Can "
    "be provided multiple times. The pattern must be "
    "key=value or key:type=value. In that latter case, the "
    "value will be casted as the specified type. Supported "
    "types are: int, float, bytes. No type specified means "
    "a utf-8 decoded string.",
)
@click.option(
    "--var-file",
    multiple=True,
    type=click.Path(exists=True),
    help="Specify files that contain configuration and secret "
    "substitution values. Either as a json/yaml payload where "
    "each key has a value mapping to a configuration entry. "
    "Or a .env file defining environment variables. "
    "Can be provided multiple times.",
)
@click.argument("journal", type=click.Path(exists=True), nargs=-1)
@click.argument("report", type=click.Path(exists=False), nargs=1)
def report(
    export_format: str = "markdown",
    var: Dict[str, Any] = None,
    var_file: List[str] = None,
    journal: str = "journal.json",
    report: str = "report.md",
    title: str = None,
):
    """
    Generate a report from the run journal(s).
    """
    header = generate_report_header(journal, export_format, title)
    report_path = report
    reports = []

    if len(journal) == 1 and not os.path.isfile(journal[0]):
        journal = glob(journal)

    for journal_path in journal:
        with io.open(journal_path) as fp:
            j = json.load(fp)

        experiment = j["experiment"]
        config_vars, secret_vars = merge_vars(var, var_file) or (None, None)
        config = load_configuration(
            experiment.get("configuration", {}), config_vars
        )
        secrets = load_secrets(experiment.get("secrets", {}), secret_vars)

        reports.append(generate_report(j, export_format, config, secrets))

    save_report(header, reports, report_path, export_format)
    click.echo("Report generated as '{f}'".format(f=report))
