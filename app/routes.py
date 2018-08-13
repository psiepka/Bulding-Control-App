from app import app
from flask import render_template

@app.route('/')
def index():
    user = {'username':'Patryk'}
    return render_template('index.html', user=user)