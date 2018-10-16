# -*- coding: utf-8 -*-
from glob import glob
import os

import click
from logzero import logger

from chaosreport import generate_report, generate_report_header, save_report

__all__ = ["cli"]


@click.command()
@click.option('--export-format', default="markdown",
              help='Format to export the report to: html, markdown, pdf.')
@click.argument('journal', type=click.Path(exists=True), nargs=-1)
@click.argument('report', type=click.Path(exists=False), nargs=1)
def report(export_format: str = "markdown", journal: str = "journal.json",
           report: str = "report.md"):
    """
    Generate a report from the run journal(s).
    """
    header = generate_report_header(journal, export_format)
    report_path = report
    reports = []

    if len(journal) == 1 and not os.path.isfile(journal[0]):
        journal = glob(journal)

    for journal in journal:
        reports.append(generate_report(journal, export_format))
    save_report(header, reports, report_path, export_format)
    click.echo("Report generated as '{f}'".format(f=report))
