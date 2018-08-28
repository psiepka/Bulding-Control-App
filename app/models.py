from datetime import datetime
from app import db



class User(db.Model):
    """database for users in website
    Arguments:
        db id -- invidiual uniq id of user
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    surname = db.Column(db.String(40), nullable=False)
    position = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(128))
    phone = db.Column(db.Integer)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {} {}>'.format(self.name, self.surname)

class Post(db.Model):
    """post model database
    Arguments:
        body and building object
    """
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
