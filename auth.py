from crypt import methods
from flask import Flask, Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required, login_user, logout_user, LoginManager, user_unauthorized
import flask_login
from forms import ChangeEmail, ChangePass, LoginForm, SignupForm
from flask_bcrypt import Bcrypt

try:
    from main import db
    from models import User

except ImportError:
    from . import db
    from .models import User

auth = Blueprint('auth', __name__, url_prefix="")
app = Flask(__name__)
bcrypt = Bcrypt(app)


#------------------------------------------------------------
# the login page
#------------------------------------------------------------
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # is user is already logged in, then just redirect to home
    # as not to casue any problems regarding 2 different logged in accounts.
    if current_user.is_authenticated:
        return redirect( url_for('routes.home') )

    form = LoginForm()

    if request.method == 'GET':
        return render_template('auth/login.html', form=form)
    
    elif request.method =='POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()

            if user:
                if bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user)

                    return render_template('index.html')
                
                else:
                    flash("Email/Password is incorrect.")
                    return redirect( url_for('auth.login') )

            # if user/email does not exists, then simply returns as either being incorect
            # since its the best practice to never let user know which is incorrect.
            else:
                flash("Email/Password is incorrect.")
                return redirect( url_for('auth.login') )


#-------------------------------------------------
# signup page
#-------------------------------------------------
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect( url_for('routes.home') )

    form = SignupForm()
    
    if request.method == 'GET':
        return render_template('auth/signup.html', form=form)
    
    elif request.method =='POST':
        existing_user = User.query.filter_by(email=form.email.data).first()
        
        # if email already exists, then don't create user and simply just 
        # return back to signup form, while flashing warning to user
        if existing_user:
            flash("Email already exists. Please login with existing email or user another.")
            return render_template( "auth/signup.html", form=form )

        hashed_pass = bcrypt.generate_password_hash(form.password.data)

        new_user = User(
            f_name=form.f_name.data,
            l_name=form.l_name.data,
            email=form.email.data,
            password=hashed_pass
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()

            # just login user after creating account, cause why not...
            login_user(new_user)
            msg="Your account has now been created."

            return render_template( "updated.html", msg=msg )

        except Exception as e:
            msg = "Could not create account."
            db.session.rollback()

            return render_template( "updated.html", msg=e )


#-------------------------------------------------
# log user out
#-------------------------------------------------
@auth.route('/logout')
def logout():
    logout_user()
    return redirect( url_for('auth.login') )


#-------------------------------------------------
# user's profile page
#-------------------------------------------------
@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ChangePass()

    if request.method == 'GET':

        return render_template('profile.html')


#-------------------------------------------------
# change user's email
#-------------------------------------------------
@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email():
    form = ChangeEmail()

    if request.method == 'GET':
        return render_template( 
            "change_email.html",
            form=form )
    
    elif request.method == 'POST':
        # if new emails given do not match, then do not proceed further
        if form.new_email.data != form.new_email_check.data:
            flash("New emails do not match.")

            return redirect( url_for('auth.change_email') )

        current_pass = flask_login.current_user.password

        # if current password user put in is not the same as the one in the db,
        # then do not change anything.
        if not bcrypt.check_password_hash(current_pass, form.current_password.data):
            flash("Current password is incorrect.")

            return redirect( url_for('auth.change_email') )

        # if new email is the same as the old one, then do not change anything
        # and tell user as such.
        current_email = flask_login.current_user.email
        if current_email == form.new_email.data:
            flash("New email cannot be current email.")

            return redirect( url_for('auth.change_email') )
        
        new_email_dict = { 'email': current_email }
        
        current_user_id = flask_login.current_user.id

        try:
            update_pass = User.query.filter_by(id=current_user_id).update(new_email_dict)

            db.session.commit()

            return render_template( 'updated.html', msg="Your email has been changed" )

        except Exception as e:
            return render_template( 'updated.html', msg=e )







        


#-------------------------------------------------
# change user's password
#-------------------------------------------------
@auth.route('/change_pass', methods=['GET', 'POST'])
@login_required
def change_pass():
    form = ChangePass()

    if request.method == 'GET':
        return render_template( 
            "change_pass.html",
            form=form )
    
    elif request.method == 'POST':
        if form.new_password.data != form.new_password_check.data:
            flash("New passwords do not match.")

            return redirect( url_for('auth.change_pass') )

        current_pass = flask_login.current_user.password

        # if current password user put in is not the same as the one in the db,
        # then do not change anything.
        if not bcrypt.check_password_hash(current_pass, form.current_password.data):
            flash("Current password is incorrect.")

            return redirect( url_for('auth.change_pass') )

        # if new password is the same as the old one, then do not change anything
        # and tell user as such.
        if bcrypt.check_password_hash(current_pass, form.new_password.data):
            flash("New password cannot be current password.")

            return redirect( url_for('auth.change_pass') )
        
        new_pass_hash = bcrypt.generate_password_hash( form.new_password.data )
        new_pass_dict = { 'password': new_pass_hash }
        
        current_user_id = flask_login.current_user.id

        try:
            update_pass = User.query.filter_by(id=current_user_id).update(new_pass_dict)

            db.session.commit()

            return render_template( 'updated.html', msg="Your password has been changed" )

        except Exception as e:
            return render_template( 'updated.html', msg=e )
