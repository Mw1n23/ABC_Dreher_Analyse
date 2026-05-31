from pathlib import Path


def test_abc_analysis_is_valid_python() -> None:
    source = Path("abc_analysis.py").read_text(encoding="utf-8")
    compile(source, "abc_analysis.py", "exec")
