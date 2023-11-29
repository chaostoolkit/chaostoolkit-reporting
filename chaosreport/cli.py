# -*- coding: utf-8 -*-
import os
from glob import glob
from typing import Any, Dict, List

import click
from chaoslib import convert_vars

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
):
    """
    Generate a report from the run journal(s).
    """
    header = generate_report_header(journal, export_format)
    report_path = report
    reports = []

    if len(journal) == 1 and not os.path.isfile(journal[0]):
        journal = glob(journal)

    for journal in journal:
        reports.append(generate_report(journal, export_format, var, var_file))
    save_report(header, reports, report_path, export_format)
    click.echo("Report generated as '{f}'".format(f=report))
