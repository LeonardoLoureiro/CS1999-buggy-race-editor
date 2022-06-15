
from crypt import methods
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
import sqlite3 as sql

from flask_login import current_user, login_required
import flask_login

from forms import DelBuggy, UserBuggies, BuggyAtts
from models import Buggy

from scripts.scrapper import *
from scripts.calcs import *
from consts import *
from scripts.form_edit import *

# this essentially makes it so this file is 'independant' and can simply just be 'imported'
# to the main file.
routes = Blueprint('routes', __name__)


from app import db


#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@routes.route('/')
@routes.route('/home')
def home():
    return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

@routes.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    form = DelBuggy()

    if request.method == 'GET':
        # if no id is given, then redirect to choose page, which will then return with an id,
        # allowing user to proceed.
        if request.args.get('buggy_id') is None:
            return redirect(url_for("routes.choose", next_step="delete"))

        buggy_id = str(request.args.get('buggy_id'))

        current_user_id = flask_login.current_user.id

        buggy_vals = Buggy.query.filter_by(id=buggy_id, user_id=current_user_id).first()

        form = DelBuggy(
            buggy_id = buggy_id
        )

        if buggy_vals is None:
            return render_template("errors/no_id.html", go_back="delete")

        return render_template(
            "delete.html", 
            buggy=buggy_vals,
            form=form
        )
    

    elif request.method == 'POST':
        # get buggy_id back
        buggy_id = form.buggy_id.data

        # get logged in user's id
        current_user_id = flask_login.current_user.id

        try:    
            # finally, search for their selected buggy and then deleted it from db table
            delete_buggy = Buggy.query.filter_by(id=buggy_id, user_id=current_user_id).delete()

            db.session.commit()
            
            msg="Buggy Deleted"

        except:
            db.session.rollback()
            msg="Buggy could not be deleted"

        return render_template("updated.html", msg=msg)


#------------------------------------------------------------
# ask user to choose which buggy, by its id, to edit/view
#------------------------------------------------------------
@routes.route('/choose', methods=['GET', 'POST'])
@login_required
def choose():
    user_buggies = UserBuggies()
    
    if request.method == 'GET':
        next_step = request.args.get('next_step')
        
        current_user_id = flask_login.current_user.id

        # get all buggies created that have current_user's account id
        created_buggies = Buggy.query.filter_by(user_id=current_user_id).all()

        # create list containing all buggy's names found in Query
        created_buggies_ops_list = [bug.name for bug in created_buggies]

        # pass all options back to the form's 'user_buggies' class obj,
        # which is a SelectField.
        user_buggies.users_buggies.choices = created_buggies_ops_list

        return render_template('choose.html',
                                form=user_buggies,
                                next_step=url_for('routes.choose', next_step=next_step ))
    
    elif request.method == 'POST':
        # get buggy id, which requires less changes to pass to other 'routes' than its entire name...#
        chosen_buggy = Buggy.query.filter_by(
            name=user_buggies.users_buggies.data, 
            user_id=flask_login.current_user.id
            ).first()

        next_step = request.args.get('next_step')
        chosen_buggy = chosen_buggy.id

        try:
            # json is only special because a function is already called json...
            # the library itself, so function had to be called something else.
            if next_step == "json":
                return redirect(url_for('routes.summary',
                                        buggy_id=chosen_buggy))
            
            else:
                next_step = "routes." + next_step
                return redirect(url_for(next_step,
                                        buggy_id=chosen_buggy))
        
        except:
            msg = "Page not found!"
            return render_template("updated.html", msg=msg)
        
        


