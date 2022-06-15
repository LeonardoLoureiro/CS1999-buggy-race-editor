from app import db

from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy

    email = db.Column(db.String(60), nullable=False, unique=True)
    
    password = db.Column(db.String(80), nullable=False)
    
    f_name = db.Column(db.String(40), nullable=False) #first name
    l_name = db.Column(db.String(40), nullable=False) #last name


class Buggy(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy

    qty_wheels = db.Column( db.Integer, nullable=False )
    power_type = db.Column( db.String(10), nullable=False )
    power_units = db.Column( db.Integer, nullable=False )
    aux_power_type = db.Column( db.String(10), nullable=False )
    aux_power_units = db.Column( db.Integer, nullable=False )
    hamster_booster = db.Column( db.Integer, nullable=False )
    flag_color = db.Column( db.String(8), nullable=False )
    flag_pattern = db.Column( db.String(10), nullable=False )
    flag_color_secondary = db.Column( db.String(8), nullable=False )
    tyres = db.Column( db.String(10), nullable=False )
    qty_tyres = db.Column( db.Integer, nullable=False )
    armour = db.Column( db.String(12), nullable=False )
    attack = db.Column( db.String(10), nullable=False )
    qty_attacks = db.Column( db.Integer, nullable=False )
    algo = db.Column( db.String(10), nullable=False )

    fireproof = db.Column( db.Boolean, nullable=False )
    insulated = db.Column( db.Boolean, nullable=False )
    antibiotic = db.Column( db.Boolean, nullable=False )
    banging = db.Column( db.Boolean, nullable=False )
	
    cost = db.Column( db.Float, nullable=False )
    mass = db.Column( db.Float, nullable=False )
    name = db.Column( db.String(35), nullable=False )

    user_id = db.Column( db.Integer, nullable=False ) # so we know whose buggy is whose