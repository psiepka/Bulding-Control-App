from flask import Blueprint


bp = Blueprint('build', __name__, template_folder='templates')


from app.build import routes