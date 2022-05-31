from crypt import methods
from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sqlite3 as sql

from scripts.scrapper import *
from scripts.calcs import *

# app - The flask application where all the magical things are configured.
app = Flask(__name__)

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "https://rhul.buggyrace.net"

SPECS_URL = "https://rhul.buggyrace.net/specs/"


# just a list of every attribute aggregated into one big list
ATTRIBUTES_WHOLE = [
    "id",
    "qty_wheels",
	"power_type",
    "power_units",
	"aux_power_type",
	"aux_power_units",
	"hamster_booster",
    "flag_color",
	"flag_pattern",
	"flag_color_secondary",
	"tyres",
	"qty_tyres",
	"armour",
	"attack",
	"qty_attacks",
    "fireproof",
	"insulated",
	"antibiotic",
	"banging",
	"algo",
	"cost",
	"mass"
]

# List of all attributes a buggy has, this way, no hard coding it again is needed
# and rather it can be iterated over. All attributed except those which are of bool
# nature.
ATTRIBUTES = ATTRIBUTES_WHOLE[1:15] + ATTRIBUTES_WHOLE[-3:-2]



# since bool attributes have to be treated differently, 
# best to have them in a separate list for easier management/correction
# when pushing to DB.
ATTRIBUTES_BOOL = ATTRIBUTES_WHOLE[15:19]

NUM_VALS = ["qty_wheels",
            "power_units",
            "aux_power_units",
            "hamster_booster",
            "qty_tyres",
            "qty_attacks"]

# Options given to users as a list for easier way to code IF code block in HTML edit page.
# Since there are more than 1 multiple-choice attributes, it's best to implement it this 
# instead of hardcoding, as this way if, in the future, there are more options to be added,
# then this makes thins much easer. Plus, doing this dynamicall instead of hard-coding,
# makes things less likely to be coded wrong.
POWER_TYPE_OPS = [
	"petrol",
	"fusion",
	"steam",
	"bio",
	"electric",
	"rocket",
	"hamster",
	"thermo",
	"solar",
	"wind",
    "none"
]

FLAG_PATT = [
	"plain",
	"vstripe",
	"hstripe",
	"dstripe",
	"checker",
	"spot"
]

TYRES = [
	"knobbly",
	"slick",
	"steelband",
	"reactive",
	"maglev"
]

ARMOR = [
	"none",
	"wood",
	"aluminium",
	"thinsteel",
	"thicksteel",
	"titanium"
]

ATTACKS = [
	"none",
	"spike",
	"flame",
	"charge",
	"biohazard",
]

AI = [
	"defensive",
	"steady",
	"offensive",
	"titfortat",
	"random"
]

# list of all default values, here so loading a single table to be edited could be used accross
# multiple page, that way any changes there would occur on all page using such (proccess) table.
DEFAULT_VALS = [
    "NULL", #this is supposed to be the id of a buggy, but since this will be used for creating, it won't be used.
    "4",
    "petrol",
    "1",
    "none",
    "0",
    "0",
    "#ffffff",
    "plain",
    "#000000",
    "knobbly",
    "4",
    "none",
    "none",
    "0",
    0,
    0,
    0,
    0,
    "steady"
]



#------------------------------------------------------------
# Custom function
#------------------------------------------------------------
# take data from form of a page, and turn it into a dict,
# with each attributes correct data type (e.g., number of wheel should be integers.)
def make_dict_form(form_data):
    form_dict = {}

    for att in ATTRIBUTES:
        if att in NUM_VALS:
            form_dict[att] = int(form_data[att])
            continue

        form_dict[att] = form_data[att]
    
    for att in ATTRIBUTES_BOOL:
        form_dict[att] = True if form_data.get(att) == "on" else False

    return form_dict

# turn data from a db row into a dict.
def db_data_2_dict(db_data):
    db_dict = {}

    for i, att in enumerate(ATTRIBUTES_WHOLE):
        db_dict[att] = db_data[i]

    return db_dict
#------------------------------------------------------------
# /Custom function
#------------------------------------------------------------




#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'GET':
        # if no id is given, then redirect to choose page, which will then return with an id,
        # allowing user to proceed.
        if request.args.get('buggy_id') is None:
            return redirect(url_for("choose", next_step="delete"))

        buggy_id = str(request.args.get('buggy_id'))

        try:
            con = sql.connect(DATABASE_FILE)
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM buggies WHERE id=?;", buggy_id)
            record = cur.fetchone() ;

        except:
            con.rollback()
            msg = "error in retrieving operation"

            return render_template("update.html", msg=msg)

        finally:
            con.close()        

        record = db_data_2_dict(record)

        return render_template("delete.html", buggy=record)
    
    elif request.method == 'POST':
        buggy_id = request.form['buggy_id']

        exec_str = "DELETE FROM buggies WHERE id=?;"
        
        try:
            con = sql.connect(DATABASE_FILE)
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute(exec_str, buggy_id)
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
@app.route('/choose', methods=['GET', 'POST'])
def choose():
    if request.method == 'GET':
        next_step = request.args.get('next_step')
        con = sql.connect(DATABASE_FILE)
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT id FROM buggies;")
        record = cur.fetchall() ;

        ids = []
        # since record returns all data from a row, we must sanitise it
        # before redering it.
        for r in record:
            ids.append( r[0] ) # the first value of a row is the primary id key...

        return render_template('choose.html', 
                                options=ids, 
                                next_step=url_for( 'choose', next_step=next_step ))
    
    elif request.method == 'POST':
        next_step = request.args.get('next_step')
        chosen_buggy = request.form['buggy_id']

        if next_step == "edit":
            return redirect(url_for('edit_buggy',
                                    buggy_id=chosen_buggy))
        
        elif next_step == "show_buggy":
            return redirect(url_for('show_buggy',
                                    buggy_id=chosen_buggy))
        
        elif next_step == "delete":
            return redirect(url_for('delete',
                                    buggy_id=chosen_buggy))


