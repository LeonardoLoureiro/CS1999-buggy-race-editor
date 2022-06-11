
from crypt import methods
from genericpath import exists
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import sqlite3 as sql

from flask_login import login_required
import flask_login
from jsonschema import ValidationError

from forms import BuggyAtts
from models import Buggy

try:
    from scripts.scrapper import *
    from scripts.calcs import *
    from consts import *
    from scripts.form_edit import *

except ImportError:
    from .scripts.scrapper import *
    from .scripts.calcs import *
    from .consts import *
    from .scripts.form_edit import *

# this essentially makes it so this file is 'independant' and can simply just be 'imported'
# to the main file.
routes = Blueprint('routes', __name__)

try:
    from main import db

except ImportError:
    from . import db

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
    if request.method == 'GET':
        # if no id is given, then redirect to choose page, which will then return with an id,
        # allowing user to proceed.
        if request.args.get('buggy_id') is None:
            return redirect(url_for("routes.choose", next_step="delete"))

        buggy_id = str(request.args.get('buggy_id'))

        try:
            con = sql.connect(DATABASE_FILE)
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM buggies WHERE id=(?) ;", (buggy_id,))
            record = cur.fetchone() ;

        except Exception as e:
            con.rollback()

            return render_template("updated.html", msg=e)

        finally:
            con.close()        

        record = db_data_2_dict(record)

        return render_template("delete.html", buggy=record)
    
    elif request.method == 'POST':
        buggy_id = request.form['buggy_id']

        exec_str = "DELETE FROM buggies WHERE id=(?) ;"
        
        try:
            con = sql.connect(DATABASE_FILE)
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute(exec_str, (buggy_id,))
            con.commit()

            msg = "Record successfully saved"
        
        except sql.Error as error:
            con.rollback()
            msg = "error in update operation"

        finally:
            con.close()
        
        return render_template("updated.html", msg=msg)


#------------------------------------------------------------
# ask user to choose which buggy, by its id, to edit/view
#------------------------------------------------------------
@routes.route('/choose', methods=['GET', 'POST'])
@login_required
def choose():
    # form = 

    if request.method == 'GET':
        next_step = request.args.get('next_step')
        con = sql.connect(DATABASE_FILE)
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT id, name FROM buggies;")
        record = cur.fetchall() ;

        ids = []
        # since record returns all data from a row, we must sanitise it
        # before redering it.
        for r in record:
            ids.append( r ) # the first value of a row is the primary id key...

        return render_template('choose.html', 
                                options=ids, 
                                next_step=url_for('routes.choose', next_step=next_step ))
    
    elif request.method == 'POST':
        next_step = request.args.get('next_step')
        chosen_buggy = request.form['buggy_id']
        
        try:
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
    if request.method == 'GET':
        # if no 'buggy_id' is passed, i.e., this is the first time 
        # accessing page, then it should first re-route to 'choose', which then 
        # will provide the buggy_id needed to continue.
        if request.args.get('buggy_id') is None:
            return redirect(url_for("routes.choose", next_step="edit"))

        # after user has chosen a buggy to edit, everything can continue 
        # as normal, by retriving data from row and displaying it on edit page.
        buggy_id = str(request.args.get('buggy_id'))

        # get bool values from DB, so HTML 'knows' whether to check their respective checkboxes or not
        con = sql.connect(DATABASE_FILE)
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM buggies WHERE id=(?) ;", (buggy_id,))
        record = cur.fetchone() ;

        # if, whatever reason, no match is found then returns to "not found" page for buggy_id
        # this can occur is user manually changes value on top of page.
        if record is None:
            return render_template("errors/no_id.html", go_back="edit")

        return render_template("edit.html", 
                                power_type_ops=POWER_TYPE_OPS,
                                flag_patts=FLAG_PATT,
                                tyres=TYRES,
                                armor=ARMOR,
                                attacks=ATTACKS,
                                ai=AI,
                                form_dest="edit",
                                vals=record)
    
    elif request.method == 'POST':
        msg=""

        # Said VARS can now be added onto the database with their relative
        # JSON names.
        try:
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()

                buggy_id = request.form['id']


                ## update the price of the new, edited buggy
                # but first make a dict out of the form values
                # It would be simple to use 'json.dumps' here, but we need 
                # certain attributes to be integers so python can later use them
                # for their respective calculations. 
                buggy_atts = calc_total_cost(request.form)


                # # now set the new cost and mass of buggie to db...
                cost_mass_pair = calc_cost_mass(buggy_atts)
                buggy_atts['cost'] = str(cost_mass_pair[0])
                buggy_atts['mass'] = str(cost_mass_pair[1])
                
                str_atts = ', '.join(ATTRIBUTES_WHOLE[1:])
                str_ques_marks = ', '.join('?' * len(ATTRIBUTES_WHOLE[1:]))

                form_att_vals = [str(buggy_atts[a]) for a in ATTRIBUTES_WHOLE[1:]]

                exec_str = "UPDATE buggies SET (%s) = (%s) WHERE id=(?) ;" % (str_atts, str_ques_marks)

                form_att_vals += (buggy_id, )

                cur.execute(exec_str, (form_att_vals))

                con.commit()
                msg = "Record successfully saved"
        
        except Exception as ee:
            con.rollback()
            msg = "error in update operation"
            msg = ee
        
        finally:
            con.close()
        
        return render_template("updated.html", msg = msg)






#------------------------------------------------------------
# creating a buggy:
#  create a new buggy, with all the default values already filled out, 
#  then post it to the DB, creating a new row.
#------------------------------------------------------------
@routes.route('/create', methods=['GET', 'POST'])
@login_required
def create_buggy():
    form = Buggy()
    
    if request.method == 'GET':
        
        form = set_defaults()
        return render_template("create.html", form=form, form_dest="create")
    
    elif request.method == 'POST':
        if form.validate_on_submit():
            # first check no buggies exist with that same name within that particular user's account
            # i.e., if that name is in the a row using user's id from 'users' table.
            current_user_id = flask_login.current_user.id

            cost, mass = calc_cost_mass_wtf(form)


            existing_buggy_name = Buggy.query.filter_by(name=form.name.data, user_id=current_user_id).first()

            if existing_buggy_name:
                raise ValidationError("That buggy name already exists, please use a different one.")

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

    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=(?) ;", (buggy_id,))
    record = cur.fetchone() ;

    # if, whatever reason, no match is found then returns to "not found" page for buggy_id
    # this can occur is user manually changes value on top of page.
    if record is None:
        return render_template("errors/no_id.html", go_back="show")
    
    return render_template("show.html", buggy=record)


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

    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=(?) LIMIT 1", (buggy_id,))

    buggy = cur.fetchone()

    # if, whatever reason, no match is found then returns to "not found" page for buggy_id
    # this can occur is user manually changes value on top of page.
    if buggy is None:
        return render_template("errors/no_id.html", go_back="json")

    buggies = dict(zip([column[0] for column in cur.description], buggy)).items()
    return jsonify({ key: val for key, val in buggies if (val != "" and val is not None) })



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
