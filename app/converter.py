import os
import uuid
import traceback
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Conversion
from app.converters.image_pdf import convert_images_to_pdf
from app.converters.pdf_image import convert_pdf_to_images
from app.converters.pdf_word import convert_pdf_to_word
from app.converters.word_pdf import convert_word_to_pdf
from app.converters.ppt_pdf import convert_ppt_to_pdf
from app.converters.pdf_ppt import convert_pdf_to_ppt
from app.converters.excel_csv import convert_excel_to_csv
from app.converters.csv_excel import convert_csv_to_excel
from app.converters.excel_pdf import convert_excel_to_pdf
from app.converters.pdf_excel import convert_pdf_to_excel

bp = Blueprint('converter', __name__)

ALLOWED_EXTENSIONS = {
    'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp',
    'doc', 'docx', 'ppt', 'pptx',
    'xls', 'xlsx', 'csv'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_unique_filename(original_name):
    ext = Path(original_name).suffix
    return f"{uuid.uuid4().hex}{ext}"

def save_uploaded_file(file):
    if not file or file.filename == '':
        return None
    if not allowed_file(file.filename):
        return None
    filename = secure_filename(file.filename)
    unique_name = get_unique_filename(filename)
    upload_path = current_app.config['UPLOAD_FOLDER'] / unique_name
    file.save(str(upload_path))
    return upload_path, filename

def log_conversion(original_name, converted_name, conv_type, status='completed'):
    conv = Conversion(
        user_id=current_user.id,
        original_filename=original_name,
        converted_filename=converted_name,
        conversion_type=conv_type,
        status=status
    )
    db.session.add(conv)
    db.session.commit()
    return conv

def cleanup_files(*paths):
    for p in paths:
        if p is not None:
            try:
                p = Path(p)
                if p.exists():
                    p.unlink()
            except Exception:
                pass

def handle_conversion(input_path, original_name, output_name, output_path, 
                       convert_func, conv_type, *extra_cleanup):
    """Universal conversion handler with bulletproof error handling."""
    try:
        convert_func(str(input_path), str(output_path))

        if not output_path.exists():
            raise RuntimeError("Output file was not created")
        if output_path.stat().st_size == 0:
            output_path.unlink()
            raise RuntimeError("Output file is empty")

        log_conversion(original_name, output_name, conv_type)
        return jsonify({'success': True, 'download_url': f'/convert/download/{output_name}'})

    except Exception as e:
        error_msg = str(e)
        tb = traceback.format_exc()
        print(f"[CONVERSION ERROR] {conv_type}: {error_msg}\n{tb}")

        cleanup_files(output_path, *extra_cleanup)

        try:
            log_conversion(original_name, output_name, conv_type, status='failed')
        except Exception:
            pass

        return jsonify({'error': error_msg, 'trace': tb}), 500

    finally:
        cleanup_files(input_path)

# ============================================
# IMAGES TO PDF
# ============================================
@bp.route('/images-to-pdf', methods=['POST'])
@login_required
def images_to_pdf():
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No images uploaded'}), 400

    image_paths = []
    original_names = []
    for file in files:
        result = save_uploaded_file(file)
        if result:
            image_paths.append(result[0])
            original_names.append(result[1])

    if not image_paths:
        return jsonify({'error': 'No valid images uploaded'}), 400

    output_name = f"{uuid.uuid4().hex}.pdf"
    output_path = current_app.config['CONVERTED_FOLDER'] / output_name

    try:
        convert_images_to_pdf([str(p) for p in image_paths], str(output_path))

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError("PDF was not created successfully")

        log_conversion(', '.join(original_names[:3]) + ('...' if len(original_names) > 3 else ''), 
                      output_name, 'images_to_pdf')
        return jsonify({'success': True, 'download_url': f'/convert/download/{output_name}'})
    except Exception as e:
        cleanup_files(output_path)
        return jsonify({'error': str(e)}), 500
    finally:
        cleanup_files(*image_paths)

# ============================================
# PDF TO IMAGES
# ============================================
@bp.route('/pdf-to-images', methods=['POST'])
@login_required
def pdf_to_images():
    result = save_uploaded_file(request.files.get('file'))
    if not result:
        return jsonify({'error': 'Invalid PDF file'}), 400

    input_path, original_name = result
    output_name = f"{uuid.uuid4().hex}.zip"
    output_path = current_app.config['CONVERTED_FOLDER'] / output_name

    return handle_conversion(input_path, original_name, output_name, output_path,
                            convert_pdf_to_images, 'pdf_to_images')

# ============================================
# PDF TO WORD
# ============================================
@bp.route('/pdf-to-word', methods=['POST'])
@login_required
def pdf_to_word():
    result = save_uploaded_file(request.files.get('file'))
    if not result:
        return jsonify({'error': 'Invalid PDF file'}), 400

    input_path, original_name = result
    output_name = f"{uuid.uuid4().hex}.docx"
    output_path = current_app.config['CONVERTED_FOLDER'] / output_name

    return handle_conversion(input_path, original_name, output_name, output_path,
                            convert_pdf_to_word, 'pdf_to_word')

# ============================================
# WORD TO PDF
# ============================================
@bp.route('/word-to-pdf', methods=['POST'])
@login_required
def word_to_pdf():
    result = save_uploaded_file(request.files.get('file'))
    if not result:
        return jsonify({'error': 'Invalid Word file'}), 400

    input_path, original_name = result
    output_name = f"{uuid.uuid4().hex}.pdf"
    output_path = current_app.config['CONVERTED_FOLDER'] / output_name

    return handle_conversion(input_path, original_name, output_name, output_path,
                            convert_word_to_pdf, 'word_to_pdf')

# ============================================
# PPT TO PDF
# ============================================
@bp.route('/ppt-to-pdf', methods=['POST'])
@login_required
def ppt_to_pdf():
    result = save_uploaded_file(request.files.get('file'))
    if not result:
        return jsonify({'error': 'Invalid PowerPoint file'}), 400

    input_path, original_name = result
    output_name = f"{uuid.uuid4().hex}.pdf"
    output_path = current_app.config['CONVERTED_FOLDER'] / output_name

    return handle_conversion(input_path, original_name, output_name, output_path,
                            convert_ppt_to_pdf, 'ppt_to_pdf')

# ============================================
# PDF TO PPT
# ============================================
@bp.route('/pdf-to-ppt', methods=['POST'])
@login_required
def pdf_to_ppt():
    result = save_uploaded_file(request.files.get('file'))
    if not result:
        return jsonify({'error': 'Invalid PDF file'}), 400

    input_path, original_name = result
    output_name = f"{uuid.uuid4().hex}.pptx"
    output_path = current_app.config['CONVERTED_FOLDER'] / output_name

    return handle_conversion(input_path, original_name, output_name, output_path,
                            convert_pdf_to_ppt, 'pdf_to_ppt')

# ============================================
# EXCEL TO CSV
# ============================================
@bp.route('/excel-to-csv', methods=['POST'])
@login_required
def excel_to_csv():
    result = save_uploaded_file(request.files.get('file'))
    if not result:
        return jsonify({'error': 'Invalid Excel file'}), 400

    input_path, original_name = result
    output_name = f"{uuid.uuid4().hex}.csv"
    output_path = current_app.config['CONVERTED_FOLDER'] / output_name

    return handle_conversion(input_path, original_name, output_name, output_path,
                            convert_excel_to_csv, 'excel_to_csv')

# ============================================
# CSV TO EXCEL
# ============================================
@bp.route('/csv-to-excel', methods=['POST'])
@login_required
def csv_to_excel():
    result = save_uploaded_file(request.files.get('file'))
    if not result:
        return jsonify({'error': 'Invalid CSV file'}), 400

    input_path, original_name = result
    output_name = f"{uuid.uuid4().hex}.xlsx"
    output_path = current_app.config['CONVERTED_FOLDER'] / output_name

    return handle_conversion(input_path, original_name, output_name, output_path,
                            convert_csv_to_excel, 'csv_to_excel')

# ============================================
# EXCEL TO PDF
# ============================================
@bp.route('/excel-to-pdf', methods=['POST'])
@login_required
def excel_to_pdf():
    result = save_uploaded_file(request.files.get('file'))
    if not result:
        return jsonify({'error': 'Invalid Excel file'}), 400

    input_path, original_name = result
    output_name = f"{uuid.uuid4().hex}.pdf"
    output_path = current_app.config['CONVERTED_FOLDER'] / output_name

    return handle_conversion(input_path, original_name, output_name, output_path,
                            convert_excel_to_pdf, 'excel_to_pdf')

# ============================================
# PDF TO EXCEL
# ============================================
@bp.route('/pdf-to-excel', methods=['POST'])
@login_required
def pdf_to_excel():
    result = save_uploaded_file(request.files.get('file'))
    if not result:
        return jsonify({'error': 'Invalid PDF file'}), 400

    input_path, original_name = result
    output_name = f"{uuid.uuid4().hex}.xlsx"
    output_path = current_app.config['CONVERTED_FOLDER'] / output_name

    return handle_conversion(input_path, original_name, output_name, output_path,
                            convert_pdf_to_excel, 'pdf_to_excel')

# ============================================
# DOWNLOAD — BULLETPROOF
# ============================================
@bp.route('/download/<filename>')
@login_required
def download(filename):
    try:
        safe_name = secure_filename(filename)
        if safe_name != filename:
            return jsonify({'error': 'Invalid filename'}), 400

        file_path = current_app.config['CONVERTED_FOLDER'] / safe_name

        if not file_path.exists():
            return jsonify({'error': 'File not found or expired'}), 404

        if file_path.stat().st_size == 0:
            return jsonify({'error': 'File is empty'}), 500

        ext = file_path.suffix.lower()
        mimetypes = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.csv': 'text/csv',
            '.zip': 'application/zip'
        }
        mimetype = mimetypes.get(ext, 'application/octet-stream')

        download_name = f"Your-Doczy-{safe_name}"

        return send_file(
            str(file_path),
            mimetype=mimetype,
            as_attachment=True,
            download_name=download_name
        )
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

# ============================================
# HISTORY
# ============================================
@bp.route('/history')
@login_required
def history():
    conversions = Conversion.query.filter_by(user_id=current_user.id)        .order_by(Conversion.created_at.desc()).all()
    return jsonify([{
        'id': c.id,
        'original': c.original_filename,
        'converted': c.converted_filename,
        'type': c.conversion_type,
        'status': c.status,
        'date': c.created_at.strftime('%Y-%m-%d %H:%M')
    } for c in conversions])
