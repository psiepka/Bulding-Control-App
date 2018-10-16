import os, re
from app import app, db
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, login_user, current_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime
from app.forms import LoginForm, PostForm, RegistrationForm, EditProfileForm, CompanyForm, BuildForm, JobAppForm, EditBuildForm, ResetPasswordForm, ResetPasswordRequestForm
from app.models import User, Post, Company, Build, followers, Employee, JobApp
from app.email import send_password_reset_email


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/index')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POST_PER_PAGE'], False)
    head = 'Followers activity'
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', head_data=head, posts=posts.items,
                            title='HomePage', next_url=next_url, prev_url=prev_url)


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
        flash('Congrats now you are logged as {}, remeber me={}'.format(
            form.nickname.data, form.remeber_me.data))
        login_user(user, remember=form.remeber_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('blog')
        return redirect(next_page)
    return render_template('login.html', form=form, title='Log in' )


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/registration',  methods=['GET','POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(nickname=form.nickname.data, name=form.name.data, surname=form.surname.data,
                    phone=form.phone.data, gender=form.gender.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congrats you register in our app ! ')
        return redirect(url_for('login'))
    return render_template('registration.html', form=form, title='Register in ')


@app.route('/user/<nickname>', methods=['GET','POST'])
@login_required
def profile_user(nickname):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(nickname=nickname).first_or_404()
    posts = Post.query.filter_by(author=user, private_company=False).order_by(
        Post.timestamp.desc()).paginate(
        page, app.config['POST_PER_PAGE'], False)
    form = JobAppForm()
    next_url = url_for('profile_user', nickname=user.nickname, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('profile_user', nickname=user.nickname, page=posts.prev_num) \
        if posts.has_prev else None
    if form:
        if form.validate_on_submit():
            job = JobApp(sender=current_user.worker_id, recipient=user, salary=form.salary.data,
                        position=form.position.data, company_id=current_user.worker_id.firm)
            db.session.add(job)
            db.session.commit()
            flash('You send ' + user.nickname + ' work proposition')
            return redirect(url_for('profile_user', nickname=user.nickname))
    return render_template('profile_user.html',posts=posts.items, next_url=next_url,
                            prev_url=prev_url, form=form, user=user, title=nickname+' profile')


@app.route('/edit_profile', methods=['GET','POST'])
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
            ex = [i for i in re.split("\W+", app.config['IMAGES']) if len(i)>1]
            f_img = os.path.join(
                'app', 'static', 'upload', 'avatar', 'avatar_' + str(current_user.id) + '.')
            for extension in ex:
                if os.path.exists(f_img + extension):
                    os.remove(f_img + extension)
            f = form.avatar.data
            f_ext = f.filename.rsplit('.',1)[1].lower()
            filename = secure_filename('avatar '+str(current_user.id)+'.'+f_ext)
            f.save(os.path.join(
                app.config['UPLOAD_FOLDER'], 'avatar', filename
            ))
        if form.curriculum_vitae.data:
            f = form.curriculum_vitae.data
            f_ext = f.filename.rsplit('.',1)[1]
            filename = secure_filename('cv '+str(current_user.id)+'.'+f_ext)
            f.save(os.path.join(
                app.config['UPLOAD_FOLDER'], 'cv', filename
            ))
        db.session.commit()
        flash('You changes are save on profile')
        return redirect(url_for('profile_user', nickname=current_user.nickname))
    elif request.method == 'GET':
        form.nickname.data = current_user.nickname
        form.gender.data = current_user.gender
        form.description.data = current_user.description
        form.phone.data = current_user.phone
        form.linkedin.data = current_user.linkedin
    return render_template('edit_profile.html', form=form, title='Edit profile')


@app.route('/quit')
@login_required
def quit_job():
    if current_user.worker_id:
        c_id = current_user.worker_id.firm.id
        company = Company.query.filter_by(id=c_id).first_or_404()
        if current_user.worker_id.firm is company:
            emp = Employee.query.filter_by(user=current_user).first()
            db.session.delete(emp)
            db.session.commit()
            if company.workers.count() < 1:
                db.session.delete(company)
                db.session.commit()
            return redirect(url_for('profile_user', nickname=current_user.nickname))
        flash('You dont work in any company.')
        return redirect(url_for('profile_user', nickname=current_user.nickname))


@app.route('/companies')
def companies():
    page = request.args.get('page', 1, type=int)
    companies = Company.query.paginate(page, app.config['POST_PER_PAGE'], False)
    next_url = url_for('companies', page=companies.next_num) \
        if companies.has_next else None
    prev_url = url_for('companies', page=companies.prev_num) \
        if companies.has_prev else None
    return render_template('companies.html', companies=companies.items,
                             title='Companies', next_url=next_url, prev_url=prev_url)



@app.route('/companies/add', methods=['GET','POST'])
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


@app.route('/companies/<int:company_id>', methods=['GET','POST'])
def profile_company(company_id):
    page = request.args.get('page', 1, type=int)
    company = Company.query.filter_by(id=company_id).first_or_404()
    posts = Post.query.filter_by(
        private_company=False, company_forum=company, build_forum=None).order_by(
            Post.timestamp.desc()).paginate(page, app.config['POST_PER_PAGE'], False)
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


@app.route('/companies/<int:company_id>/employees')
@login_required
def employees(company_id):
    company = Company.query.filter_by(id=company_id).first_or_404()
    workers = company.workers
    return render_template('employee.html',workers=workers, company=company,
                             title=company.name+' employe')


@app.route('/companies/<int:company_id>/builds')
@login_required
def company_builds(company_id):
    company = Company.query.filter_by(id=company_id).first_or_404()
    builds = company.builds
    return render_template('builds.html',heading='All builds of ' + company.name,
                             builds=builds, title=company.name +' builds')


@app.route('/builds')
def builds():
    page = request.args.get('page', 1, type=int)
    builds = Build.query.paginate(page, app.config['POST_PER_PAGE'], False)
    next_url = url_for('builds', page=builds.next_num) \
        if builds.has_next else None
    prev_url = url_for('builds', page=builds.prev_num) \
        if builds.has_prev else None
    heading='All register in builds'
    return render_template('builds.html',heading='All register in builds', next_url=next_url,
                            builds=builds.items, title='All builds', prev_url=prev_url)


@app.route('/builds/add', methods=['GET','POST'])
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
        return redirect(url_for('builds'))
    return render_template('add_build.html', form=form, title='Create Build')


@app.route('/builds/<int:build_id>', methods=['GET','POST'])
def profile_build(build_id):
    page = request.args.get('page', 1, type=int)
    build = Build.query.filter_by(id=build_id).first_or_404()
    posts = Post.query.filter_by(build_forum=build, private_company=False).order_by(
        Post.timestamp.desc()).paginate(page, app.config['POST_PER_PAGE'], False)
    next_url = url_for('profile_build', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('profile_build', page=posts.prev_num) \
        if posts.has_prev else None
    heading='All register in builds'
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user, build_forum=build)
        db.session.add(post)
        db.session.commit()
        flash('You post is now avaible ')
        return redirect(url_for('profile_build',build_id=build.id))
    return render_template('profile_build.html', build=build, form=form, next_url=next_url,
                            posts=posts.items, title=build.name, prev_url=prev_url)


@app.route('/', methods=['GET','POST'])
@app.route('/blog', methods=['GET','POST'])
def blog():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(
        private_company=False, company_id=None,build_id=None).order_by(
        Post.timestamp.desc()).paginate(page, app.config['POST_PER_PAGE'], False)
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
        return redirect(url_for('blog'))
    return render_template('index.html', head_data=head, posts=posts.items, next_url=next_url,
                            form=form,  title='MicroBlog', prev_url=prev_url)


@app.route('/user/<nickname>/follow')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cant follow yourself!')
        return redirect(url_for('profile_user', nickname=nickname))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(nickname))
    return redirect(url_for('profile_user', nickname=nickname))


@app.route('/user/<nickname>/unfollow')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cant unfollow yourself!')
        return redirect(url_for('profile_user', nickname=nickname))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are  not following {}!'.format(nickname))
    return redirect(url_for('profile_user', nickname=nickname))


@app.route('/user/<nickname>/work_offer')
@login_required
def user_offers(nickname):
    user = User.query.filter_by(nickname=nickname).first_or_404()
    offers = current_user.check_offer_user(user)
    return render_template('work_offers.html', user=user, offers=offers)


@app.route('/work_offer', methods=['GET','POST'])
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
            return redirect(url_for('self_workoffer'))
    return render_template('work_offers.html', offers=offers)


@app.route('/builds/<int:build_id>/edit', methods=['GET','POST'])
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
            return redirect(url_for('builds'))
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
        return redirect(url_for('builds'))


@app.route('/reset_password', methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instruction to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset password', form=form)


@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_passwordd_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
