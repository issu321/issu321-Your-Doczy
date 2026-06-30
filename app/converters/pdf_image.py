import os
import zipfile
from pathlib import Path

def convert_pdf_to_images(input_path, output_path):
    """Convert PDF pages to images.
    Tries PyMuPDF first (fast), falls back to pure Python (slow but reliable).
    """
    # Try PyMuPDF first
    try:
        return _convert_with_pymupdf(input_path, output_path)
    except Exception as e:
        print(f"[PyMuPDF failed: {e}], trying pure Python fallback...")

    # Fallback to pure Python
    try:
        return _convert_with_pypdf(input_path, output_path)
    except Exception as e:
        raise RuntimeError(f"Both PyMuPDF and pure Python failed: {e}")

def _convert_with_pymupdf(input_path, output_path):
    """Fast conversion using PyMuPDF."""
    import fitz
    from PIL import Image as PILImage

    image_paths = []
    temp_dir = None
    doc = None

    try:
        doc = fitz.open(str(input_path))
        if len(doc) == 0:
            raise ValueError("PDF has no pages")

        temp_dir = Path(output_path).parent / f"temp_{Path(output_path).stem}"
        temp_dir.mkdir(parents=True, exist_ok=True)

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # Render with default settings
            pix = page.get_pixmap()

            # Convert to PIL
            img = PILImage.frombytes("RGB", [pix.width, pix.height], pix.samples)

            img_path = temp_dir / f"page_{page_num + 1:03d}.png"
            img.save(str(img_path), "PNG")
            image_paths.append(img_path)

        if not image_paths:
            raise ValueError("No pages rendered")

        with zipfile.ZipFile(str(output_path), 'w', zipfile.ZIP_DEFLATED) as zf:
            for img_path in image_paths:
                zf.write(str(img_path), img_path.name)

    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass
        for img_path in image_paths:
            try:
                if img_path.exists():
                    img_path.unlink()
            except Exception:
                pass
        if temp_dir is not None and temp_dir.exists():
            try:
                for f in temp_dir.iterdir():
                    try:
                        f.unlink()
                    except Exception:
                        pass
                temp_dir.rmdir()
            except Exception:
                pass

def _convert_with_pypdf(input_path, output_path):
    """Pure Python fallback using pypdf + PIL."""
    from pypdf import PdfReader
    from PIL import Image as PILImage, ImageDraw, ImageFont

    image_paths = []
    temp_dir = None

    try:
        reader = PdfReader(str(input_path))
        num_pages = len(reader.pages)

        if num_pages == 0:
            raise ValueError("PDF has no pages")

        temp_dir = Path(output_path).parent / f"temp_{Path(output_path).stem}"
        temp_dir.mkdir(parents=True, exist_ok=True)

        for page_num in range(num_pages):
            page = reader.pages[page_num]

            # Get dimensions
            try:
                width = float(page.mediabox.width)
                height = float(page.mediabox.height)
            except Exception:
                width, height = 612.0, 792.0

            scale = 150 / 72.0
            img_width = max(int(width * scale), 100)
            img_height = max(int(height * scale), 100)

            img = PILImage.new('RGB', (img_width, img_height), (255, 255, 255))
            draw = ImageDraw.Draw(img)

            # Extract text with error handling
            text = None
            try:
                text = page.extract_text()
            except Exception:
                try:
                    text = page.extract_text(extraction_mode="layout")
                except Exception:
                    text = None

            if text:
                try:
                    font = ImageFont.truetype("arial.ttf", 14)
                except Exception:
                    font = ImageFont.load_default()

                y = 10
                for line in text.split('\n')[:80]:
                    line = line.strip()
                    if line:
                        if len(line) > 120:
                            line = line[:120] + "..."
                        draw.text((10, y), line, fill=(0, 0, 0), font=font)
                        y += 18
                        if y > img_height - 20:
                            break
            else:
                try:
                    font = ImageFont.truetype("arial.ttf", 20)
                except Exception:
                    font = ImageFont.load_default()
                draw.text((10, 10), f"Page {page_num + 1}", fill=(100, 100, 100), font=font)
                draw.text((10, 40), "(No extractable text)", fill=(150, 150, 150), font=font)

            img_path = temp_dir / f"page_{page_num + 1:03d}.png"
            img.save(str(img_path), "PNG")
            image_paths.append(img_path)

        if not image_paths:
            raise ValueError("No images generated")

        with zipfile.ZipFile(str(output_path), 'w', zipfile.ZIP_DEFLATED) as zf:
            for img_path in image_paths:
                zf.write(str(img_path), img_path.name)

    finally:
        for img_path in image_paths:
            try:
                if img_path.exists():
                    img_path.unlink()
            except Exception:
                pass
        if temp_dir is not None and temp_dir.exists():
            try:
                for f in temp_dir.iterdir():
                    try:
                        f.unlink()
                    except Exception:
                        pass
                temp_dir.rmdir()
            except Exception:
                pass
