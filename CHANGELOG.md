# Changelog

## [Unreleased][]

[Unreleased]: https://github.com/chaostoolkit/chaostoolkit-reporting/compare/0.6.0...HEAD

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