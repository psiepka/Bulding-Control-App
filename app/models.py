import os
from datetime import datetime
from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.types import Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from flask_admin.contrib.sqla import ModelView
from app import db, login_manager, admin


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

employees = db.Table('employees',
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id')),
    db.Column('build_id', db.Integer, db.ForeignKey('build.id'))
)

class User(UserMixin, db.Model):
    """database for users in website
    Arguments:
        db id -- invidiual uniq id of user
    """
    id = Column(Integer, primary_key=True)
    nickname = Column(String(40), nullable=False, unique=True)
    name = Column(String(40), nullable=False)
    surname = Column(String(40), nullable=False)
    education = Column(String(40))
    linkedin = Column(String(100))
    email = Column(String(120), nullable=False, unique=True)
    password_hash = Column(String(128))
    gender = Column(String(20), nullable=False)
    phone = Column(Integer)
    last_seen = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)
    admin = Column(Boolean, default=False)
    posts = relationship('Post', backref='author', lazy='dynamic')
    worker_id = relationship('Employee', uselist=False, back_populates="user")
    creatures = relationship('Build', backref='creater', lazy='dynamic')
    followed = relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {} {}>'.format(self.name, self.surname)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self):
        f_img = os.path.join('app', 'static', 'upload', 'avatar', 'avatar_' + self.nickname)
        if os.path.exists(f_img+'.'+'jpg'):
            return os.path.join('..', 'static', 'upload', 'avatar', 'avatar_' + self.nickname+'.jpg')
        elif os.path.isfile(f_img+'.'+'jpeg'):
            return os.path.join('..', 'static', 'upload', 'avatar', 'avatar_' + self.nickname+'.jpeg')
        elif os.path.isfile(f_img+'.'+'png'):
            return os.path.join('..', 'static', 'upload', 'avatar', 'avatar_' + self.nickname+'.png')
        elif self.gender == 'male':
            return os.path.join('..','static', 'img','male.jpg')
        else:
            return os.path.join('..','static', 'img','female.jpg')

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            return self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            return self.followed.remove(user)

    def followed_posts(self):
        followed = Post.query.join(
            followers.c.followed_id == Post.user_id).filter_by(
                followers.c.follower_id == self.id).filter_by(
                    Post.company_private == False).order_by(
                    Post.timestamp.desc())
        own = Post.query.filter_by(user_id=self.id).filter_by(company_private=False)
        return followed.union(own).order_by(Post.timestamp.desc())


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
    user_id = Column(Integer, ForeignKey('user.id'))
    build_id = Column(Integer, ForeignKey('build.id'))
    company_id = Column(Integer, ForeignKey('company.id'))
    private_company = Column(Boolean, default=False)

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Company(db.Model):
    """model database of building company
    Arguments:
        contains all administrators and employees of company
    """
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(1000))
    web_page = Column(String(100), unique=True)
    verified = Column(Boolean, default=False)
    workers = relationship('Employee', backref='firm', lazy='dynamic')
    builds = relationship('Build', backref='contractor', lazy='dynamic')
    posts = relationship('Post', backref='company_forum', lazy='dynamic')

    def __repr__(self):
        return "<Company {}>".format(self.name)

    def is_working(self, user):
        return user.worker_id in self.workers

    def number_workers(self):
        return self.workers.count()

    def add_build(self, building):
        if not building in self.builds.all():
            self.builds.append(building)

    def del_build(self, building):
        if building in self.builds.all():
            self.builds.remove(building)


class Employee(db.Model):
    """Worker model
    Arguments:
    Position(str), salary(int), date_join(datetime)
    """
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='worker_id')
    company = Column(Integer, ForeignKey('company.id'))
    admin = Column(Boolean, default=False)
    position = Column(String(100), nullable=False)
    salary = Column(Integer)
    date_join = Column(DateTime, default=datetime.utcnow)
    builds = relationship("Build", secondary=employees, backref=db.backref('employers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return "<employee {}>".format(self.user.nickname)

    def is_building(self, build):
        return self.builds.filter(employees.c.build_id == build.id).count() > 0

    def add_build(self, build):
        if not self.is_building(build):
            self.builds.append(build)

    def del_build(self, build):
        if self.is_building(build):
            self.builds.remove(user)


class Build(db.Model):
    """model database of builds
    Object must belong to some company which is responsible for process of building
    """
    __tablename__ = 'build'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    specification = Column(String(2000), nullable=False)
    category = Column(String(200), nullable=False)
    worth = Column(Integer, nullable=False)
    place = Column(String(200), nullable=False)
    post_date = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    verified = Column(Boolean, default=False)
    creater_id = Column(Integer, ForeignKey('user.id'))
    contractor_id = Column(Integer, ForeignKey('company.id'))
    posts = relationship('Post', backref='build_forum', lazy='dynamic')

    def __repr__(self):
        return "<Build {}>".format(self.name)


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Build, db.session))
admin.add_view(ModelView(Company, db.session))