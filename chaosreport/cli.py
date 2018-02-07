# -*- coding: utf-8 -*-
import click
from logzero import logger

from chaosreport import generate_report

__all__ = ["cli"]


@click.command()
@click.option('--export-format', default="markdown",
              help='Format to export the report to: html, markdown, pdf.')
@click.argument('journal', type=click.Path(exists=True))
@click.argument('report', type=click.Path(exists=False))
def report(export_format: str="markdown", journal: str="journal.json",
           report: str="report.md"):
    """
    Generate a report from the run journal.
    """
    generate_report(journal, report, export_format)
    click.echo("Report generated as '{f}'".format(f=report))
