from app import app, db
from app.models import User, Post, Company, Build, Employee


@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'User':User, 'Post':Post, 'Company':Company, 'Employee':Employee, 'Build':Build}