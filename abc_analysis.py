import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import csv

# Step 1: Import data from the specified file path
file_path = "data/input_data.csv"

try:
    df = pd.read_csv(
        file_path,
        encoding='utf-8-sig',
        sep=';',
        quoting=csv.QUOTE_ALL,
        on_bad_lines='skip'
    )
except pd.errors.ParserError as e:
    print(f"Error parsing the file: {e}")
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        lines = file.readlines()
        print("\nSample lines for inspection:")
        for i, line in enumerate(lines[0:8], start=1):
            print(f"Line {i}: {line.strip()}")
    exit()
except UnicodeDecodeError:
    print("Encoding error. Trying alternative encoding (iso-8859-1)...")
    try:
        df = pd.read_csv(file_path, encoding='iso-8859-1', sep=';', quoting=csv.QUOTE_ALL, on_bad_lines='skip')
    except UnicodeDecodeError:
        print("Error with iso-8859-1. Trying cp1252...")
        try:
            df = pd.read_csv(file_path, encoding='cp1252', sep=';', quoting=csv.QUOTE_ALL, on_bad_lines='skip')
        except Exception as e:
            print(f"All encoding attempts failed. Last error: {e}")
            exit()
except FileNotFoundError:
    print(f"File not found at '{file_path}'. Please check the file path.")
    exit()
except pd.errors.EmptyDataError:
    print(f"The file at '{file_path}' is empty. Please check the file.")
    exit()
except Exception as e:
    print(f"An error occurred while reading the file: {e}")
    exit()

# Step 2: Check for required columns
required_columns = ['id', 'number', 'name']
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    print(f"The following required columns are missing: {missing_columns}")
    print("Found columns:", df.columns.tolist())
    exit()

# Define monthly columns (generalized)
month_columns = [f'Month_{i}' for i in range(1, 14)]  # Represents 13 months
missing_months = [col for col in month_columns if col not in df.columns]
if missing_months:
    print(f"The following month columns are missing: {missing_months}")
    print("Found columns:", df.columns.tolist())
    exit()

# Step 3: Check for NaN values in monthly columns
if df[month_columns].isna().any().any():
    print("Warning: NaN values found in monthly columns. These will be ignored for analysis.")

# Step 4: Statistical analysis of monthly movements
monthly_stats = pd.DataFrame({
    'Mean': df[month_columns].mean(),
    'Std': df[month_columns].std(),
    'Min': df[month_columns].min(),
    'Max': df[month_columns].max()
})

print("\nStatistical Analysis of Monthly Movements:")
print(monthly_stats)

# Step 5: Calculate movements for the last 6 months
last_6_months_columns = month_columns[-6:]  # Last 6 months
df['last_6_months'] = df[last_6_months_columns].sum(axis=1)

# Step 6: Sort articles by movement frequency (last_6_months) in descending order
df_sorted = df.sort_values(by='last_6_months', ascending=False)

# Identify top-5 articles for the legend and top-10 for colors
top_5_articles = df_sorted['name'].head(5).tolist()
top_10_articles = df_sorted['name'].head(10).tolist()

# Step 7: Time series plot for monthly movements of articles
plt.figure(figsize=(12, 6))

# Define distinct colors for top-10 articles
top_10_colors = [
    'red', 'green', 'orange', 'purple', 'brown',
    'pink', 'lime', 'cyan', 'magenta', 'gold'
]

# Generate blue shades for remaining articles
num_non_top_10 = len(df) - len(top_10_articles)
blue_colors = plt.cm.Blues(np.linspace(0.2, 1, num_non_top_10))  # Blue shades from light to dark

# Counter for blue shades
blue_idx = 0

# Plot for each article
for idx, (index, row) in enumerate(df.iterrows()):
    article_name = row['name']
    # Choose color based on top-10 or not
    if article_name in top_10_articles:
        color = top_10_colors[top_10_articles.index(article_name)]
    else:
        color = blue_colors[blue_idx]
        blue_idx += 1
    # Plot the time series for the article
    line, = plt.plot(range(len(month_columns)), row[month_columns], color=color, label=article_name if article_name in top_5_articles else None)

# Labels and layout
plt.xticks(range(len(month_columns)), month_columns, rotation=45)
plt.xlabel('Month')
plt.ylabel('Number of Movements')
plt.title('Monthly Movements of Articles (Time Series Plot)')
plt.grid(True)

# Legend for top-5 articles only
handles, labels = plt.gca().get_legend_handles_labels()
if labels:
    plt.legend(handles, labels, title="Top-5 Articles (ABC Analysis)", loc='upper right')

plt.tight_layout()

# Save the time series plot
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Output directory '{output_dir}' created.")
plt.savefig(os.path.join(output_dir, 'monthly_timeseries.png'), bbox_inches='tight')

# Display the plot
plt.show()

