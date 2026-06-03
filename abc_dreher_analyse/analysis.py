from __future__ import annotations

import csv
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LOGGER = logging.getLogger(__name__)
BASE_COLUMNS = ("id", "number", "name")
MONTH_PATTERN = re.compile(r"^Month_(\d+)$")


class DataLoadError(RuntimeError):
    """Raised when input data cannot be loaded."""


class DataValidationError(ValueError):
    """Raised when input data does not match the expected schema."""


@dataclass(frozen=True)
class AnalysisConfig:
    input_file: Path
    output_dir: Path
    delimiter: str = ";"
    last_months: int = 6
    save_plots: bool = True
    show_plots: bool = False


@dataclass(frozen=True)
class AnalysisArtifacts:
    month_columns: list[str]
    last_n_label: str
    monthly_stats: Any
    processed_df: Any
    sorted_df: Any
    result_df: Any
    summary_df: Any
    total_movements: float
    top_5_articles: list[str]
    top_10_articles: list[str]


def load_analysis_dependencies() -> Any:
    try:
        import pandas as pd
    except ImportError as exc:
        raise RuntimeError(
            "pandas is required for the analysis. Install the project dependencies first."
        ) from exc
    return pd


def load_plot_dependencies(show_plots: bool) -> tuple[Any, Any]:
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "matplotlib and numpy are required for plotting. Install the project with plotting dependencies."
        ) from exc

    if not show_plots:
        plt.switch_backend("Agg")
    return plt, np


def read_input_data(input_file: Path, delimiter: str) -> tuple[Any, str]:
    pd = load_analysis_dependencies()

    if not input_file.exists():
        raise FileNotFoundError(f"File not found at '{input_file}'. Please check the file path.")

    encodings = ("utf-8-sig", "iso-8859-1", "cp1252")
    last_error: Exception | None = None

    for encoding in encodings:
        try:
            dataframe = pd.read_csv(
                input_file,
                encoding=encoding,
                sep=delimiter,
                quoting=csv.QUOTE_MINIMAL,
                on_bad_lines="skip",
            )
            return dataframe, encoding
        except (UnicodeDecodeError, pd.errors.ParserError) as exc:
            last_error = exc
            continue
        except pd.errors.EmptyDataError as exc:
            raise DataLoadError(
                f"The file at '{input_file}' is empty. Please check the file."
            ) from exc

    raise DataLoadError(
        f"Could not load '{input_file}' with the supported encodings. Last error: {last_error}"
    )


def detect_month_columns(columns: list[str], last_months: int) -> list[str]:
    month_matches: list[tuple[int, str]] = []
    for column in columns:
        match = MONTH_PATTERN.match(column)
        if match:
            month_matches.append((int(match.group(1)), column))

    if not month_matches:
        raise DataValidationError(
            "No monthly columns found. Expected columns like 'Month_1', 'Month_2', ..."
        )

    month_matches.sort(key=lambda item: item[0])
    month_columns = [column for _, column in month_matches]
    if len(month_columns) < last_months:
        raise DataValidationError(
            f"Found only {len(month_columns)} month columns, but last_months={last_months}."
        )
    return month_columns


def validate_dataframe(dataframe: Any, last_months: int) -> list[str]:
    missing_columns = [column for column in BASE_COLUMNS if column not in dataframe.columns]
    if missing_columns:
        raise DataValidationError(
            f"The following required columns are missing: {missing_columns}. "
            f"Found columns: {dataframe.columns.tolist()}"
        )

    return detect_month_columns(dataframe.columns.tolist(), last_months=last_months)


def compute_monthly_stats(dataframe: Any, month_columns: list[str]) -> Any:
    pd = load_analysis_dependencies()
    monthly_numeric = dataframe[month_columns].apply(pd.to_numeric, errors="coerce")
    return pd.DataFrame(
        {
            "Mean": monthly_numeric.mean(),
            "Std": monthly_numeric.std(),
            "Min": monthly_numeric.min(),
            "Max": monthly_numeric.max(),
        }
    )


def assign_abc_category(cumulative_percentage: float) -> str:
    if cumulative_percentage <= 80:
        return "A"
    if cumulative_percentage <= 95:
        return "B"
    return "C"


