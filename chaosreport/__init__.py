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
from typing import List

import cairosvg
from chaoslib.caching import cache_activities, lookup_activity
from chaoslib.types import Experiment, Journal, Run
import dateparser
from jinja2 import Environment, PackageLoader, select_autoescape
from logzero import logger
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import maya
from natural import date
import pygal
from pygal.style import DefaultStyle, LightColorizedStyle
import pypandoc
import semver

__all__ = ["__version__", "generate_report", "generate_report_header",
           "save_report"]
__version__ = '0.12.0'

curdir = os.getcwd()
basedir = os.path.dirname(__file__)
css_dir = os.path.join(basedir, "template", "css")
js_dir = os.path.join(basedir, "template", "js")


def generate_report_header(journal_paths: List[str],
                           export_format: str = "markdown") -> str:
    header_template = get_report_template(None, "header.md")

    header_info = {}
    header_info["title"] = "Chaos Engineering Report"
    header_info["today"] = datetime.now().strftime("%d %B %Y")
    header_info["export_format"] = export_format
    tags = []

    contribution_labels = []
    contributions_by_experiment = []
    contributions_by_tag = []
    experiment_titles = []

    for journal_path in journal_paths:
        with io.open(journal_path) as fp:
            journal = json.load(fp)

        experiment = journal.get("experiment")
        experiment_tags = experiment.get("tags", [])
        tags.extend(experiment_tags)
        contribs = experiment.get("contributions")

        title = experiment["title"]
        experiment_titles.append(title)

        if not contribs:
            continue

        for contrib in contribs:
            contribution_labels.append(contrib)
            level = contribs[contrib]
            contributions_by_experiment.append((title, level, contrib))
            for tag in experiment_tags:
                contributions_by_tag.append((tag, level, contrib))

    number_of_contributions = len(set(contribution_labels))
    header_info["contributions"] = number_of_contributions > 0
    header_info["num_experiments"] = len(experiment_titles)
    header_info["tags"] = tags = set(tags)

    if number_of_contributions:
        unique_contributions = sorted(set(contribution_labels))
        header_info["num_distinct_contributions"] = number_of_contributions
        #######################################################################
        # Distribution chart
        #######################################################################
        dist_chart = pygal.Bar(
            print_values=True, print_values_position='top', show_legend=False,
            show_y_labels=False, legend_at_bottom=True)
        dist_chart.title = 'Organization Contributions Distribution'
        dist_chart.x_labels = unique_contributions
        dist_chart.add(
            "", [
                contribution_labels.count(contrib)
                for contrib in unique_contributions
            ])

        if export_format in ["html", "html5"]:
            header_info["contribution_distribution"] = dist_chart.render(
                    disable_xml_declaration=True)
        else:
            header_info["contribution_distribution"] = b64encode(
                cairosvg.svg2png(
                    bytestring=dist_chart.render(), dpi=72)).decode("utf-8")

        contribution_labels = list(unique_contributions)

        #######################################################################
        # Dot chart per experiment
        #######################################################################
        contributions = {}
        for title in experiment_titles:
            contributions[title] = [None] * number_of_contributions

        for (title, level, contrib) in contributions_by_experiment:
            idx = contribution_labels.index(contrib)
            amount = 0
            if level == "high":
                amount = 0.75
            elif level == "medium":
                amount = 0.50
            elif level == "low":
                amount = 0.25
            elif level == "none":
                amount = -0.1
            else:
                continue
            contributions[title][idx] = amount

        chart = pygal.Dot(
            legend_at_bottom_columns=1, show_y_labels=False,
            legend_at_bottom=True, show_legend=True, x_label_rotation=30,
            style=LightColorizedStyle, interpolate='hermite')
        chart.title = 'Experiment Contributions to Organization Properties'
        chart.x_labels = contribution_labels
        for title in contributions:
            chart.add(
                title, contributions[title], fill=False,
                allow_interruptions=True)

        if export_format in ["html", "html5"]:
            header_info["contributions_per_exp"] = chart.render(
                    disable_xml_declaration=True)
        else:
            header_info["contributions_per_exp"] = b64encode(
                cairosvg.svg2png(
                    bytestring=chart.render(), dpi=72)).decode("utf-8")

        chart = pygal.Radar(
            legend_at_bottom_columns=1, show_y_labels=False,
            legend_at_bottom=True, show_legend=True, x_label_rotation=30,
            style=LightColorizedStyle, interpolate='hermite')
        chart.title = 'Experiment Contributions to Organization Properties'
        chart.x_labels = contribution_labels
        for title in contributions:
            chart.add(
                title, contributions[title], fill=False,
                allow_interruptions=True)

        if export_format in ["html", "html5"]:
            header_info["contributions_per_exp_radar"] = chart.render(
                    disable_xml_declaration=True)
        else:
            header_info["contributions_per_exp_radar"] = b64encode(
                cairosvg.svg2png(
                    bytestring=chart.render(), dpi=72)).decode("utf-8")

        #######################################################################
        # Dot chart per tag
        #######################################################################
        contributions = {}
        for tag in tags:
            contributions[tag] = [None] * number_of_contributions

        for (tag, level, contrib) in contributions_by_tag:
            idx = contribution_labels.index(contrib)
            amount = 0
            if level == "high":
                amount = 0.75
            elif level == "medium":
                amount = 0.50
            elif level == "low":
                amount = 0.25
            elif level == "none":
                amount = -0.1
            else:
                continue
            contributions[tag][idx] = amount

        chart = pygal.Dot(
            show_legend=False, x_label_rotation=30, style=LightColorizedStyle,
            interpolate='hermite')
        chart.title = 'Organization Properties Coverage by Area'
        chart.x_labels = contribution_labels
        for tag in contributions:
            chart.add(
                tag, contributions[tag], fill=False, allow_interruptions=True)

        if export_format in ["html", "html5"]:
            header_info["contributions_per_tag"] = chart.render(
                    disable_xml_declaration=True)
        else:
            header_info["contributions_per_tag"] = b64encode(
                cairosvg.svg2png(
                    bytestring=chart.render(), dpi=72)).decode("utf-8")

    header = header_template.render(header_info)
    return header


