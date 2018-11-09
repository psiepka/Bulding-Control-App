from app import create_app, db
from app.models import User, Company, Build, Employee, JobApp, Post


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'User':User, 'Post':Post, 'Company':Company, 'Employee':Employee, 'Build':Build, 'JobApp':JobApp}