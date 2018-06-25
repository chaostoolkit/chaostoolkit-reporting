# -*- coding: utf-8 -*-
from base64 import b64encode
from datetime import datetime, timedelta
import io
import itertools
import json
from math import pi
import os
import os.path
import shlex
import shutil
import subprocess
import tempfile

import cairosvg
from chaoslib.types import Experiment, Journal, Run
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
__version__ = '0.8.0'

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
    add_contribution_model(experiment)
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
    Generate charts from probes that pulled data. The charts
    are serialized to SVG (for HTML reports) or PNG (for PDF reports).
    """
    for run in journal["run"]:
        if run["status"] != "succeeded":
            continue

        provider = run["activity"]["provider"]
        activity_type = run["activity"]["type"]

        if provider["type"] == "python":
            if "chaosprometheus" in provider["module"] and \
                    activity_type == "probe":
                generate_chart_from_prometheus(run, export_format)

        elif provider["type"] == "process":
            path = provider["path"]
            if "vegeta" in path:
                generate_from_vegeta_result(run, export_format)


def generate_chart_from_prometheus(run: Run, export_format: str):
    """
    Generate charts from probes that pulled data out of Prometheus. The charts
    are serialized to SVG (for HTML reports) and PNG (for PDF reports).
    """
    output = run.get("output")
    if not isinstance(output, dict):
        return

    data = output.get("data")
    if data:
        result_type = data.get("resultType")
        if result_type == "matrix":

            chart = pygal.Line(
                x_label_rotation=20, style=DefaultStyle, truncate_legend=-1,
                show_minor_x_labels=False, legend_at_bottom=True,
                legend_at_bottom_columns=1)

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
            chart.title = "Query -  {}".format(
                run["activity"]["provider"]["arguments"]["query"])

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
                    y_label = "_".join(
                        [v for k, v in metric.items() if k != '__name__'])
                chart.add(y_label, y, allow_interruptions=True)

            if export_format in ["html", "html5"]:
                run["charts"] = [chart.render(disable_xml_declaration=True)]
            else:
                run["charts"] = [
                    b64encode(
                        cairosvg.svg2png(bytestring=chart.render(), dpi=72)
                    ).decode("utf-8")
                ]


def generate_from_vegeta_result(run: Run, export_format: str):
    """
    Generate charts from probes that pulled data out of Prometheus. The charts
    are serialized to SVG (for HTML reports) and PNG (for PDF reports).
    """
    vegeta_path = shutil.which("vegeta")
    if not vegeta_path:
        logger.warning("Failed to find the 'vegeta' binary in PATH")
        return

    provider = run["activity"]["provider"]
    args = provider.get("arguments")
    if not args:
        return

    if isinstance(args, str):
        args = shlex.split(args)
    elif isinstance(args, dict):
        args = itertools.chain.from_iterable(args.items())
        args = list([str(p) for p in args if p not in (None, "")])

    if "attack" not in args:
        return

    result_path = None
    for idx, t in enumerate(args):
        if t.startswith("-output="):
            result_path = t[8:]
            break
        elif t.startswith("-output"):
            result_path = args[idx+1]
            break

    if not result_path:
        return

    if not os.path.exists(result_path):
        logger.warning("vegeta result path could not be found: {}".format(
            result_path))
        return

    cmd = "{} report -inputs={} -reporter=text".format(
        vegeta_path, result_path)
    try:
        proc = subprocess.run(
            cmd, timeout=10, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True, check=True)
    except subprocess.CalledProcessError as x:
        logger.error("vegeta reporter failed: {}".format(str(x)))
    except subprocess.TimeoutExpired:
        logger.error("vegeta reporter took too long to complete")
    else:
        run["text"] = proc.stdout.decode('utf-8')

    cmd = "{} dump -inputs={} -dumper=json".format(
        vegeta_path, result_path)
    try:
        proc = subprocess.run(
            cmd, timeout=10, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True, check=True)
    except subprocess.CalledProcessError as x:
        logger.error("vegeta reporter failed: {}".format(str(x)))
    except subprocess.TimeoutExpired:
        logger.error("vegeta dumper took too long to complete")
    else:
        calls = proc.stdout.decode('utf-8').strip().replace("\n", ",")
        data = json.loads("[{}]".format(calls))

        def latency_chart() -> pygal.Line:
            chart = pygal.Line(
                    x_label_rotation=20, style=DefaultStyle, logarithmic=True,
                    show_minor_x_labels=False, legend_at_bottom=False)
            chart.title = "HTTP Latency"
            chart.y_title = "Latency (in ms)"
            chart.x_labels = [call["timestamp"] for call in data]
            num_entries = len(chart.x_labels)
            step = 10
            if num_entries > 100:
                step = 200
            elif num_entries > 1000:
                step = 2000
            chart.x_labels_major = chart.x_labels[::step]

            y_values = {}
            for index, call in enumerate(data):
                code = str(call["code"])
                if code not in y_values:
                    y_values[code] = [None] * num_entries

                latency = call["latency"] / 1000000.
                y_values[code].insert(index, latency)

            for code, latencies in y_values.items():
                chart.add(code, latencies, allow_interruptions=True)

            return chart

        def status_distribution() -> pygal.Bar:
            chart = pygal.Bar(
                x_label_rotation=20, style=DefaultStyle,
                show_minor_x_labels=False, legend_at_bottom=False)
            chart.title = "Distribution of HTTP Responses Per Second"
            chart.y_title = "Status Code Count"

            status_intervals = {}
            for call in data:
                ts = call["timestamp"]
                dt = dateparser.parse(ts)
                by_second_dt = dt.replace(microsecond=0).isoformat()
                if by_second_dt not in status_intervals:
                    status_intervals[by_second_dt] = {}

                code = call["code"]
                if code not in status_intervals[by_second_dt]:
                    status_intervals[by_second_dt][code] = 0
                status_intervals[by_second_dt][code] = \
                    status_intervals[by_second_dt][code] + 1

            chart.x_labels = list(status_intervals.keys())
            chart.x_labels_major = chart.x_labels[::5]

            num_entries = len(chart.x_labels)
            y_values = {}
            for index, interval in enumerate(status_intervals):
                for code, count in status_intervals[interval].items():
                    if code not in y_values:
                        y_values[code] = [None] * num_entries
                    y_values[code].insert(index, count)

            for code, count in y_values.items():
                chart.add(str(code), count, allow_interruptions=True)

            return chart

        def add_chart(chart: pygal.Graph):
            if "charts" not in run:
                run["charts"] = []

            if export_format in ["html", "html5"]:
                run["charts"].append(
                    chart.render(disable_xml_declaration=True))
            else:
                run["charts"].append(b64encode(
                    cairosvg.svg2png(bytestring=chart.render(), dpi=72)
                ).decode("utf-8"))

        add_chart(latency_chart())
        add_chart(status_distribution())


def add_contribution_model(experiment: Experiment):
    """
    Expose the contribution of that experiment to the report.

    As this is part of an extension, we bubble it up to the experiment itself
    for rendering purpose.
    """
    for extension in experiment.get("extensions", []):
        contributions = extension.get("contributions")
        if contributions:
            experiment["contributions"] = contributions
            break
