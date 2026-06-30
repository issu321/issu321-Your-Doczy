#!/usr/bin/env python3
"""Diagnose PyMuPDF installation and test PDF to image conversion."""

import sys

print("=" * 60)
print("YOUR-DOCZY DIAGNOSTIC TOOL")
print("=" * 60)

# 1. Check PyMuPDF version
print("\n[1] Checking PyMuPDF...")
try:
    import fitz
    print(f"    ✅ PyMuPDF installed: version {fitz.__doc__.split()[-1] if hasattr(fitz, '__doc__') else 'unknown'}")
    print(f"       Module path: {fitz.__file__}")
except ImportError as e:
    print(f"    ❌ PyMuPDF NOT installed: {e}")
    print("    Run: pip install PyMuPDF")
    sys.exit(1)

# 2. Check if we can create a simple PDF and convert it
print("\n[2] Testing PDF creation...")
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    import tempfile
    import os

    # Create a test PDF
    test_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    test_pdf.close()

    c = canvas.Canvas(test_pdf.name, pagesize=letter)
    c.drawString(100, 700, "Hello Your-Doczy!")
    c.drawString(100, 680, "This is a test PDF.")
    c.showPage()
    c.save()
    print(f"    ✅ Test PDF created: {test_pdf.name}")
except Exception as e:
    print(f"    ❌ Failed to create test PDF: {e}")
    sys.exit(1)

# 3. Test PDF to image conversion
print("\n[3] Testing PDF to image conversion...")
try:
    doc = fitz.open(test_pdf.name)
    page = doc.load_page(0)

    # Try dpi API
    print("    Trying dpi=200...")
    pix = page.get_pixmap(dpi=200)
    print(f"    ✅ dpi API works! Image size: {pix.width}x{pix.height}")

    # Try matrix API
    print("    Trying matrix API...")
    mat = fitz.Matrix(2, 2)
    pix2 = page.get_pixmap(matrix=mat)
    print(f"    ✅ matrix API works! Image size: {pix2.width}x{pix2.height}")

    doc.close()

    # Cleanup
    os.unlink(test_pdf.name)
    print("\n✅ ALL TESTS PASSED! Your-Doczy PDF to Images should work.")

except Exception as e:
    print(f"    ❌ Conversion failed: {e}")
    import traceback
    traceback.print_exc()
    print("\n❌ PDF to Images will NOT work. Check PyMuPDF installation.")
    sys.exit(1)

print("\n" + "=" * 60)
