from flask import Flask, Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user, LoginManager, user_unauthorized
from graphviz import render
from jsonschema import ValidationError
from forms import LoginForm, SignupForm
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
                    return render_template( url_for('login') )

            else:
                return render_template( url_for('login'), already_exists=1 )

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


@auth.route('/logout')
def logout():
    logout_user()
    return redirect( url_for('auth.login') )