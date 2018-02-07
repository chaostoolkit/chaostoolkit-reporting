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
import semver

__all__ = ["__version__", "generate_report"]
__version__ = '0.6.0'

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
    journal["hypo"] = experiment.get("steady-state-hypothesis")
    journal["num_probes"] = len(list(
        filter(lambda a: a["type"] == "probe", experiment["method"])))
    journal["num_actions"] = len(list(
        filter(lambda a: a["type"] == "action", experiment["method"])))
    journal["human_duration"] = str(timedelta(seconds=journal["duration"]))
    journal["export_format"] = export_format
    journal["today"] = datetime.now().strftime("%d %B %Y")

    generate_chart_from_metric_probes(journal, export_format)
    template = get_report_template(journal["chaoslib-version"])
    report = template.render(journal)

    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8') as fp:
        fp.write(report)
        fp.seek(0)
        extra_args = [
            "--self-contained",
            "--standalone",
            "--toc",
            "--highlight-style", "pygments",
            "--from", "markdown-markdown_in_html_blocks+raw_html",
            "--css", os.path.join(css_dir, "normalize.min.css"),
            "--css", os.path.join(css_dir, "main.css")
        ]
        pypandoc.convert_file(
            fp.name, to=export_format, format='md', outputfile=report_path,
            extra_args=extra_args)


def get_report_template(report_version: str):
    """
    Retrieve and return the most appropriate template based on the
    chaostoolkit-lib version used when running the experiment.
    """
    env = Environment(
        loader=PackageLoader('chaosreport', 'template')
    )
    env.filters["pretty_date"] = lambda d: str(maya.MayaDT.from_datetime(
        dateparser.parse(d)))
    env.globals["pretty_duration"] = lambda d0, d1: date.delta(
        dateparser.parse(d0), dateparser.parse(d1), words=False)[0]

    templates = []
    for name in env.list_templates(["md"]):
        if name == "index.md":
            continue

        _, _, v = name.split('_')
        v, _ = v.rsplit('.md', 1)
        templates.append((semver.parse_version_info(v), name))

    templates = sorted(templates, key=lambda vinfo: vinfo[0])

    for (vinfo, name) in templates:
        if semver.match(
            report_version, "<={v}".format(v=semver.format_version(
                **vinfo._asdict()))):
            return env.get_template(name)

    # none of the old versions matched, we can use the latest template
    return env.get_template("index.md")


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

                # we may have series with different x length, so we try to
                # generate a set of all seen abscisses
                x = set([])
                for result in data["result"]:
                    values = result.get("values")
                    for value in values:
                        x.add(value[0])

                # now we have our range of abscissa, let's map those
                # timestamps to formatted strings
                x = sorted(list(x))
                fromts = datetime.utcfromtimestamp
                chart.x_labels = [
                    fromts(v).strftime('%Y-%m-%d\n %H:%M:%S') for v in x]
                chart.x_labels_major = chart.x_labels[::10]

                metric = data["result"][0]["metric"]
                chart.title = metric["__name__"]

                for result in data["result"]:
                    # initialize first to null values to handle missing data
                    y = [None] * len(x)

                    # next, we update the y with actual values
                    values = result.get("values")
                    for value in values:
                        x_idx = x.index(value[0])
                        y[x_idx] = int(value[1])

                    metric = result["metric"]
                    if "method" in metric:
                        y_label = "{m} {p} - {s}".format(
                            m=metric["method"], p=metric["path"],
                            s=metric["status"])
                    elif "pod" in metric:
                        y_label = metric["pod"]
                    else:
                        y_label = metric["instance"]
                    chart.add(y_label, y, allow_interruptions=True)

                if export_format in ["html", "html5"]:
                    run["chart"] = chart.render(disable_xml_declaration=True)
                else:
                    run["chart"] = b64encode(
                        cairosvg.svg2png(bytestring=chart.render(), dpi=72)
                    ).decode("utf-8")
