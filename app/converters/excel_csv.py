import pandas as pd
from pathlib import Path

def convert_excel_to_csv(input_path, output_path):
    """Convert Excel file to CSV."""
    df = pd.read_excel(input_path)
    df.to_csv(output_path, index=False, encoding='utf-8')
