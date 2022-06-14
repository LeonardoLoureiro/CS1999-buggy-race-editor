from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from datetime import timedelta

# First, RUN:
#   - export FLASK_APP=main.py
#
# Then you can simply run flask normally:
#   - flask run

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

try:
    from models import User

except ImportError:
    from .models import User


def create_app():
    app = Flask(__name__)
    csrf = CSRFProtect(app)

    app.config['SECRET_KEY'] = "\x0c\xc3\xfe\xc5L\xcc\x8dMLt\xef\x85\xe4:c.\xb8\xde\xcc\xaf7M\x04:"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['DEBUG_MODE'] = True

    # this will make sure users that login don't stay logged in forever
    app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=15)

    db.init_app(app)
    csrf.init_app(app)

    # blueprint for auth routes in our app
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from routes import routes as main_blueprint
    app.register_blueprint(main_blueprint)

    ##  WARNING ##
    # This MUST come after `db`, the code above.
    # Otherwise, a circular import is created, causing many, many problems!
    ## /WARNING ##
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    return app