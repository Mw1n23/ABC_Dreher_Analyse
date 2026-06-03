# Analysis Method and Repository Setup

## Purpose
This repository performs an ABC analysis on article movement data.

The original version was a single script with top-level side effects. It has now been refactored into an installable package with a CLI, explicit configuration, and repository-level documentation.

## Current analysis flow
The runtime entry point is `abc_dreher_analyse.cli`.

### 1. Read the CSV input
- Default input path: `data/input_data.csv`
- Default delimiter: `;`
- Encoding fallback order:
  - `utf-8-sig`
  - `iso-8859-1`
  - `cp1252`

### 2. Validate the input schema
Required columns:
- `id`
- `number`
- `name`

Month columns are discovered dynamically using the pattern `Month_<n>`.

### 3. Convert month columns to numeric values
- Non-numeric values are coerced to `NaN`.
- Missing values are tolerated and ignored in the aggregation.

### 4. Build the ABC ranking
- The analysis sums the trailing `N` month columns, where `N` is controlled by `--last-months`.
- Default: `6`
- Articles are sorted descending by that trailing-period movement total.
- Cumulative percentages are computed over the sorted result.

### 5. Assign categories
- `A`: up to 80% cumulative movements
- `B`: next up to 95%
- `C`: remaining share

### 6. Export outputs
By default the repository writes:
- `output/abc_analysis_results.csv`
- `output/monthly_timeseries.png`
- `output/abc_analysis.png`

Interactive display is optional and disabled by default.

## Install modes

### Standard user install
```bash
git clone https://github.com/Mw1n23/ABC_Dreher_Analyse.git
cd ABC_Dreher_Analyse
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .[plot]
```

### Development install
```bash
git clone https://github.com/Mw1n23/ABC_Dreher_Analyse.git
cd ABC_Dreher_Analyse
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[plot]
```

## CLI entry points
- `abc-dreher-analyse`
- `abc-analysis`
- `python -m abc_dreher_analyse`
- `python abc_analysis.py`

## Local gate
Run before pushing:
```bash
python -m unittest discover -s tests -q
python -m abc_dreher_analyse --help
python abc_analysis.py --help
```

## Limitations
- The project expects a column-oriented monthly input layout.
- The current classification thresholds are fixed to the common `80/95/100` convention.
- Plot output requires the plotting extra.
