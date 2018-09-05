import os
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from app import db, login_manager



class User(UserMixin, db.Model):
    """database for users in website
    Arguments:
        db id -- invidiual uniq id of user
    """
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(40),nullable=False, unique=True)
    name = db.Column(db.String(40), nullable=False)
    surname = db.Column(db.String(40), nullable=False)
    position = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    phone = db.Column(db.Integer)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {} {}>'.format(self.name, self.surname)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def avatar(self):
        if self.position == 'B':
            return os.path.join('..','static', 'img','budowa.jpg')
        else:
            return os.path.join('..','static', 'img','biuro.jpg')


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


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