def analyze_dataframe(dataframe: Any, month_columns: list[str], last_months: int) -> AnalysisArtifacts:
    pd = load_analysis_dependencies()
    processed_df = dataframe.copy()
    processed_df[month_columns] = processed_df[month_columns].apply(pd.to_numeric, errors="coerce")

    if processed_df[month_columns].isna().any().any():
        LOGGER.warning(
            "NaN values found in monthly columns. Missing values will be ignored in the analysis."
        )

    monthly_stats = compute_monthly_stats(processed_df, month_columns)
    last_n_columns = month_columns[-last_months:]
    last_n_label = f"last_{last_months}_months"

    processed_df[last_n_label] = processed_df[last_n_columns].fillna(0).sum(axis=1)
    sorted_df = processed_df.sort_values(by=last_n_label, ascending=False).copy()

    top_5_articles = sorted_df["name"].head(5).tolist()
    top_10_articles = sorted_df["name"].head(10).tolist()

    total_movements = float(sorted_df[last_n_label].sum())
    if total_movements > 0:
        sorted_df["cumulative_movements"] = sorted_df[last_n_label].cumsum()
        sorted_df["cumulative_percentage"] = (
            sorted_df["cumulative_movements"] / total_movements * 100
        )
        sorted_df["abc_category"] = sorted_df["cumulative_percentage"].apply(assign_abc_category)
    else:
        sorted_df["cumulative_movements"] = 0.0
        sorted_df["cumulative_percentage"] = 0.0
        sorted_df["abc_category"] = "C"

    result_df = sorted_df[
        ["id", "number", "name", last_n_label, "abc_category"]
    ].copy()

    summary_df = (
        result_df.groupby("abc_category", dropna=False)
        .agg(
            Article_Count=("id", "count"),
            Total_Movements=(last_n_label, "sum"),
        )
        .sort_index()
    )

    article_count = len(result_df)
    if article_count > 0:
        summary_df["Percent_Articles"] = summary_df["Article_Count"] / article_count * 100
    else:
        summary_df["Percent_Articles"] = 0.0

    if total_movements > 0:
        summary_df["Percent_Movements"] = summary_df["Total_Movements"] / total_movements * 100
    else:
        summary_df["Percent_Movements"] = 0.0

    return AnalysisArtifacts(
        month_columns=month_columns,
        last_n_label=last_n_label,
        monthly_stats=monthly_stats,
        processed_df=processed_df,
        sorted_df=sorted_df,
        result_df=result_df,
        summary_df=summary_df,
        total_movements=total_movements,
        top_5_articles=top_5_articles,
        top_10_articles=top_10_articles,
    )


def build_summary_text(summary_df: Any) -> str:
    lines = ["Summary of ABC Categories:"]
    for category in ("A", "B", "C"):
        if category not in summary_df.index:
            continue
        row = summary_df.loc[category]
        lines.append(
            f"Category {category}: {int(row['Article_Count'])} Articles "
            f"({row['Percent_Articles']:.2f}%), "
            f"Total Movements: {int(row['Total_Movements'])} "
            f"({row['Percent_Movements']:.2f}%)"
        )
    return "\n".join(lines)


def create_time_series_plot(artifacts: AnalysisArtifacts, output_dir: Path, show_plots: bool) -> None:
    plt, np = load_plot_dependencies(show_plots=show_plots)
    plt.figure(figsize=(12, 6))

    top_10_colors = list(plt.cm.tab10.colors)
    non_top_10_count = max(0, len(artifacts.processed_df) - len(artifacts.top_10_articles))
    blue_colors = plt.cm.Blues(np.linspace(0.3, 1.0, max(non_top_10_count, 1)))
    blue_index = 0

    for _, row in artifacts.processed_df.iterrows():
        article_name = row["name"]
        if article_name in artifacts.top_10_articles:
            color = top_10_colors[artifacts.top_10_articles.index(article_name) % len(top_10_colors)]
        else:
            color = blue_colors[blue_index]
            blue_index += 1

        plt.plot(
            range(len(artifacts.month_columns)),
            row[artifacts.month_columns],
            color=color,
            label=article_name if article_name in artifacts.top_5_articles else None,
        )

    plt.xticks(range(len(artifacts.month_columns)), artifacts.month_columns, rotation=45)
    plt.xlabel("Month")
    plt.ylabel("Number of Movements")
    plt.title("Monthly Movements of Articles")
    plt.grid(True)

    handles, labels = plt.gca().get_legend_handles_labels()
    if labels:
        plt.legend(handles, labels, title="Top-5 Articles", loc="upper right")

    plt.tight_layout()
    plt.savefig(output_dir / "monthly_timeseries.png", bbox_inches="tight")
    if show_plots:
        plt.show()
    plt.close()


