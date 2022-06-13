"""Sign-up & log-in forms."""
import email
from secrets import choice
from flask_wtf import FlaskForm
from jsonschema import ValidationError
from requests import session
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, BooleanField, HiddenField
# from wtforms.fields import ColorInput
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length
)


try:
    from consts import POWER_TYPE_OPS, FLAG_PATT, TYRES, ARMOR, ATTACKS, AI

except ImportError:
    from .consts import POWER_TYPE_OPS, FLAG_PATT, TYRES, ARMOR, ATTACKS, AI

class SignupForm(FlaskForm):
    """User Sign-up Form."""
    f_name = StringField(
        'F_Name',
        validators=[DataRequired(), Length(min=3, max=40)],
        render_kw={"placeholder": "First Name"}
    )

    l_name = StringField(
        'L_Name',
        validators=[DataRequired(), Length(min=3, max=40)],
        render_kw={"placeholder": "Last Name"}
    )

    email = StringField(
        'Email',
        validators=[
            Length(min=6),
            Email(message='Enter a valid email.'),
            Length(min=3, max=60),
            DataRequired()
        ],
        render_kw={"placeholder": "Email"}
    )
    
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6, message='Select a stronger password.')
        ],
        render_kw={"placeholder": "Password"}
    )
    
    confirm_pass = PasswordField(
        'Confirm Your Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ],
        render_kw={"placeholder": "Re-enter password"}
    )
    
    submit = SubmitField('Signup')

class LoginForm(FlaskForm):
    """User Log-in Form."""
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(message='Enter a valid email.')
        ],
        render_kw={"placeholder": "Email"}
    )
    password = PasswordField(
        'Password', 
        validators=[DataRequired()],
        render_kw={"placeholder": "Password"}
    )
    submit = SubmitField('Log In')

class BuggyAtts(FlaskForm):
    """Buggy attributes Form."""

    id = HiddenField(
        'id'
    )

    qty_wheels = IntegerField(
        'qty_wheels',
        validators=[DataRequired(), Length(min=4)]
	)

    power_type = SelectField(
        'power_type',
        validators=[DataRequired()],
        choices=POWER_TYPE_OPS
	)

    power_units = IntegerField(
        'power_units',
        validators=[DataRequired(), Length(min=0)]
	)

    aux_power_type = SelectField(
        'aux_power_type',
        validators=[DataRequired()],
        choices=POWER_TYPE_OPS
	)

    aux_power_units = IntegerField(
        'aux_power_units',
        validators=[DataRequired(), Length(min=0)]
	)

    hamster_booster = IntegerField(
        'hamster_booster',
        validators=[DataRequired(), Length(min=0)]
	)

    flag_color = StringField(
        'flag_color',
        validators=[DataRequired()]
	)
    
    flag_pattern = SelectField(
        'flag_pattern',
        validators=[DataRequired()],
        choices=FLAG_PATT
	)
    
    flag_color_secondary = StringField(
        'flag_color_secondary',
        validators=[DataRequired()]
	)
    
    tyres = SelectField(
        'tyres',
        validators=[DataRequired()],
        choices=TYRES
	)
    
    qty_tyres = IntegerField(
        'qty_tyres',
        validators=[DataRequired(), Length(min=4)]
	)
    
    armour = SelectField(
        'armour',
        validators=[DataRequired()],
        choices=ARMOR
	)
    
    attack = SelectField(
        'attack',
        validators=[DataRequired()],
        choices=ATTACKS
	)
    
    qty_attacks = IntegerField(
        'qty_attacks',
        validators=[DataRequired(), Length(min=0)]
	)
    
    fireproof = BooleanField(
        'fireproof',
	)
    
    insulated = BooleanField(
        'insulated',
	)
    
    antibiotic = BooleanField(
        'antibiotic',
	)
    
    banging = BooleanField(
        'banging',
	)   
    
    algo = SelectField(
        'algo',
        validators=[DataRequired()],
        choices=AI
	)
    
    name = StringField(
        'name',
        validators=[DataRequired(), Length(min=3, max=34)]
    )

    submit = SubmitField('Submit')

class UserBuggies(FlaskForm):
    """Buggies under specific user's account"""

    # since we cannot dynamically assign them here,
    # we must create the obj first, then assign the options later.
    users_buggies = SelectField(
        'Buggies', 
        choices=[]
    )
    
    submit = SubmitField('Choose')


class DelBuggy(FlaskForm):
    """Form used specifically for deleting a buggy"""
    buggy_id = HiddenField('buggy_id')

    submit = SubmitField('Delete')

class ChangePass(FlaskForm):
    """Form for changing a user's password"""

    # first user must enter the current set password.
    # This is best practice in the real world in case someone gets
    # ahold of their device while logged in and cannot change password easily.
    current_password = PasswordField(
        'Password', 
        validators=[DataRequired()],
        render_kw={"placeholder": "Password"}
    )

    new_password = PasswordField(
        'Password', 
        validators=[DataRequired()],
        render_kw={"placeholder": "Please Password"}
    )

    new_password_check = PasswordField(
        'Password', 
        validators=[DataRequired()],
        render_kw={"placeholder": "Please Password"}
    )

    submit = SubmitField('Change Password')

class ChangeEmail(FlaskForm):
    """Form for changing a user's password"""

    # first user must enter the current set password.
    # This is best practice in the real world in case someone gets
    # ahold of their device while logged in and cannot change password easily.
    current_password = PasswordField(
        'Password', 
        validators=[DataRequired()],
        render_kw={"placeholder": "Password"}
    )

    new_email = StringField(
        'email',
        validators=[
            Length(min=6),
            Email(message='Enter a valid email.'),
            Length(min=3, max=60),
            DataRequired()
        ],
        render_kw={"placeholder": "Email"}
    )

    new_email_check = StringField(
        'email_check',
        validators=[
            Length(min=6),
            Email(message='Enter a valid email.'),
            Length(min=3, max=60),
            DataRequired()
        ],
        render_kw={"placeholder": "Re-enter Email"}
    )

    submit = SubmitField('Change Email')