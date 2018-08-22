from app import app
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm

@app.route('/')
def index():
    user = {'username':'Patryk'}
    return render_template('index.html', user=user, title='HomePage')


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Congrats now you are logged as {}, remeber me={}'.format(form.nickname.data, form.remeber_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', form=form, title='Log in' )


@app.route('/registration')
def registration():
    form = RegistrationForm()
    return render_template('registration.html', form=form, title='Register in ')


