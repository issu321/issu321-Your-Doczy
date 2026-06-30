import os
from pathlib import Path
from PIL import Image

def convert_images_to_pdf(image_paths, output_path):
    """Convert multiple images to a single PDF.

    Args:
        image_paths: List of string paths to image files
        output_path: String path for output PDF
    """
    images = []
    for path in image_paths:
        path = str(path)  # Ensure string
        img = Image.open(path)
        # Convert to RGB if necessary (handles RGBA, P mode, etc.)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            else:
                img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        images.append(img)

    if not images:
        raise ValueError("No valid images found")

    # Save first image and append rest
    first_image = images[0]
    rest_images = images[1:] if len(images) > 1 else []
    first_image.save(str(output_path), save_all=True, append_images=rest_images, resolution=100.0)

    # Close images to free memory
    for img in images:
        img.close()
