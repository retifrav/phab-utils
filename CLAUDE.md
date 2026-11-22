# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`phab-utils` (on PyPI; it was called `uio-exoplanet-group` until 2025-01-29) is a Python library for querying astronomy databases and processing the results as Pandas tables. It covers the NASA Exoplanet Archive, PADC, Gaia and SIMBAD over TAP/ADQL, and Kepler/K2/TESS light curves through lightkurve. `wiki/` is a separate Markdown knowledge base (HPC, HELIOS, RH1.5D, Jupyter tunnelling and so on) that has nothing to do with the package code.

## Commands

The runtime dependencies (`install_requires` in `setup.cfg`) are not in the container's system Python. Create a uv venv for them, e.g. `uv venv /tmp/phab-venv && VIRTUAL_ENV=/tmp/phab-venv uv pip install -e . pytest mypy pdoc`, and run the tools with that venv's `python -m …`.

- **Tests** must run from the repo root, because they open `./data/...` by relative path. The test files are not named `test_*.py`, so `pytest src/phab/tests/` collects **nothing**. Pass the files explicitly:
  ```sh
  python -m pytest ./src/phab/tests/*[^_*].py          # all files (the glob skips __init__.py)
  python -m pytest ./src/phab/tests/databases.py       # one file
  python -m pytest ./src/phab/tests/databases.py -k "test_get_parameters_that_are_double_in_nasa"
  ```
  `strings.py`, `math.py`, `datasets.py` and `files.py` work offline. Nearly all of `databases.py` queries live services (NASA, PADC, SIMBAD, Gaia, MAST), so its results depend on remote data that can change. Before you debug the code, check whether the failure comes from the remote side with a bare `curl` to the endpoint. Two signatures were seen from this sandbox on 2026-11-22:
  - Cloudflare in front of the NASA archive returned a 403 HTML page for some query shapes, e.g. `WHERE hostname = 'Kepler-11' AND st_teff IS NOT NULL`, while simpler queries got 200. In pytest that shows up as `DALServiceError: 403` after `E19: File does not appear to be a VOTABLE`.
  - SIMBAD was unreachable on ports 80 and 443. pyvo sets no connect timeout, so each SIMBAD test then hangs about 130 s, and the whole file took about 12 min. Run it in the background with a generous timeout.
- **Type check**: `python -m mypy ./src/phab`. `mypy.ini` sets `disallow_untyped_defs`, so every function needs full annotations, tests included (`-> None`).
- **Lint**: the repo has no ruff config. The code is clean under ruff's pre-0.17 defaults, `ruff check --select E4,E7,E9,F .`. A bare `ruff check .` on ruff ≥ 0.17 uses the larger new default set and reports many UP/I/FLY findings across the tree, so don't mass-fix those unless asked. The code is not ruff-formatted (`ruff format` would rewrite 18 files), so don't run it unless asked.
- **Build a wheel**: `python -m build` (into `dist/`).
- **API docs** (pdoc, published at phab.decovar.dev): use the exact README command. It passes `./src/phab/utils ./src/phab/tasks` as paths, sets `PHAB_PACKAGE_VERSION` (shown in the templates) and writes to `documentation/_deploy/`, which is gitignored apart from `.gitkeep`. To check that docs build, use `--output-directory` with a scratch dir.

## Architecture

### One source tree, three import roots

`src/phab/` is a **namespace package** with no `__init__.py`. `setup.cfg` relies on `find_namespace:`, and leaving that out is what broke the 0.8.0 wheels. The subpackages are `phab.utils` (reusable modules), `phab.tasks` (multi-step procedures that combine utils) and `phab.tests`. The same code gets imported under different names depending on the caller:

- **Package users** write `from phab.utils.databases import tap`. All docstring examples use this form.
- **Tests** write `from utils.databases import tap`. pytest puts `src/phab` on `sys.path`, because it is the first directory above the tests with no `__init__.py`. So tests run against the source tree as top-level `utils`/`tests` packages, not against an installed `phab`. Shared fixtures live in `tests/__init__.py` and are imported as `from . import somethingThatDoesntExist  # noqa: F401`. The test parameter that receives one then needs `# noqa: F811`.
- **pdoc** documents the modules as `utils.*` and `tasks.*`. That is why `tasks` modules import with `try: from ..utils… except ImportError: from utils…`. The `except` branch is a deliberate pdoc workaround, so don't remove it. Inside `utils`, always use relative imports (`from ..logs.log import logger`), because only those resolve under all three roots. Cross-references in docstrings use pdoc's names (`` `utils.databases.simbad.getObjectID` ``) so that pdoc can link them.

