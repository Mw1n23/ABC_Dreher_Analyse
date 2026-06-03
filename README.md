# ABC Analysis Script

[![CI](https://github.com/Mw1n23/ABC_Dreher_Analyse/actions/workflows/python-ci.yml/badge.svg)](https://github.com/Mw1n23/ABC_Dreher_Analyse/actions/workflows/python-ci.yml)

## Overview
This project performs an ABC analysis on article movement data, creates two plots, and exports result categories to CSV.

It has been refactored from a single script into an installable package with:
- a stable CLI,
- schema validation and explicit configuration,
- repository docs and contributor guidance,
- package metadata and CI for GitHub publishing.

Technical notes and setup details are documented in `docs/ANALYSIS_METHOD_AND_SETUP.md`.

## Repository Layout
- `abc_dreher_analyse/`: installable Python package
- `abc_analysis.py`: compatibility wrapper for the legacy script entry point
- `requirements.txt`: convenience wrapper for `pip install -r requirements.txt`
- `tests/`: unit tests
- `data/`: Input CSV folder (local, ignored by git).
- `output/`: Generated charts and result files (local, ignored by git).
- `pyproject.toml` and `setup.py`: package metadata

## Clone and Install
Standard installation:
```bash
git clone https://github.com/Mw1n23/ABC_Dreher_Analyse.git
cd ABC_Dreher_Analyse
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .[plot]
```

Development installation:
```bash
git clone https://github.com/Mw1n23/ABC_Dreher_Analyse.git
cd ABC_Dreher_Analyse
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[plot]
```

## Usage
Installed CLI:
```bash
abc-dreher-analyse --help
```

Module entry point:
```bash
python -m abc_dreher_analyse --help
```

Legacy script entry point:
```bash
python abc_analysis.py --help
```

Typical run:
```bash
abc-dreher-analyse --input-file data/input_data.csv --output-dir output --no-show-plots
```

Results are written to `output/`:
- `monthly_timeseries.png`
- `abc_analysis.png`
- `abc_analysis_results.csv`

## Input Format
- Delimiter: `;`
- Required columns: `id`, `number`, `name`
- Month columns: `Month_1`, `Month_2`, ... `Month_n`
- The trailing `--last-months` month columns are used for the ABC ranking.

## Quality Check
```bash
python -m unittest discover -s tests -q
```

## GitHub workflow
- CI runs on push and pull request.
- `CONTRIBUTING.md` defines the local gate.
- `CHANGELOG.md` tracks user-visible repository changes.
