from pathlib import Path

def convert_pdf_to_word(input_path, output_path):
    """Convert PDF to Word document."""
    try:
        from pdf2docx import Converter
    except ImportError:
        raise ImportError("pdf2docx is required. Install with: pip install pdf2docx")

    cv = Converter(str(input_path))
    cv.convert(str(output_path), start=0, end=None)
    cv.close()