### Databases layer (`utils/databases/`)

- `tap.py` holds the `services` registry: each endpoint plus flags for that service's quirks, such as `drops-leading-zero-on-cast-to-varchar` and `parameters-that-are-strings`. It also holds `mappings` (NASA→PADC column names). `getParameterFromNASA` decides whether a parameter is stellar or planetary by looking it up in the `mappings["NASA-to-PADC"]["stars"]` keys.
- `queryService()` is the single choke point for TAP queries. On `DALQueryError` it retries once with `escapeSpecialCharactersForAdql()`, which escapes single quotes. It returns `None` for an empty result, so callers test `if results:`. ADQL is built as f-strings with the values interpolated directly, and long queries and messages use the `" ".join((…))` idiom.
- The remote databases have quirks, and the workarounds are intentional. Their docstrings explain them and link to the decovar.dev TAP/ADQL blog post, so keep them:
  - NASA rounds doubles in `SELECT` but compares the unrounded values in `WHERE`. The workaround is `parameterTypeIsDouble`, `CAST(… AS REAL)`, a `CAST(… AS VARCHAR(n)) LIKE` retry and `strings.conversion.floatToStringForADQLcastVarchar`.
  - NASA's `TOP` is broken, so queries `ORDER BY pl_pubdate DESC` and take row 0.
  - SIMBAD does not support `CAST`.
  - astroquery 0.4.8 renamed the `query_objectids` column from `ID` to `id`, and the code handles both.
  - `simbad.getObjectID` has a `LIKE` fallback for problematic `main_id`s such as `SZ  66` (two spaces). It has been off by default since 2026.1.9.
- `simbad.py` resolves a star name to SIMBAD's `oid`. It first tries the name as `main_id` in the `basic` table. If that fails, it walks every alias from astroquery's `Simbad.query_objectids` the same way.
- `lightcurves.py` wraps lightkurve searches. The `authors` dict maps each author to its mission and cadence values, and `lightCurveFluxTableSchema` (pandera) validates the flux tables it produces.

### Cross-cutting conventions

- **Logging**: modules log through `from ..logs.log import logger`. That is a `phab` logger writing to stdout with `propagate = False`, so it doesn't change logging in the consuming project. The `PHAB_DEBUG` env var switches it to DEBUG with timestamps; any value except `0`/`no`/`off`/`false`/`disable` turns it on. It is read once, at import time, in `utils/logs/__init__.py`.
- **Docs are the docstrings**: every public function's docstring has an `Example:` with a ```` ``` py ```` block. Each subpackage's `__init__.py` docstring is `.. include:: ../../../../documentation/utils/<name>/index.md`, so a new subpackage needs a matching `documentation/utils/<name>/index.md`.
- **Naming**: functions, variables and parameters are camelCase (`getObjectID`, `parameterTypeIsDouble`). Module names and test functions are snake_case.
- **Shadowing module name**: `utils/datasets/pandas.py` has the same name as the real `pandas`, and its own docstring requires an alias. Always import it as `from ..datasets import pandas as pnd`, and keep `import pandas` for the library.
- **Python version**: `setup.cfg` declares `python_requires >= 3.8`, but `tap.py` uses PEP 604 unions in signatures, which Python evaluates when the function is defined. In practice the floor is therefore 3.10. Most code still uses `typing.Optional`/`List`/`Dict`.

## Releases

- Versioning has been date-based since 2026.1.9. `__version_info__ = (YYYY, M, D)` (no zero padding) lives in `src/phab/utils/_version.py`, and `setup.cfg` reads it via `attr:`. PyPI won't accept the same version twice.
- Each release adds a section at the top of `changelog.md`. It starts with `` Released on `YYYY-MM-DD`. `` and nests bullets as module → submodule → function. Add the new heading to the `MarkdownTOC` block as well.

## Data

`data/` holds the sample files that docstring examples and tests refer to (`systems-528n.pkl`, `merge-pickles/*.pkl`, a TESS `_lc.fits`). Git LFS is deliberately inactive: the attributes file is parked as `disabled.gitattributes` and the binaries are committed directly. Don't rename it to `.gitattributes`.