def generate_report(journal_path: str, export_format: str = "markdown") -> str:
    """
    Generate a report document from a chaostoolkit journal.

    The report is first generated from the markdown template and converted to
    the desired format using Pandoc.
    """
    with io.open(journal_path) as fp:
        journal = json.load(fp)

    # inject some pre-processed values into the journal for rendering
    experiment = journal["experiment"]
    cache_activities(experiment)
    journal["chaoslib_version"] = journal["chaoslib-version"]
    journal["hypo"] = experiment.get("steady-state-hypothesis")
    journal["num_probes"] = count_activities(experiment, "probe")
    journal["num_actions"] = count_activities(experiment, "action")
    journal["human_duration"] = str(timedelta(seconds=journal["duration"]))
    journal["export_format"] = export_format
    journal["today"] = datetime.now().strftime("%d %B %Y")

    generate_chart_from_metric_probes(journal, export_format)
    add_contribution_model(journal, export_format)
    template = get_report_template(journal["chaoslib-version"])
    report = template.render(journal)

    return report


def count_activities(experiment: Experiment, activity_type: str) -> int:
    """
    Count the number of activity by type in the experiment's method
    """
    count = 0
    for activity in experiment["method"]:
        if "ref" in activity:
            activity = lookup_activity(activity["ref"])
        if activity["type"] == activity_type:
            count += 1
    return count


def save_report(header: str, reports: List[str], report_path: str,
                export_format: str = "markdown"):
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8') as fp:
        fp.write(header)

        for report in reports:
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


def get_report_template(report_version: str,
                        default_template: str = "index.md"):
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

    if not report_version:
        return env.get_template(default_template)

    templates = []
    for name in env.list_templates(["md"]):
        if name in ["index.md", "header.md"]:
            continue

        _, _, v = name.split('_')
        v, _ = v.rsplit('.md', 1)
        templates.append((semver.parse_version_info(v), name))

    templates = sorted(templates, key=lambda vinfo: vinfo[0])

    report_version = report_version.replace('rc1', '-rc1')
    for (vinfo, name) in templates:
        if semver.match(
            report_version, "<={v}".format(v=semver.format_version(
                **vinfo._asdict()))):
            return env.get_template(name)

    # none of the old versions matched, we can use the latest template
    return env.get_template(default_template)


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

    cmd = "{} report --type text {}".format(
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

    cmd = "{} encode --to json {}".format(
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


def add_contribution_model(journal: Journal, export_format: str):
    """
    Expose the contribution of that experiment to the report.
    """
    experiment = journal.get("experiment")
    contributions = experiment.get("contributions")
    if not contributions:
        return

    chart = pygal.Pie()
    chart.title = 'Organization Contributions Impact'
    for (contribution, impact) in contributions.items():
        value = 0
        if impact == "high":
            value = 1
        elif impact == "medium":
            value = 0.5
        if impact == "low":
            value = 0.25

        chart.add(contribution, value)

    if export_format in ["html", "html5"]:
        experiment["contributions_chart"] = chart.render(
            disable_xml_declaration=True)
    else:
        experiment["contributions_chart"] = b64encode(
            cairosvg.svg2png(
                bytestring=chart.render(), dpi=72)).decode("utf-8")
