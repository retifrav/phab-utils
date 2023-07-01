# Changelog

<!-- MarkdownTOC -->

- [0.3.1](#031)
- [0.3.0](#030)
- [0.2.0](#020)
- [0.1.0](#010)

<!-- /MarkdownTOC -->

## 0.3.1

Released on `2023-07-01`.

- `databases`
    + `lightcurves`
        * gathering light curves cadence values statistics
- documentation
    + favicon, new poster and PHAB domain
- wiki
    + generating chemical abundances for HELIOS using FastChem
    + updated AltaiPony installation instructions

## 0.3.0

Released on `2023-05-01`.

- consistent modules naming
- `databases`
    + `tap`
        * querying parameters from NASA and PADC databases
        * querying TAP service returns `pyvo.dal.tap.TAPResults` instead of `pandas.DataFrame`
            - user is expected to do `.to_table().to_pandas()` if he needs `pandas.DataFrame`
        * additional validations on getting the TAP service endpoint
        * some convenience lists for TAP services (*parameters that are strings, parameters with errors, etc*)
        * NASA to PADC parameters/columns mapping
- `files`
    + `pickles`
        * merging several pickle files into one
        * openning a pickle can take both `pathlib.Path` object and plain string

## 0.2.0

Released on `2023-03-19`.

- grouped `utility` modules
- proper [documentation pages](https://uio.decovar.dev/) (*generated with [pdoc](https://pdoc.dev)*)

## 0.1.0

Released on `2022-11-06`.

- first version
