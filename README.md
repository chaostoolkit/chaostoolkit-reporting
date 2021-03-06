# chaostoolkit-reporting

[![Build Status](https://travis-ci.org/chaostoolkit/chaostoolkit-reporting.svg?branch=master)](https://travis-ci.org/chaostoolkit/chaostoolkit-reporting)

The Chaos Toolkit reporting extension library.

## Purpose

The purpose of this library is to provide reporting support to the
[Chaos Toolkit][chaostoolkit] experiment results.

[chaostoolkit]: http://chaostoolkit.org

## Features

The library takes the journal generated by the `chaos run` command
and transforms into a human friendly report. The report can be a standalone
PDF or HTML document.

## Install

Install this package as any other Python packages:

```
$ pip install -U chaostoolkit-reporting
```

Notice that this draws a few [dependencies][deps]:

[deps]: https://github.com/chaostoolkit/chaostoolkit-reporting/blob/master/requirements.txt

Some of them are LGPL v3 licensed.

If you are using Mac OS X then you will need to [install some additional dependencies](osx-install.md) that the `chaos report` command relies upon.

You will also need to install the [pandoc][] package on your system.

[pandoc]: https://pandoc.org/

If you intend on creating PDF reports, the following additional packages will
be needed:

```
$ sudo apt-get install texlive-latex-base \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    pdflatex
```

### Download a Docker Image

As the dependencies for this plugin can be difficult to get right, we also
provide a docker image. Note that this image is rather big with 1.4Gb to
pull.

```console
$ docker pull chaostoolkit/reporting
```

## Usage

Once installed, a new `report` subcommand will be made available to the
`chaos` command, use it as follows:

```
$ chaos report --export-format=html5 chaos-report.json report.html
```

or, for a PDF document:

```
$ chaos report --export-format=pdf chaos-report.json report.pdf
```

You can also generate a single report from many journals at once:

```
$ chaos report --export-format=pdf journal-1.json journal-2 journal-3 report.pdf
```

Or more succintly:

```
$ chaos report --export-format=pdf journal-*.json report.pdf
```

### Use a Docker container

To generate a PDF report using the Docker image:

```console
$ ls .
journal.json

$ docker run \
    --user `id -u` \
    -v `pwd`:/tmp/result \
    -it \
    chaostoolkit/reporting

$ ls .
journal.json report.pdf chaostoolkit.log
```

As you can see, you should run that command from where the `journal.json`
file, generated during an experiment run, can be found. This will create a
`report.pdf` in this directory.

The file will be owned by the user id returned by the command `id -u`, it should
be your user. The reason we specify a user is that, by default, the container
runs as root and the image doesn't make a guess about which user will run
the container. If you don't have the `id` command you can set the value
manually as follows instead: `--user 1000:1000` assuming both your user and
group ids are `1000`.

The default command of the image is equivalent to running this without a
container:

```console
$ chaos report --export-format=pdf journal.json report.pdf
```

If you wish to override that command, pass the `chaos report` parameters as
follows:

```console
$ docker run \
    --user `id -u` \
    -v `pwd`:/tmp/result \
    -it \
    chaostoolkit/reporting -- report --export-format=html5 journal.json report.html

$ ls .
journal.json report.html chaostoolkit.log
```

## Contribute

Contributors to this project are welcome as this is an open-source effort that
seeks [discussions][join] and continuous improvement.

[join]: https://join.chaostoolkit.org/

From a code perspective, if you wish to contribute, you will need to run a 
Python 3.5+ environment. Then, fork this repository and submit a PR. The
project cares for code readability and checks the code style to match best
practices defined in [PEP8][pep8]. Please also make sure you provide tests
whenever you submit a PR so we keep the code reliable.

[pep8]: https://pycodestyle.readthedocs.io/en/latest/

