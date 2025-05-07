# app/routes/components.py
from flask import render_template, Blueprint

components = Blueprint('components', __name__)

@components.route('/components')
def index():
    return render_template('components/index.html', title='Компоненты')