# -*- coding: utf-8 -*-
from base64 import b64encode
from datetime import datetime, timedelta
import io
import json
from math import pi
import os
import os.path
import tempfile

import cairosvg
from chaoslib.types import Journal
import dateparser
from jinja2 import Environment, PackageLoader, select_autoescape
from logzero import logger
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import maya
from natural import date
import pygal
from pygal.style import DefaultStyle
import pypandoc

__all__ = ["__version__", "generate_report"]
__version__ = '0.2.0'

curdir = os.getcwd()
basedir = os.path.dirname(__file__)
css_dir = os.path.join(basedir, "template", "css")
js_dir = os.path.join(basedir, "template", "js")


def generate_report(journal_path: str, report_path: str,
                    export_format: str = "markdown"):
    """
    Generate a report document from a chaostoolkit journal.

    The report is first generated from the markdown template and converted to
    the desired format using Pandoc.
    """
    with io.open(journal_path) as fp:
        journal = json.load(fp)

    # inject some pre-processed values into the journal for rendering
    experiment = journal["experiment"]
    journal["chaoslib_version"] = journal["chaoslib-version"]
    journal["hypo"] = experiment["steady-state-hypothesis"]
    journal["num_probes"] = len(list(
        filter(lambda a: a["type"] == "probe", experiment["method"])))
    journal["num_actions"] = len(list(
        filter(lambda a: a["type"] == "action", experiment["method"])))
    journal["human_duration"] = str(timedelta(seconds=journal["duration"]))
    journal["export_format"] = export_format
    journal["today"] = datetime.now().strftime("%d %B %Y")

    generate_chart_from_metric_probes(journal, export_format)

    env = Environment(
        loader=PackageLoader('chaosreport', 'template')
    )
    env.filters["pretty_date"] = lambda d: str(maya.MayaDT.from_datetime(
        dateparser.parse(d)))
    env.globals["pretty_duration"] = lambda d0, d1: date.delta(
        dateparser.parse(d0), dateparser.parse(d1), words=False)[0]
    template = env.get_template("index.md")
    report = template.render(journal)

    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8') as fp:
        fp.write(report)
        fp.seek(0)
        extra_args = [
            "--self-contained",
            "--standalone",
            "--toc",
            "--smart",
            "--highlight-style", "pygments",
            "--from", "markdown-markdown_in_html_blocks+raw_html",
            "--css", os.path.join(css_dir, "normalize.min.css"),
            "--css", os.path.join(css_dir, "main.css")
        ]
        pypandoc.convert_file(
            fp.name, to=export_format, format='md', outputfile=report_path,
            extra_args=extra_args)


def generate_chart_from_metric_probes(journal: Journal, export_format: str):
    """
    Generate charts from probes that pulled data out of Prometheus. The charts
    are serialized to SVG (for HTML reports) and PNG (for PDF reports).
    """
    for run in journal["run"]:
        if run["status"] != "succeeded":
            continue

        if run["activity"]["type"] != "probe":
            continue

        output = run.get("output")
        if not isinstance(output, dict):
            continue

        data = output.get("data")
        if data:
            result_type = data.get("resultType")
            if result_type == "matrix":

                chart = pygal.Line(
                    x_label_rotation=20, style=DefaultStyle,
                    show_minor_x_labels=False, legend_at_bottom=True)

                initialized = False
                for result in data["result"]:
                    metric = result["metric"]
                    values = result.get("values")

                    # same data for each sequence of values
                    if not initialized:
                        initialized = True
                        chart.title = metric["__name__"]

                        x = []
                        fromts = datetime.utcfromtimestamp
                        for value in values:
                            x.append(
                                fromts(value[0]).strftime(
                                    '%Y-%m-%d\n %H:%M:%S'))

                        chart.x_labels = x
                        chart.x_labels_major = x[::10]

                    y = []
                    for value in values:
                        y.append(int(value[1]))

                    if "method" in metric:
                        y_label = "{m} {p} - {s}".format(
                            m=metric["method"], p=metric["path"],
                            s=metric["status"])
                    elif "pod" in metric:
                        y_label = metric["pod"]
                    else:
                        y_label = metric["instance"]

                    chart.add(y_label, y)

                if export_format in ["html", "html5"]:
                    run["chart"] = chart.render(disable_xml_declaration=True)
                else:
                    run["chart"] = b64encode(
                        cairosvg.svg2png(bytestring=chart.render(), dpi=72)
                    ).decode("utf-8")