#------------------------------------------------------------
# editing a buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form with saved data filled out
#------------------------------------------------------------
@routes.route('/edit', methods = ['POST', 'GET'])
@login_required
def edit():
    form = BuggyAtts()

    if request.method == 'GET':
        # if no 'buggy_id' is passed, i.e., this is the first time 
        # accessing page, then it should first re-route to 'choose', which then 
        # will provide the buggy_id needed to continue.
        if request.args.get('buggy_id') is None:
            return redirect(url_for("routes.choose", next_step="edit"))

        # after user has chosen a buggy to edit, everything can continue 
        # as normal, by retriving data from row and displaying it on edit page.
        buggy_id = str(request.args.get('buggy_id'))

        current_user_id = flask_login.current_user.id

        # fetch buggy's info from db
        # the reason we ask for user's ID also is because otherwise, you could enter any buggy_id
        # in the search bar and it would return the buggy's settings, even if they did not belong to user...
        buggy_id_info = Buggy.query.filter_by(
            user_id=current_user_id,
            id=buggy_id
        ).first()

        # if, whatever reason, no match is found then returns to "not found" page for buggy_id
        # this can occur if user manually changes value on top of page.
        if buggy_id_info is None:
            return render_template("errors/no_id.html", go_back="edit")

        buggy_id_info = BuggyAtts(
            id = buggy_id,
            user_id = current_user_id,
            qty_wheels = buggy_id_info.qty_wheels,
            power_type = buggy_id_info.power_type,
            power_units = buggy_id_info.power_units,
            aux_power_type = buggy_id_info.aux_power_type,
            aux_power_units = buggy_id_info.aux_power_units,
            hamster_booster = buggy_id_info.hamster_booster,
            flag_color = buggy_id_info.flag_color,
            flag_pattern = buggy_id_info.flag_pattern,
            flag_color_secondary = buggy_id_info.flag_color_secondary,
            tyres = buggy_id_info.tyres,
            qty_tyres = buggy_id_info.qty_tyres,
            armour = buggy_id_info.armour,
            attack = buggy_id_info.attack,
            qty_attacks = buggy_id_info.qty_attacks,
            fireproof = buggy_id_info.fireproof,
            insulated = buggy_id_info.insulated,
            antibiotic = buggy_id_info.antibiotic,
            banging = buggy_id_info.banging,
            algo = buggy_id_info.algo,
            cost = buggy_id_info.cost,
            mass = buggy_id_info.mass,
            name = buggy_id_info.name
        )

        return render_template("edit.html",
                                form_dest="edit",
                                form=buggy_id_info)
    
    elif request.method == 'POST':
        # get buggy's db row
        buggy_id = form.id.data

        current_user_id = flask_login.current_user.id        
      
        # calculate the price of the new buggy. 
        cost, mass = calc_cost_mass_wtf(form)

        new_vals = dict(form.data)

        # now add cost and mass key/values to dict
        new_vals['cost'] = cost
        new_vals['mass'] = mass

        # because the form dict has the 'submit' and 'csrf_token' keys,
        # we must eliminate them before passing them to 'update', otherwise SQLite will not know what
        # to do with it since db does not have those columns, and simply throw up an error.
        del new_vals['csrf_token']
        del new_vals['submit']

        current_buggy = Buggy.query.filter_by(id=buggy_id, user_id=current_user_id).update(new_vals)

        try:
            db.session.commit()
            msg = "Buggy Updated!"
        
        except Exception as e:
            msg = e
        
        return render_template("updated.html", msg = msg)
        

#------------------------------------------------------------
# creating a buggy:
#  create a new buggy, with all the default values already filled out, 
#  then post it to the DB, creating a new row.
#------------------------------------------------------------
@routes.route('/create', methods=['GET', 'POST'])
@login_required
def create_buggy():
    form = set_defaults()
    if request.method == 'GET':
        
        return render_template("create.html", form=form, form_dest="create")
    
    elif request.method == 'POST':
        # first check no buggies exist with that same name within that particular user's account
        # i.e., if that name is in the a row using user's id from 'users' table.
        current_user_id = flask_login.current_user.id

        cost, mass = calc_cost_mass_wtf(form)

        existing_buggy_name = Buggy.query.filter_by(name=form.name.data, user_id=current_user_id).first()

        if existing_buggy_name:
            flash("That buggy name already exists, please use a different one.")

            return redirect( url_for('routes.create') )

        # now assing each variable to specific class attribute so it can be saved
        buggy_class_vals = Buggy(
            qty_wheels = form.qty_wheels.data,
            power_type = form.power_type.data,
            power_units = form.power_units.data,
            aux_power_type = form.aux_power_type.data,
            aux_power_units = form.aux_power_units.data,
            hamster_booster = form.hamster_booster.data,
            flag_color = form.flag_color.data,
            flag_pattern = form.flag_pattern.data,
            flag_color_secondary = form.flag_color_secondary.data,
            tyres = form.tyres.data,
            qty_tyres = form.qty_tyres.data,
            armour = form.armour.data,
            attack = form.attack.data,
            qty_attacks = form.qty_attacks.data,
            fireproof = form.fireproof.data,
            insulated = form.insulated.data,
            antibiotic = form.antibiotic.data,
            banging = form.banging.data,
            algo = form.algo.data,
            cost = cost,
            mass = mass,
            name = form.name.data,
            user_id = current_user_id
        )

        db.session.add(buggy_class_vals)
        db.session.commit()
        msg = "Created Successfully"
    
        return render_template("updated.html", msg = msg)
    
    return render_template("create.html", form=form, form_dest="create")


