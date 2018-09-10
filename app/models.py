import os
from datetime import datetime
from sqlalchemy import Column, Table
from sqlalchemy.types import Integer, String, Text, DateTime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from app import db, login_manager



class User(UserMixin, db.Model):
    """database for users in website
    Arguments:
        db id -- invidiual uniq id of user
    """
    id = Column(Integer, primary_key=True)
    nickname = Column(String(40), nullable=False, unique=True)
    name = Column(String(40), nullable=False)
    surname = Column(String(40), nullable=False)
    position = Column(String(20), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    password_hash = Column(String(128))
    phone = Column(Integer)
    last_seen = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    company_id = Column(Integer, db.ForeignKey('company.id'))

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
    id = Column(Integer, primary_key=True)
    body = Column(String(200), nullable=False)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    user_id = Column(Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Company(db.Model):
    """model database of building company
    Arguments:
        contains all administrators and employees of company
    """
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(300))
    workers = db.relationship('User', backref='company', lazy='dynamic')
    builds = db.relationship('Build', backref='contractor', lazy='dynamic')

    def hire(self, user):
        if not user in self.workers:
            self.workers.append(user)

    def fire(self, user):
        if user in self.workers:
            self.workers.remove(user)

    def number_workers(self, user):
        return self.workers.count()

    def add_build(self, building):
        if not building in self.builds:
            self.builds.append(building)

    def del_build(self, building):
        if building in self.builds:
            self.builds.remove(building)


class Build(db.Model):
    """model database of builds
    Object must belong to some company which is responsible for process of building
    """
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    specification = Column(String(2000), nullable=False)
    worth = Column(Integer, nullable=False)
    contractor_id = Column(Integer, db.ForeignKey('company.id'))