#------------------------------------------------------------
# editing a buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form with saved data filled out
#------------------------------------------------------------
@app.route('/edit', methods = ['POST', 'GET'])
def edit_buggy():
    if request.method == 'GET':
        # if no 'buggy_id' is passed, i.e., this is the first time 
        # accessing page, then it should first re-route to 'choose', which then 
        # will provide the buggy_id needed to continue.
        if request.args.get('buggy_id') is None:
            return redirect(url_for("choose", next_step="edit"))

        # after user has chosen a buggy to edit, everything can continue 
        # as normal, by retriving data from row and displaying it on edit page.
        buggy_id = str(request.args.get('buggy_id'))

        # get bool values from DB, so HTML 'knows' whether to check their respective checkboxes or not
        con = sql.connect(DATABASE_FILE)
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM buggies WHERE id=?", buggy_id)
        record = cur.fetchone() ;

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
                buggy_atts = make_dict_form(request.form)


                # now set the new cost and mass of buggie to db...
                cost_mass_pair = calc_cost_mass(buggy_atts)
                exec_str_cost = "UPDATE buggies set cost=? WHERE id=?"
                cur.execute(
                    exec_str_cost,
                    (str(cost_mass_pair[0]), buggy_id)
                )

                exec_str_mass = "UPDATE buggies set mass=? WHERE id=?"
                cur.execute(
                    exec_str_mass,
                    (str(cost_mass_pair[1]), buggy_id)
                )


                for att in ATTRIBUTES:
                    form_att = request.form[att]

                    exec_str = "UPDATE buggies set %s=? WHERE id=?" % att

                    cur.execute(
                    exec_str,
                    (form_att, buggy_id)
                )

                # now a separate FOR loop for boolean values
                for att in ATTRIBUTES_BOOL:
                    form_att = True if request.form.get(att) == "on" else False

                    exec_str = "UPDATE buggies set %s=? WHERE id=?" % att

                    cur.execute(
                    exec_str,
                    (form_att, buggy_id)
                )


                con.commit()
                msg = "Record successfully saved"
        
        except:
            con.rollback()
            msg = "error in update operation"
        
        finally:
            con.close()
        
        return render_template("updated.html", msg = msg)


#------------------------------------------------------------
# creating a buggy:
#  create a new buggy, with all the default values already filled out, 
#  then post it to the DB, creating a new row.
#------------------------------------------------------------
@app.route('/create', methods = ['POST', 'GET'])
def create_buggy():
    if request.method == 'GET':

        return render_template("create.html", 
            power_type_ops=POWER_TYPE_OPS,
            flag_patts=FLAG_PATT,
            tyres=TYRES,
            armor=ARMOR,
            attacks=ATTACKS,
            ai=AI,
            vals=DEFAULT_VALS,
            form_dest="create")
    
    elif request.method == 'POST':
        msg = ""

        try:
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()

                buggy_atts = make_dict_form(request.form) 
                # ^this will be used to calculate cost and mass of the buggy
                # but first the data must be 'turned' into their correct
                # respective data types for their calculations.

                # now calculate them
                cost_mass_pair = calc_cost_mass(buggy_atts)

                # must add "cost" and "mass" to the dict which will be added to db.
                buggy_atts['cost'] = cost_mass_pair[0]
                buggy_atts['mass'] = cost_mass_pair[1]

                exec_str_list = ', '.join('?' * len(buggy_atts))
                exec_str_att_names = ', '.join( buggy_atts.keys() )

                exec_str = "INSERT INTO buggies (%s) VALUES (%s);" % (exec_str_att_names, exec_str_list)

                val_list_as_str = [str(a) for a in buggy_atts.values()]
                # ^must turn all vals into strings, since SQL does NOT like anything else when assigning variables
                #  to be entered into a db.
                
                cur.execute(exec_str, val_list_as_str)

                con.commit()

                msg = "Record successfully saved"
        
        except:
            con.rollback()
            msg = "error in update operation"
        
        finally:
            con.close()
            
        
        return render_template("updated.html", msg = msg)


#------------------------------------------------------------
# a page for displaying the buggy, 
# after user chooses which to display
#------------------------------------------------------------
@app.route('/show')
def show_buggy():
    if request.args.get('buggy_id') is None:
        return redirect(url_for("choose", next_step="show_buggy"))

    buggy_id = request.args.get('buggy_id')

    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=?", buggy_id)
    record = cur.fetchone(); 
    
    return render_template("show.html", buggy=record)


#------------------------------------------------------------
# INFO/Prices page
#------------------------------------------------------------
@app.route('/info')
def info():
    tables = get_tables(SPECS_URL)

    tables = tables[1:]
    #^getting rid of 1st table, as it merely states all the different attributes 
    # and is not useful for this page

    # get info from db so user can compare against info from tables
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    record = cur.fetchone();

    return render_template('info.html', specs=tables, buggy=record)


#------------------------------------------------------------
# the poster page
#------------------------------------------------------------
@app.route('/poster')
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
@app.route('/json')
def summary():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))

    buggies = dict(zip([column[0] for column in cur.description], cur.fetchone())).items() 
    return jsonify({ key: val for key, val in buggies if (val != "" and val is not None) })


# You shouldn't need to add anything below this!
if __name__ == '__main__':
    alloc_port = os.environ['CS1999_PORT']
    app.run(debug=True, host="0.0.0.0", port=alloc_port)
