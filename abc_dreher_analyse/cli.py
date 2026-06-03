from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .analysis import AnalysisConfig, run_analysis


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run an ABC analysis on article movement data."
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        default=Path("data/input_data.csv"),
        help="Input CSV file. Default: data/input_data.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory for generated CSV and plots. Default: output",
    )
    parser.add_argument(
        "--delimiter",
        default=";",
        help="Input CSV delimiter. Default: ';'",
    )
    parser.add_argument(
        "--last-months",
        type=int,
        default=6,
        help="Number of trailing month columns used for the ABC ranking. Default: 6",
    )
    parser.add_argument(
        "--save-plots",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Save plot files into the output directory.",
    )
    parser.add_argument(
        "--show-plots",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Open plots interactively after creation.",
    )
    return parser


def parse_arguments(argv: list[str] | None = None) -> AnalysisConfig:
    args = build_parser().parse_args(argv)
    if args.last_months <= 0:
        raise ValueError("last-months must be greater than zero.")

    return AnalysisConfig(
        input_file=args.input_file,
        output_dir=args.output_dir,
        delimiter=args.delimiter,
        last_months=args.last_months,
        save_plots=args.save_plots,
        show_plots=args.show_plots,
    )


def main(argv: list[str] | None = None) -> int:
    try:
        config = parse_arguments(argv)
        run_analysis(config)
    except Exception as exc:
        LOGGER.error("Program failed: %s", exc)
        return 1
    return 0