# Step 8: Calculate cumulative percentage of movements
total_movements = df_sorted['last_6_months'].sum()
df_sorted['cumulative_movements'] = df_sorted['last_6_months'].cumsum()
df_sorted['cumulative_percentage'] = df_sorted['cumulative_movements'] / total_movements * 100

# Step 9: Assign ABC categories based on cumulative percentages
def assign_abc_category(cumulative_percentage):
    if cumulative_percentage <= 80:  # A: 80% of movements
        return 'A'
    elif cumulative_percentage <= 95:  # B: Next 15% of movements
        return 'B'
    else:  # C: Remaining 5% of movements
        return 'C'

df_sorted['abc_category'] = df_sorted['cumulative_percentage'].apply(assign_abc_category)

# Step 10: Display results
result_df = df_sorted[['id', 'number', 'name', 'last_6_months', 'abc_category']]
print("\nABC Analysis Results:")
print(result_df)

# Summary of categories
summary = result_df.groupby('abc_category').agg({
    'id': 'count',
    'last_6_months': 'sum'
}).rename(columns={'id': 'Article_Count', 'last_6_months': 'Total_Movements'})
summary['Percent_Articles'] = summary['Article_Count'] / len(df) * 100
summary['Percent_Movements'] = summary['Total_Movements'] / total_movements * 100

# Step 11: Visualization of ABC Analysis with colored categories
plt.figure(figsize=(12, 8))

# Calculate the number of articles in each category
a_count = summary.loc['A', 'Article_Count'] if 'A' in summary.index else 0
b_count = summary.loc['B', 'Article_Count'] if 'B' in summary.index else 0
c_count = summary.loc['C', 'Article_Count'] if 'C' in summary.index else 0

# Define segment boundaries
a_end = a_count
b_end = a_count + b_count
c_end = a_count + b_count + c_count

# Plot cumulative distribution in segments with different colors
if a_count > 0:
    plt.plot(range(a_end), df_sorted['cumulative_percentage'].iloc[:a_end], marker='o', color='r', label='Category A')
if b_count > 0:
    plt.plot(range(a_end-1, b_end), df_sorted['cumulative_percentage'].iloc[a_end-1:b_end], marker='o', color='g', label='Category B')
if c_count > 0:
    plt.plot(range(b_end-1, c_end), df_sorted['cumulative_percentage'].iloc[b_end-1:c_end], marker='o', color='b', label='Category C')

# Horizontal lines for A, B, C
plt.axhline(y=80, color='r', linestyle='--', label='80% Movements (A)')
plt.axhline(y=95, color='g', linestyle='--', label='95% Movements (B)')

# Vertical markers for article counts in A, B, C
a_boundary = a_count - 0.5
b_boundary = (a_count + b_count) - 0.5

# Vertical lines for boundaries
if a_count > 0:
    plt.axvline(x=a_boundary, color='r', linestyle='--', alpha=0.5, label=f'A: {int(a_count)} Articles')
if b_count > 0:
    plt.axvline(x=b_boundary, color='g', linestyle='--', alpha=0.5, label=f'B: {int(b_count)} Articles')

# Labels with dynamic totals
total_articles = len(df)
total_movements = int(df_sorted['last_6_months'].sum())
plt.xlabel(f'Individual Articles (Sorted by Movement Frequency) | Total Articles: {total_articles}')
plt.ylabel(f'Cumulative Percentage of Movements [%] | Total Movements: {total_movements}')
plt.title('ABC Analysis: Cumulative Distribution of Movements')
plt.legend(loc='center right')
plt.grid(True)

# Summary as a textbox inside the plot
summary_text = "Summary of ABC Categories:\n"
for category in ['A', 'B', 'C']:
    if category in summary.index:
        summary_text += (f"Category {category}: {int(summary.loc[category, 'Article_Count'])} Articles "
                         f"({summary.loc[category, 'Percent_Articles']:.2f}%), "
                         f"Total Movements: {int(summary.loc[category, 'Total_Movements'])}, "
                         f"({summary.loc[category, 'Percent_Movements']:.2f}%)\n")

# Textbox in the plot (bottom right)
plt.text(0.95, 0.05, summary_text, transform=plt.gca().transAxes, fontsize=10,
         verticalalignment='bottom', horizontalalignment='right',
         bbox=dict(facecolor='white', alpha=0.8))

# Adjust layout
plt.tight_layout()

# Save the ABC Analysis plot
plt.savefig(os.path.join(output_dir, 'abc_analysis.png'), bbox_inches='tight')

# Display the plot
plt.show()

# Step 12: Save results to a CSV file in the output directory
output_file = os.path.join(output_dir, 'abc_analysis_results.csv')
try:
    result_df.to_csv(output_file, index=False)
    print(f"\nResults saved to '{output_file}'.")
except Exception as e:
    print(f"Error saving the results file: {e}")
    exit()
