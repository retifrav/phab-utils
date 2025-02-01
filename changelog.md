# Changelog

<!-- MarkdownTOC -->

- [0.8.1](#081)
- [0.8.0](#080)
- [0.7.0](#070)
- [0.6.0](#060)
- [0.5.1](#051)
- [0.5.0](#050)
- [0.4.0](#040)
- [0.3.2](#032)
- [0.3.1](#031)
- [0.3.0](#030)
- [0.2.0](#020)
- [0.1.0](#010)

<!-- /MarkdownTOC -->

## 0.8.1

Released on `2025-02-01`.

- fixed incorrect namespacing of the package, was missing `find_namespace:` directive in the manifest, which made imports fail
    + that affected users who install it from PyPI wheel with `pip install phab-utils`
    + installing from sources with `pip install -e .` doesn't seem to be affected
    + the version is increased because it is impossible to re-publish the same version to PyPI

## 0.8.0

Released on `2025-02-01`.

- the package has been renamed from `uio-exoplanet-group` to `phab-utils`
    + `utility` namespace is now `utils`, and in general you will need to adapt your imports from `uio.utility.SOMETHING` to `phab.utils.SOMETHING`
    + new wheels
        * published in PyPI under the [new name](https://pypi.org/project/phab-utils/)
        * previous versions are still available in PyPI under the [old name](https://pypi.org/project/uio-exoplanet-group/#history)
- `math` - new module for mathematics
    + `statistics`
        * `findOutliers()` - marking outliers in an array
- `databases`
    + `simbad`
        * `getObjectID` - workaround for [breaking API](https://github.com/astropy/astropy/issues/17695) in Astroquery version `0.4.8`

## 0.7.0

Released on `2024-10-20`.

- `databases`
    + `tap`
        * `escapeSpecialCharactersForAdql()` - escaping certain special characters (*such as single quotes*) in ADQL queries
        * `getPlanetaryParameterReferenceFromNASA()` - getting the publication reference for the given planetary parameter value from NASA database
        * `getStellarParameterFromNASA()` and `getPlanetaryParameterFromNASA()` can optionally get non-rounded float values to work around the problem with [inconsistent values](https://decovar.dev/blog/2022/02/26/astronomy-databases-tap-adql/#float-values-are-rounded-on-select-but-compared-to-originals-in-where) in `SELECT`/`WHERE`
- `strings` - new module for working with strings
    + `extraction`
        * `adsRefFromFullReferenceNASA()` - extracting just the ADS reference value from the full reference string
    + `conversion`
        * `floatToStringForADQLcastVarchar()` - converting floats to strings for ADQL

## 0.6.0

Released on `2024-08-31`.

- `databases`
    + `lightcurves`
        * `getLightCurveStats`
            - cadence can have more than one value, so it now accepts a list instead of just one value (*and an empty list would mean that any value is good*)
            - detailed results format has changed, now it also includes the cadence value per sector
    + `simbad` and `tap` - querying for a parameter in SIMBAD also returns its bibliographic code, so now the return type for the following functions is `tuple[Any, str]`:
        * `getStellarParameter()`
        * `getStellarParameterFromSimbadByMainID()`
        * `getStellarParameterFromSimbadByObjectID()`

## 0.5.1

Released on `2024-08-24`.

- `databases`
    + `simbad`
        * renamed `findObjectID()` to `getObjectID()`
            - checking for the main ID before iterating all the identificators
        * renamed `getOtherIDfromSimbad()` to `findIdentificatorFromAnotherCatalogue()`
        * `getStellarParameterFromSimbad()` - wraps `getObjectID()` and `getStellarParameterFromSimbadByObjectID()` into a single convenience function
    + `tap`
        * split `getStellarParameterFromSimbad()` into `getStellarParameterFromSimbadByMainID()` and `getStellarParameterFromSimbadByObjectID()`
        * `getServiceEndpoint()` now raises a `ValueError` exception instead of returning `None`

## 0.5.0

Released on `2024-08-23`.

- `databases`
    + `simbad`
        * `findObjectID()` - finding SIMBAD object ID
    + `tap`
        * `getStellarParameterFromSimbad()` - querying stellar parameters from SIMBAD
- `datasets`
    + `pandas`
        * `dropMeaninglessRows()` - dropping/removing meaningless rows from a table
- wiki
    + running jobs on NRIS

## 0.4.0

Released on `2023-11-27`.

- `datasets` - new module for data processing
    + `pandas`
        * `mergeTables()` - merging several tables into one
        * `deduplicateTable()` - finding duplicate rows in the table
- `files`
    + `pickles`
        * `mergePickles()` - option for saving to file or returning merging Pandas table
- `logs` - new module for logging

## 0.3.2

Released on `2023-10-05`.

- the package can be installed from [PyPI](https://pypi.org/project/uio-exoplanet-group/) now
- disabled Git LFS because of GitHub's LFS policy/pricing
- using `ValueError` where suitable instead of `SystemError` for everything
- `databases`
    + `lightcurves`
        * `getLightCurveIDs()` - geting missions and cadences based on light curves stats
- wiki
    + how to build RH15D from sources
    + updated instructions for installing AltaiPony

## 0.3.1

Released on `2023-07-01`.

- `databases`
    + `lightcurves`
        * `getLightCurveStats()` - gathering light curves cadence values statistics
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
