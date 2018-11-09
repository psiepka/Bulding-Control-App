from flask import Blueprint


bp = Blueprint('company', __name__, template_folder='templates')


from app.company import routes