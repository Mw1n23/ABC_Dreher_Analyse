from pathlib import Path

from setuptools import find_packages, setup


README = Path(__file__).with_name("README.md").read_text(encoding="utf-8")


setup(
    name="abc-dreher-analyse",
    version="0.1.0",
    description="ABC analysis for article movement data with CSV export and plots.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Mw1n23",
    license="MIT",
    url="https://github.com/Mw1n23/ABC_Dreher_Analyse",
    python_requires=">=3.10",
    packages=find_packages(include=["abc_dreher_analyse", "abc_dreher_analyse.*"]),
    include_package_data=True,
    install_requires=[
        "pandas>=2.0",
    ],
    extras_require={
        "plot": [
            "matplotlib>=3.7",
            "numpy>=1.24",
        ],
        "dev": ["pytest>=8"],
    },
    project_urls={
        "Source": "https://github.com/Mw1n23/ABC_Dreher_Analyse",
        "Issues": "https://github.com/Mw1n23/ABC_Dreher_Analyse/issues",
    },
    entry_points={
        "console_scripts": [
            "abc-dreher-analyse=abc_dreher_analyse.cli:main",
            "abc-analysis=abc_dreher_analyse.cli:main",
        ]
    },
)
