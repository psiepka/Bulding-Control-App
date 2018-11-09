import os, re
from app import db
from flask import render_template, flash, redirect, url_for, request, current_app, g
from flask_login import login_required, login_user, current_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
from app.forms import PostForm, SearchForm
from app.models import User, Post, Company, Build, Employee, JobApp
from app.main.forms import EditProfileForm, JobAppForm
from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.blog'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POST_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POST_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('index.html', title='Search', head_data='Search results:', posts=posts,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/', methods=['GET','POST'])
@bp.route('/blog', methods=['GET','POST'])
def blog():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(
        private_company=False, company_id=None,build_id=None).order_by(
        Post.timestamp.desc()).paginate(page, current_app.config['POST_PER_PAGE'], False)
    next_url = url_for('blog', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('blog', page=posts.prev_num) \
        if posts.has_prev else None
    form = PostForm()
    head = 'Blog'
    if form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('You post is now avaible ')
        return redirect(url_for('main.blog'))
    return render_template('index.html', head_data=head, posts=posts.items, next_url=next_url,
                            form=form,  title='MicroBlog', prev_url=prev_url)


@bp.route('/home')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POST_PER_PAGE'], False)
    head = 'Followers activity'
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', head_data=head, posts=posts.items,
                            title='HomePage', next_url=next_url, prev_url=prev_url)


@bp.route('/user/<nickname>', methods=['GET','POST'])
@login_required
def profile_user(nickname):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(nickname=nickname).first_or_404()
    posts = Post.query.filter_by(author=user, private_company=False).order_by(
        Post.timestamp.desc()).paginate(
        page, current_app.config['POST_PER_PAGE'], False)
    form = JobAppForm()
    next_url = url_for('main.profile_user', nickname=user.nickname, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.profile_user', nickname=user.nickname, page=posts.prev_num) \
        if posts.has_prev else None
    if form:
        if form.validate_on_submit():
            job = JobApp(sender=current_user.worker_id, recipient=user, salary=form.salary.data,
                        position=form.position.data, company_id=current_user.worker_id.firm)
            db.session.add(job)
            db.session.commit()
            flash('You send ' + user.nickname + ' work proposition')
            return redirect(url_for('main.profile_user', nickname=user.nickname))
    return render_template('profile_user.html',posts=posts.items, next_url=next_url,
                            prev_url=prev_url, form=form, user=user, title=nickname+' profile')


@bp.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.nickname)
    if form.validate_on_submit():
        current_user.nickname = form.nickname.data
        current_user.description = form.description.data
        current_user.phone = form.phone.data
        current_user.gender = form.gender.data
        current_user.linkedin = form.linkedin.data
        if form.avatar.data:
            ex = [i for i in re.split("\W+", current_app.config['IMAGES']) if len(i)>1]
            f_img = os.path.join(
                'app', 'static', 'upload', 'avatar', 'avatar_' + str(current_user.id) + '.')
            for extension in ex:
                if os.path.exists(f_img + extension):
                    os.remove(f_img + extension)
            f = form.avatar.data
            f_ext = f.filename.rsplit('.',1)[1].lower()
            filename = secure_filename('avatar '+str(current_user.id)+'.'+f_ext)
            f.save(os.path.join(
                current_app.config['UPLOAD_FOLDER'], 'avatar', filename
            ))
        if form.curriculum_vitae.data:
            f = form.curriculum_vitae.data
            f_ext = f.filename.rsplit('.',1)[1]
            filename = secure_filename('cv '+str(current_user.id)+'.'+f_ext)
            f.save(os.path.join(
                current_app.config['UPLOAD_FOLDER'], 'cv', filename
            ))
        db.session.commit()
        flash('You changes are save on profile')
        return redirect(url_for('main.profile_user', nickname=current_user.nickname))
    elif request.method == 'GET':
        form.nickname.data = current_user.nickname
        form.gender.data = current_user.gender
        form.description.data = current_user.description
        form.phone.data = current_user.phone
        form.linkedin.data = current_user.linkedin
    return render_template('edit_profile.html', form=form, title='Edit profile')


@bp.route('/user/<nickname>/follow')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cant follow yourself!')
        return redirect(url_for('main.profile_user', nickname=nickname))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(nickname))
    return redirect(url_for('main.profile_user', nickname=nickname))


@bp.route('/user/<nickname>/unfollow')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cant unfollow yourself!')
        return redirect(url_for('main.profile_user', nickname=nickname))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are  not following {}!'.format(nickname))
    return redirect(url_for('main.profile_user', nickname=nickname))


@bp.route('/user/<nickname>/work_offer')
@login_required
def user_offers(nickname):
    user = User.query.filter_by(nickname=nickname).first_or_404()
    offers = current_user.check_offer_user(user)
    return render_template('work_offers.html', user=user, offers=offers)


@bp.route('/work_offer', methods=['GET','POST'])
@login_required
def self_workoffer():
    offers = current_user.self_receive_offer()
    if request.method == 'POST':
        if JobApp.query.get(request.form['id']):
            job = JobApp.query.get(request.form['id'])
            a = Employee(user=current_user, firm=job.company_id,
                position=job.position, salary=job.salary)
            db.session.add(a)
            db.session.delete(job)
            db.session.commit()
            flash('Congratulation now you working for '+ a.firm.name)
            return redirect(url_for('main.self_workoffer'))
    return render_template('work_offers.html', offers=offers)