import os, re
from app import db
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, login_user, current_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
from app.forms import PostForm
from app.models import User, Post, Company, Build, Employee, JobApp
from app.company.forms import CompanyForm, EditCompanyForm
from app.company import bp



def job_required(func):
    '''
    If you decorate a view with this, it will ensure that the current user is
    assign in register company before calling the actual view. (If they are
    not, it redirect to user profile page.)
    '''
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        elif not current_user.worker_id:
            flash('You are not assign to any company.')
            return redirect(url_for('main.profile_user', nickname=current_user.nickname))
        return func(*args, **kwargs)
    return decorated_view


@bp.route('/companies')
def companies():
    page = request.args.get('page', 1, type=int)
    companies = Company.query.paginate(page, current_app.config['POST_PER_PAGE'], False)
    next_url = url_for('companies', page=companies.next_num) \
        if companies.has_next else None
    prev_url = url_for('companies', page=companies.prev_num) \
        if companies.has_prev else None
    return render_template('companies.html', companies=companies.items,
                             title='Companies', next_url=next_url, prev_url=prev_url)



@bp.route('/companies/add', methods=['GET','POST'])
@login_required
def add_company():
    form = CompanyForm()
    if form.validate_on_submit():
        if current_user.admin:
            company = Company(name=form.name.data, description=form.description.data,
                            web_page=form.web_page.data, verified=True)
            creater = Employee(user = current_user, firm=company, admin=True,
                                position="Administrator", )
            db.session.add(company)
            db.session.add(creater)
            db.session.commit()
            flash('Congratulation you create company!')
            return redirect(url_for('companies'))
        else:
            company = Company(name=form.name.data, description=form.description.data,
                                web_page=form.web_page.data)
            creater = Employee(user = current_user, firm=company, admin=True,
                                position="Administrator", )
            db.session.add(company)
            db.session.add(creater)
            db.session.commit()
            flash('Congratulation you create company!')
            return redirect(url_for('companies'))
    return render_template('add_company.html', form=form, title='Create Company')


@bp.route('/companies/<int:company_id>', methods=['GET','POST'])
def profile_company(company_id):
    page = request.args.get('page', 1, type=int)
    company = Company.query.filter_by(id=company_id).first_or_404()
    posts = Post.query.filter_by(
        private_company=False, company_forum=company, build_forum=None).order_by(
            Post.timestamp.desc()).paginate(page, current_app.config['POST_PER_PAGE'], False)
    next_url = url_for('profile_company', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('profile_company', page=posts.prev_num) \
        if posts.has_prev else None
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user, company_forum=company)
        db.session.add(post)
        db.session.commit()
        flash('You post is now avaible ')
        return redirect(url_for('profile_company', company_id=company.id))
    return render_template('profile_company.html', form=form, posts=posts.items, next_url=next_url,
                            company=company, title=company.name+' profile', prev_url=prev_url)


@bp.route('/companies/<int:company_id>/employees')
@login_required
def employees(company_id):
    company = Company.query.filter_by(id=company_id).first_or_404()
    workers = company.workers
    return render_template('employee.html',workers=workers, company=company,
                             title=company.name+' employe')


@bp.route('/companies/<int:company_id>/builds')
@login_required
def company_builds(company_id):
    company = Company.query.filter_by(id=company_id).first_or_404()
    builds = company.builds
    return render_template('builds.html',heading='All builds of ' + company.name,
                             builds=builds, title=company.name +' builds')


@bp.route('/firm', methods=['GET','POST'])
@login_required
@job_required
def company_inside_forum():
    company = current_user.worker_id.firm
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(
        private_company=True, company_id=company.id ,build_id=None).order_by(
        Post.timestamp.desc()).paginate(page, current_app.config['POST_PER_PAGE'], False)
    next_url = url_for('company.company_inside_forum', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('company.company_inside_forum', page=posts.prev_num) \
        if posts.has_prev else None
    form = PostForm()
    head = "Forum of "+company.name
    if form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user,
                    private_company=True, company_id=company.id)
        db.session.add(post)
        db.session.commit()
        flash('You post is now avaible ')
        return redirect(url_for('company.company_inside_forum'))
    return render_template('index.html', head_data=head, posts=posts.items, next_url=next_url,
                            form=form,  title=company.name+" forum", prev_url=prev_url)


@bp.route('/firm/builds')
@login_required
@job_required
def company_inside_builds():
    company = current_user.worker_id.firm
    builds = company.builds
    return render_template('builds.html',heading='List of builds ' + company.name,
                             builds=builds, title=company.name +' builds')


@bp.route('/firm/quit')
@login_required
@job_required
def quit_job():
    emp = Employee.query.filter_by(user=current_user).first()
    company = Company.query.filter_by(name=emp.firm.name).first()
    db.session.delete(emp)
    db.session.commit()
    if company.workers.count() < 1:
        db.session.delete(company)
        db.session.commit()
        return redirect(url_for('main.profile_user', nickname=current_user.nickname))
    return redirect(url_for('main.profile_user', nickname=current_user.nickname))


@bp.route('/firm/config')
@login_required
@job_required
def company_inside_config():
    company = Company.query.filter_by(id=current_user.worker_id.firm.id).first()
    if not current_user.worker_id.admin:
        return redirect(url_for('company.company_inside_forum'))
    form = EditCompanyForm(company.name)
    if form.validate_on_submit():
        company.name = form.name.data
        company.description = form.description.data
        company.web_page = form.web_page.data
        db.session.commit()
        flash('Edit of company are saved.')
        return redirect(url_for('company.profile_company', company_id=company.id))
    elif request.method == 'GET':
        form.name = company.name
        form.description = company.description
        form.web_page = company.web_page
    return render_template('edit_company.html', form=form, title='Edit company data', company=company)
