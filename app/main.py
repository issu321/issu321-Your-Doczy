from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Conversion

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    recent_conversions = Conversion.query.filter_by(user_id=current_user.id)\
        .order_by(Conversion.created_at.desc()).limit(10).all()
    return render_template('dashboard.html', conversions=recent_conversions)
