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
from app.build.forms import BuildForm, EditBuildForm
from app.build import bp


@bp.route('/builds')
def builds():
    page = request.args.get('page', 1, type=int)
    builds = Build.query.paginate(page, current_app.config['POST_PER_PAGE'], False)
    next_url = url_for('build.builds', page=builds.next_num) \
        if builds.has_next else None
    prev_url = url_for('build.builds', page=builds.prev_num) \
        if builds.has_prev else None
    heading='All register in builds'
    return render_template('builds.html',heading=heading , next_url=next_url,
                            builds=builds.items, title='All builds', prev_url=prev_url)


@bp.route('/builds/add', methods=['GET','POST'])
@login_required
def add_build():
    form = BuildForm()
    if form.validate_on_submit():
        if current_user.admin or (current_user.worker_id != None and current_user.worker_id.firm.verified):
            build = Build(name=form.name.data, specification=form.specification.data,
                        category=form.category.data, worth=form.worth.data, place=form.place.data,
                        creater=current_user, verified=True, contractor=current_user.worker_id.firm)
        elif current_user.worker_id != None:
            build = Build(name=form.name.data, specification=form.specification.data,
                            category=form.category.data, worth=form.worth.data, place=form.place.data,
                            creater=current_user, contractor=current_user.worker_id.firm)
        else:
            build = Build(name=form.name.data, specification=form.specification.data,
                            category=form.category.data, worth=form.worth.data, place=form.place.data,
                            creater=current_user)
        db.session.add(build)
        db.session.commit()
        flash('Congratulation you create your own build!')
        return redirect(url_for('build.builds'))
    return render_template('add_build.html', form=form, title='Create Build')


@bp.route('/builds/<int:build_id>', methods=['GET','POST'])
def profile_build(build_id):
    page = request.args.get('page', 1, type=int)
    page_c = request.args.get('page_c', 1, type=int)
    build = Build.query.filter_by(id=build_id).first_or_404()
    posts1 = Post.query.filter_by(build_forum=build, private_company=False).order_by(
        Post.timestamp.desc()).paginate(page, current_app.config['POST_PER_PAGE'], False)
    form1 = PostForm(prefix="form1")
    posts2 = Post.query.filter_by(build_forum=build, private_company=True).order_by(
        Post.timestamp.desc()).paginate(page_c, current_app.config['POST_PER_PAGE'], False)
    form2 = PostForm(prefix="form2")
    if form1.validate_on_submit():
        post = Post(body=form1.body.data, author=current_user, build_forum=build)
        db.session.add(post)
        db.session.commit()
        flash('You post is now avaible ')
        return redirect(url_for('build.profile_build',build_id=build.id))
    if current_user.is_authenticated and current_user.worker_id.firm is build.contractor:
        if form2.validate_on_submit():
            post = Post(body=form2.body.data, author=current_user, build_forum=build, private_company=True)
            db.session.add(post)
            db.session.commit()
            flash('You post is now avaible ')
            return redirect(url_for('build.profile_build',build_id=build.id))
    next_url = url_for('build.profile_build', build_id=build.id, page=posts1.next_num) \
        if posts1.has_next else None
    prev_url = url_for('build.profile_build', build_id=build.id, page=posts1.prev_num) \
        if posts1.has_prev else None
    next_url_c = url_for('build.profile_build', build_id=build.id, page=posts1.next_num) \
        if posts1.has_next else None
    prev_url_c = url_for('build.profile_build', build_id=build.id, page=posts1.prev_num) \
        if posts1.has_prev else None
    return render_template('profile_build.html', build=build, form1=form1, form2=form2, next_url=next_url, next_url_c=next_url_c,
                            posts1=posts1.items, posts2=posts2.items, title=build.name, prev_url=prev_url, prev_url_c=prev_url_c)





@bp.route('/builds/<int:build_id>/edit', methods=['GET','POST'])
@login_required
def edit_build(build_id):
    build = Build.query.filter_by(id=build_id).first_or_404()
    form = EditBuildForm(build.name)
    if current_user.creatures is build.creater or (current_user.worker_id and current_user.worker_id.firm is build.contractor):
        if form.validate_on_submit():
            build.name = form.name.data
            build.specification = form.specification.data
            build.category = form.category.data
            build.start_date = form.start_date.data if form.start_date.data else None
            build.end_date = form.end_date.data
            build.contractor.name = form.contractor.data
            build.worth = form.worth.data
            build.place = form.place.data
            db.session.commit()
            return redirect(url_for('build.builds'))
        elif request.method == 'GET':
            form.name.data = build.name
            form.specification.data = build.specification
            form.category.data = build.category
            form.start_date.data = build.start_date
            form.end_date.data = build.end_date
            form.contractor.data = build.contractor.name
            form.worth.data = build.worth
            form.place.data = build.place
        return render_template('edit_build.html', build=build, form=form, title=build.name +' edition')
    else:
        return redirect(url_for('build.builds'))