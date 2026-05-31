# ABC Analysis Script

## Overview
This project performs an ABC analysis on article movement data, creates two plots, and exports result categories to CSV.

## Repository Layout
- `abc_analysis.py`: Main analysis script.
- `requirements.txt`: Python dependencies.
- `tests/`: Basic validation tests.
- `data/`: Input CSV folder (local, ignored by git).
- `output/`: Generated charts and result files (local, ignored by git).

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage
1. Put `input_data.csv` into `data/`.
2. Run:
```bash
python abc_analysis.py
```
3. Results are written to `output/`:
- `monthly_timeseries.png`
- `abc_analysis.png`
- `abc_analysis_results.csv`

## Input Format
- Delimiter: `;`
- Required columns: `id`, `number`, `name`, `Month_1` ... `Month_13`

## Quality Check
```bash
pytest -q
```
