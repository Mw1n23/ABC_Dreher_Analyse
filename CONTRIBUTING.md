# Contributing

## Development setup
```bash
git clone https://github.com/Mw1n23/ABC_Dreher_Analyse.git
cd ABC_Dreher_Analyse
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[plot]
```

## Local validation
Run the repository gate before opening a pull request:
```bash
python -m unittest discover -s tests -q
python -m abc_dreher_analyse --help
python abc_analysis.py --help
```

For a runtime smoke test with real input data:
```bash
abc-dreher-analyse --input-file data/input_data.csv --output-dir output --no-show-plots
```

## Scope for changes
- Keep the CLI stable unless there is a clear usability gain.
- Preserve the legacy wrapper `abc_analysis.py` unless there is an explicit breaking-change decision.
- Keep analysis behavior changes and packaging changes separate unless the packaging work depends on the refactor.

## Pull request notes
- Describe whether the change affects analysis logic, plotting, or repository infrastructure.
- Mention any input-format assumptions that changed.
- Include the commands used for validation.
