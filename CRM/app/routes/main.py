# app/routes/main.py

from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('base.html')

@main_bp.route('/dashboard')
def dashboard():
    # Later: query segments from database
    return render_template('dashboard.html')
