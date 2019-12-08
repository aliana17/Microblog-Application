from app import app
from flask import Flask,render_template, request,redirect,url_for,session,flash
import os
from datetime import datetime
from app.login_form import LoginForm, RegistrationForm, EditProfileForm
from app import db
from flask_login import current_user,login_user,logout_user,login_required
from app.models import User,Post
from app import login_manager

@app.route('/')
def home():
    return render_template("blogs.html")


@app.route('/user/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('blogger',username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/welcome')
def about():
    return 'Congratulations!! you have posted your first blog'

@app.route('/contact')
def contact():
    return 'Contact us at agarwalanchal72@gmail.com'

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register', form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
        user= User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('blogger',username=current_user.username))
    return render_template('login.html',title='Sign In', form=form)
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/user/<username>')
@login_required
def blogger(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts=[
        {'author':user, 'body':'Test post #1'},
        {'author':user, 'body':'Test post #1'}
    ]
    return render_template('write_blogs.html',user=user,posts=posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}

if __name__ == "__main__":
    app.run(debug=True)
