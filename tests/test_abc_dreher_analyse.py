import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from abc_dreher_analyse import cli
from abc_dreher_analyse import analysis as analysis_module


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "abc_analysis.py"
CLI_MODULE_PATH = REPO_ROOT / "abc_dreher_analyse" / "cli.py"

try:
    import pandas as pd  # type: ignore
except ImportError:  # pragma: no cover - optional in local sandbox
    pd = None


class ABCDreherAnalyseTests(unittest.TestCase):
    def test_cli_module_compiles(self) -> None:
        source = CLI_MODULE_PATH.read_text(encoding="utf-8")
        compile(source, str(CLI_MODULE_PATH), "exec")

    def test_module_help_works(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "abc_dreher_analyse", "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Run an ABC analysis on article movement data.", result.stdout)

    def test_legacy_script_help_works(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Run an ABC analysis on article movement data.", result.stdout)

    def test_parse_arguments_returns_config(self) -> None:
        config = cli.parse_arguments(
            [
                "--input-file",
                "data/input.csv",
                "--output-dir",
                "output",
                "--delimiter",
                ";",
                "--last-months",
                "4",
                "--no-show-plots",
            ]
        )

        self.assertEqual(config.input_file, Path("data/input.csv"))
        self.assertEqual(config.output_dir, Path("output"))
        self.assertEqual(config.last_months, 4)
        self.assertFalse(config.show_plots)

    def test_main_returns_error_when_pandas_is_missing(self) -> None:
        with mock.patch.object(
            analysis_module,
            "load_analysis_dependencies",
            side_effect=RuntimeError("pandas missing"),
        ), mock.patch.object(cli.LOGGER, "error"):
            exit_code = cli.main([])

        self.assertEqual(exit_code, 1)

    @unittest.skipUnless(pd is not None, "pandas not installed")
    def test_run_analysis_on_sample_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_file = tmpdir_path / "input_data.csv"
            output_dir = tmpdir_path / "output"

            with input_file.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, delimiter=";")
                writer.writerow(
                    [
                        "id",
                        "number",
                        "name",
                        "Month_1",
                        "Month_2",
                        "Month_3",
                        "Month_4",
                        "Month_5",
                        "Month_6",
                    ]
                )
                writer.writerow(["1", "1001", "Artikel A", "10", "10", "10", "10", "10", "10"])
                writer.writerow(["2", "1002", "Artikel B", "5", "5", "5", "5", "5", "5"])
                writer.writerow(["3", "1003", "Artikel C", "1", "1", "1", "1", "1", "1"])

            config = analysis_module.AnalysisConfig(
                input_file=input_file,
                output_dir=output_dir,
                last_months=6,
                save_plots=False,
                show_plots=False,
            )

            artifacts = analysis_module.run_analysis(config)

            self.assertEqual(list(artifacts.result_df["abc_category"]), ["A", "B", "C"])
            self.assertTrue((output_dir / "abc_analysis_results.csv").exists())


if __name__ == "__main__":
    unittest.main()