def create_abc_plot(artifacts: AnalysisArtifacts, output_dir: Path, show_plots: bool) -> None:
    plt, _ = load_plot_dependencies(show_plots=show_plots)
    plt.figure(figsize=(12, 8))

    summary_df = artifacts.summary_df
    sorted_df = artifacts.sorted_df
    a_count = int(summary_df.loc["A", "Article_Count"]) if "A" in summary_df.index else 0
    b_count = int(summary_df.loc["B", "Article_Count"]) if "B" in summary_df.index else 0
    c_count = int(summary_df.loc["C", "Article_Count"]) if "C" in summary_df.index else 0

    a_end = a_count
    b_end = a_count + b_count
    c_end = a_count + b_count + c_count

    if a_count > 0:
        plt.plot(
            range(a_end),
            sorted_df["cumulative_percentage"].iloc[:a_end],
            marker="o",
            color="r",
            label="Category A",
        )
    if b_count > 0:
        plt.plot(
            range(max(a_end - 1, 0), b_end),
            sorted_df["cumulative_percentage"].iloc[max(a_end - 1, 0):b_end],
            marker="o",
            color="g",
            label="Category B",
        )
    if c_count > 0:
        plt.plot(
            range(max(b_end - 1, 0), c_end),
            sorted_df["cumulative_percentage"].iloc[max(b_end - 1, 0):c_end],
            marker="o",
            color="b",
            label="Category C",
        )

    plt.axhline(y=80, color="r", linestyle="--", label="80% Movements (A)")
    plt.axhline(y=95, color="g", linestyle="--", label="95% Movements (B)")

    if a_count > 0:
        plt.axvline(x=a_count - 0.5, color="r", linestyle="--", alpha=0.5, label=f"A: {a_count} Articles")
    if b_count > 0:
        plt.axvline(
            x=(a_count + b_count) - 0.5,
            color="g",
            linestyle="--",
            alpha=0.5,
            label=f"B: {b_count} Articles",
        )

    total_articles = len(sorted_df)
    total_movements = int(sorted_df[artifacts.last_n_label].sum())
    plt.xlabel(f"Individual Articles (Sorted by Movement Frequency) | Total Articles: {total_articles}")
    plt.ylabel(f"Cumulative Percentage of Movements [%] | Total Movements: {total_movements}")
    plt.title("ABC Analysis: Cumulative Distribution of Movements")
    plt.legend(loc="center right")
    plt.grid(True)

    summary_text = build_summary_text(summary_df)
    plt.text(
        0.95,
        0.05,
        summary_text,
        transform=plt.gca().transAxes,
        fontsize=10,
        verticalalignment="bottom",
        horizontalalignment="right",
        bbox=dict(facecolor="white", alpha=0.8),
    )

    plt.tight_layout()
    plt.savefig(output_dir / "abc_analysis.png", bbox_inches="tight")
    if show_plots:
        plt.show()
    plt.close()


def save_results_csv(result_df: Any, output_dir: Path) -> Path:
    output_file = output_dir / "abc_analysis_results.csv"
    result_df.to_csv(output_file, index=False)
    return output_file


def ensure_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)


def run_analysis(config: AnalysisConfig) -> AnalysisArtifacts:
    ensure_output_dir(config.output_dir)
    dataframe, encoding_used = read_input_data(config.input_file, delimiter=config.delimiter)
    LOGGER.info("Loaded input file '%s' using encoding %s.", config.input_file, encoding_used)

    month_columns = validate_dataframe(dataframe, last_months=config.last_months)
    artifacts = analyze_dataframe(dataframe, month_columns=month_columns, last_months=config.last_months)

    LOGGER.info("Statistical Analysis of Monthly Movements:\n%s", artifacts.monthly_stats.to_string())
    LOGGER.info("ABC Analysis Results:\n%s", artifacts.result_df.to_string(index=False))
    LOGGER.info("Summary:\n%s", artifacts.summary_df.to_string())

    if config.save_plots:
        create_time_series_plot(artifacts, output_dir=config.output_dir, show_plots=config.show_plots)
        create_abc_plot(artifacts, output_dir=config.output_dir, show_plots=config.show_plots)

    results_file = save_results_csv(artifacts.result_df, output_dir=config.output_dir)
    LOGGER.info("Results saved to '%s'.", results_file)
    return artifacts
