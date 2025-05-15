## ABC Analysis Script

### Overview
This Python script performs an ABC analysis on article movement data, visualizing monthly trends and categorizing articles into A, B, and C classes based on their movement frequency over the last 6 months. It generates two plots (time series and cumulative distribution) and saves the results to a CSV file.

### Requirements
- Python 3.6+
- Libraries: `pandas`, `matplotlib`, `numpy`
- Install dependencies: `pip install pandas matplotlib numpy`

### Usage
1. Place your input data file (`input_data.csv`) in the `data/` directory.
2. Run the script: `python abc_analysis.py`
3. Output files (plots and CSV) will be saved in the `output/` directory.

### Input Format
- **File**: CSV file named `input_data.csv`
- **Delimiter**: Semicolon (`;`)
- **Encoding**: UTF-8 (with BOM), ISO-8859-1, or CP1252
- **Columns**:
  - `id`: Unique article identifier
  - `number`: Article number
  - `name`: Article name
  - `Month_1` to `Month_13`: Monthly movement data (numeric) for 13 months
- **Example**:


id;number;name;Month_1;Month_2;...;Month_13 <br/>
1;1001;Article A;10;15;...;20 <br/>
2;1002;Article B;5;8;...;12 <br/>


### Output
- `monthly_timeseries.png`: Time series plot of monthly movements (top-5 articles highlighted).
- `abc_analysis.png`: Cumulative distribution plot with A/B/C categories.
- `abc_analysis_results.csv`: Results table with article details and ABC categories.

