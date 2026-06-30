import pandas as pd
from pathlib import Path

def convert_csv_to_excel(input_path, output_path):
    """Convert CSV file to Excel."""
    df = pd.read_csv(input_path)
    df.to_excel(output_path, index=False, engine='openpyxl')
