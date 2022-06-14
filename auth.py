from crypt import methods
from flask import Flask, Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required, login_user, logout_user, LoginManager, user_unauthorized
import flask_login
from forms import ChangeEmail, ChangePass, DelAccount, LoginForm, SignupForm
from flask_bcrypt import Bcrypt


try:
    from main import db
    from models import User, Buggy

except ImportError:
    from . import db
    from .models import User, Buggy

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
        next_page = request.args.get('next')
        
        return render_template('auth/login.html', form=form, next_page=next_page)
    
    elif request.method =='POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            
            next_page = request.args.get('next')
            
            if user:
                if bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user)

                    # if user tried to access page which needed logging in, then it'll redirect
                    # to this page back once user is logged in.
                    if next_page is not None:
                        return redirect(next_page) 
                    
                    # otherwise then simply just redirect back to home
                    return redirect( url_for('routes.home') )
                
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
@auth.route('/profile')
@login_required
def profile():

    return render_template('profile.html')


#-------------------------------------------------
# delete user's profile
#-------------------------------------------------
@auth.route('/profile/delete', methods=['GET', 'POST'])
@login_required
def delete_profile():
    form = DelAccount()

    if request.method == 'GET':
        # get all buggies under user's account to remind them buggies 

        return render_template('profile/delete.html', form=form)

    elif request.method == 'POST':
        # check password is correct
        if not bcrypt.check_password_hash(flask_login.current_user.password, form.confirm_password.data):
            flash('Password is incorrect')

            return redirect( url_for('auth.delete_profile') )

        # delete all buggies first
        current_user_id = flask_login.current_user.id 

        try:
            buggies_own_user = Buggy.query.filter_by(user_id=current_user_id).delete()
            db.session.commit()

        except:
            db.session.rollback()

            return render_template('updated.html', msg="Buggies could not be deleted, cancelling account deletion")

        # then delete their account
        try:
            user_account_del = User.query.filter_by(id=current_user_id).delete()
            db.session.commit()
        
        except:
            db.session.rollback()

            return render_template(
                'updated.html', 
                msg="Account could not be deleted, cancelling account deletion, but buggies were.")

        # log user out so nothing breaks
        logout_user()

        # then, finally, tells user everything has gone smoothly. 
        return render_template( 'updated.html', msg="Your account has now been deleted." )


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
