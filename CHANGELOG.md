# Changelog

## [Unreleased][]

[Unreleased]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.14.0...HEAD

## [0.14.0][] - 2022-12-07

[0.14.0]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.13.0...0.14.0

### Changed

- Using `--embed-resources` instead of `--self-contained` as it's been
  [deprecated](https://pandoc.org/releases.html#pandoc-2.19-2022-08-03)
  in Pandoc 2.19
- Only support Python 3.7+ now as the rest of the Chaos Toolkit
- Move from TravisCI to GitHub actions

## [0.13.0][] - 2019-04-15

[0.13.0]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.12.0...0.13.0

### Changed

-   Bumped to chaostoolkit 1.0

## [0.12.0][] - 2018-12-06

[0.12.0]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.11.0...0.12.0

### Changed

-   Support `"ref"` to other activities
-   Support versions that don't match semver specification such as `rc`

## [0.11.0][] - 2018-11-08

[0.11.0]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.10.0...0.11.0

### Changed

-   the `dump` command from `vegeta` has been deprecated to `encode`
    (their changelog doesn't mention from which version)
-   the `report` command from `vegeta` has changed the name of its arguments
    (their changelog doesn't mention from which version)

## [0.10.0][] - 2018-10-17

[0.10.0]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.9.0...0.10.0

### Changed

-   aggregate any number of experiment journals into a single report. This
    changes slightly the report that was produced. [#16][16]

    ```
    $ chaos report --export-format=pdf journal1.json journal2.json report.pdf
    $ chaos report --export-format=pdf journal*.json report.pdf
    ```

[16]: https://github.com/chaostoolkit/chaostoolkit-reporting/issues/16

-   render contributions into the report [#81][81]

[81]: https://github.com/chaostoolkit/chaostoolkit/issues/81

## [0.9.0][] - 2018-07-19

[0.9.0]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.8.0...0.9.0

### Added

-   a Dockerfile to build an image with all the system-wide dependencies

### Changed

-   Showing entire exception in PDF reports

## [0.8.0][] - 2018-06-25

[0.8.0]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.7.1...0.8.0

### Added

-   a section about reliability contributions of an experiment

## [0.7.1][] - 2018-04-23

[0.7.1]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.7.0...0.7.1

### Changed

-   process actions as well, not just probes

## [0.7.0][] - 2018-04-13

[0.7.0]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.6.0...0.7.0

### Added

-   insert vegeta results as charts and text

### Changed

-   better chart support
-   can inline many charts at once for a given probe

## [0.6.0][] - 2018-02-07

[0.6.0]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.5.2...0.6.0

### Changed

-   the chaostoolkit cli now produces journal as `journal.json`,
    not `chaos-report.json` [#9][9]

[9]: https://github.com/chaostoolkit/chaostoolkit-reporting/issues/9

## [0.5.2][] - 2018-01-30

[0.5.2]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.5.1...0.5.2

### Changed

-   Steady state can be optional so don't expect it
-   Echo a message indicating the report was created [#8][8]

[8]: https://github.com/chaostoolkit/chaostoolkit-reporting/issues/8

## [0.5.1][] - 2018-01-29

[0.5.1]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.5.0...0.5.1

### Changed

-   Ensure we use the right template based on the chaostoolkit-lib version
    used for the experiment [#4][4]

[4]: https://github.com/chaostoolkit/chaostoolkit-reporting/issues/4

## [0.5.0][] - 2018-01-28

[0.5.0]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.4.2...0.5.0

### Changed

-   `--smart` argument is gone from pandoc [#3][3]
-   Render steady state results

[3]: https://github.com/chaostoolkit/chaostoolkit-reporting/issues/3

## [0.4.2][] - 2018-01-27

[0.4.2]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.4.1...0.4.2

### Changed

-   Packaging the stylesheets alongside the report template [#1][1]

[1]: https://github.com/chaostoolkit/chaostoolkit-reporting/issues/1

## [0.4.1][] - 2018-01-27

[0.4.1]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.4.0...0.4.1

### Changed

-   Packaging the report template alongside the Python files [#1][1]

[1]: https://github.com/chaostoolkit/chaostoolkit-reporting/issues/1

## [0.4.0][] - 2017-12-29

[0.4.0]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.2.0...0.4.0

### Changed

-   Ensuring charts of series with missing data are aligned

## [0.2.0][] - 2017-12-28

[0.2.0]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.1.0...0.2.0

### Changed

-   Serializing all series in a single chart

## [0.1.0][] - 2017-12-28

[0.1.0]: https://github.com/chaostoolkit/chaostoolkit-reporting/tree/0.1.0

### Added

-   Initial release