from app import app, db
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, login_user, current_user, logout_user
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm
from app.models import User, Post


@app.route('/')
def index():
    user = {'username':'Patryk'}
    return render_template('index.html', user=user, title='HomePage')


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.nickname.data).first()
        if user == None or not user.check_password(form.password.data):
            flash('Bad username or password mate! :(')
            return redirect(url_for('login'))
        flash('Congrats now you are logged as {}, remeber me={}'.format(form.nickname.data, form.remeber_me.data))
        login_user(user, remember=form.remeber_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', form=form, title='Log in' )


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/registration',  methods=['GET','POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(nickname=form.nickname.data, name=form.name.data, surname=form.surname.data, phone=form.phone.data, position=form.position.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congrats you register in our app ! ')
        return redirect(url_for('login'))
    return render_template('registration.html', form=form, title='Register in ')


