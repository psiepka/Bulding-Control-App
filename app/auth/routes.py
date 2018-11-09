import os, re
from app import db
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, login_user, current_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordForm, ResetPasswordRequestForm
from app.models import User, Post, Company, Build, Employee, JobApp
from app.auth.email import send_password_reset_email




@bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.nickname.data).first()
        if user == None or not user.check_password(form.password.data):
            flash('Bad username or password mate! :(')
            return redirect(url_for('auth.login'))
        flash('Congrats now you are logged as {}'.format(
            form.nickname.data))
        login_user(user, remember=form.remeber_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.blog')
        return redirect(next_page)
    return render_template('login.html', form=form, title='Log in' )


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.blog'))


@bp.route('/registration',  methods=['GET','POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(nickname=form.nickname.data, name=form.name.data, surname=form.surname.data,
                    phone=form.phone.data, gender=form.gender.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congrats you register in our app ! ')
        return redirect(url_for('auth.login'))
    return render_template('registration.html', form=form, title='Register in ')


@bp.route('/reset_password', methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instruction to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html', title='Reset password', form=form)


@bp.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_passwordd_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)