#------------------------------------------------------------
# a page for displaying the buggy, 
# after user chooses which to display
#------------------------------------------------------------
@routes.route('/show')
@login_required
def show():
    if request.args.get('buggy_id') is None:
        return redirect(url_for("routes.choose", next_step="show"))

    buggy_id = request.args.get('buggy_id')
    current_user_id = flask_login.current_user.id

    buggy_vals = Buggy.query.filter_by(id=buggy_id, user_id=current_user_id).first()

    # if, whatever reason, no match is found then returns to "not found" page for buggy_id
    # this can occur is user manually changes value on top of page.
    if buggy_vals is None:
        return render_template("errors/no_id.html", go_back="show")
    
    return render_template("show.html", buggy=buggy_vals)


#------------------------------------------------------------
# INFO/Prices page
#------------------------------------------------------------
@routes.route('/info')
def info():
    tables = get_tables(SPECS_URL)

    tables = tables[1:]
    #^getting rid of 1st table, as it merely states all the different attributes 
    # and is not useful for this page

    # get info from db so user can compare against info from tables
    # con = sql.connect(DATABASE_FILE)
    # con.row_factory = sql.Row
    # cur = con.cursor()
    # cur.execute("SELECT * FROM buggies")
    # record = cur.fetchone();

    return render_template('info.html', specs=tables, buggy=DEFAULT_VALS)


#------------------------------------------------------------
# the poster page
#------------------------------------------------------------
@routes.route('/poster')
def poster():
   return render_template('poster.html')


#------------------------------------------------------------
# You probably don't need to edit this... unless you want to ;)
#
# get JSON from current record
#  This reads the buggy record from the database, turns it
#  into JSON format (excluding any empty values), and returns
#  it. There's no .html template here because it's *only* returning
#  the data, so in effect jsonify() is rendering the data.
#------------------------------------------------------------
@routes.route('/json')
@login_required
def summary():
    if request.args.get('buggy_id') is None:
        return redirect(url_for("routes.choose", next_step="json"))
    
    buggy_id = str(request.args.get('buggy_id'))

    buggy = Buggy.query.filter_by(id=buggy_id, user_id=flask_login.current_user.id).first()

    # if, whatever reason, no match is found then returns to "not found" page for buggy_id
    # this can occur is user manually changes value on top of page.
    if buggy is None:
        return render_template("errors/no_id.html", go_back="json")

    
    json_buggy = {
        "id": buggy.id,
        "qty_wheels": buggy.qty_wheels,
        "power_type": buggy.power_type,
        "power_units": buggy.power_units,
        "aux_power_type": buggy.aux_power_type,
        "aux_power_units": buggy.aux_power_units,
        "hamster_booster": buggy.hamster_booster,
        "flag_color": buggy.flag_color,
        "flag_pattern": buggy.flag_pattern,
        "flag_color_secondary": buggy.flag_color_secondary,
        "tyres": buggy.tyres,
        "qty_tyres": buggy.qty_tyres,
        "armour": buggy.armour,
        "attack": buggy.attack,
        "qty_attacks": buggy.qty_attacks,
        "fireproof": buggy.fireproof,
        "insulated": buggy.insulated,
        "antibiotic": buggy.antibiotic,
        "banging": buggy.banging,
        "algo": buggy.algo,
        "cost": buggy.cost,
        "mass": buggy.mass,
        "name": buggy.name
    }    

    return jsonify(json_buggy)



#------------------------------------------------------------
# error pages
#------------------------------------------------------------
# Now, a few routes to handle common errors:
@routes.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('errors/404.html')

# Now, a few routes to handle common errors:
@routes.errorhandler(403)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('errors/403.html')
