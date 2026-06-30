import pdfplumber
import pandas as pd
from pathlib import Path

def convert_pdf_to_excel(input_path, output_path):
    """Extract tables from PDF to Excel."""
    all_tables = []

    try:
        with pdfplumber.open(str(input_path)) as pdf:
            for page in pdf.pages:
                try:
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            if table and len(table) > 1:
                                df = pd.DataFrame(table[1:], columns=table[0])
                                all_tables.append(df)
                except Exception:
                    continue
    except Exception as e:
        raise RuntimeError(f"Could not open PDF: {e}")

    if not all_tables:
        # Fallback: extract text
        try:
            with pdfplumber.open(str(input_path)) as pdf:
                text_data = []
                for i, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text()
                        if text:
                            text_data.append({"Page": i + 1, "Content": text})
                    except Exception:
                        continue
                if text_data:
                    df = pd.DataFrame(text_data)
                    df.to_excel(str(output_path), index=False, engine='openpyxl')
                    return
        except Exception:
            pass
        raise ValueError("No tables or text could be extracted from the PDF")

    # Write all tables to Excel
    with pd.ExcelWriter(str(output_path), engine='openpyxl') as writer:
        for i, df in enumerate(all_tables):
            sheet_name = f"Table_{i+1}"[:31]
            df.to_excel(writer, sheet_name=sheet_name, index=False)
