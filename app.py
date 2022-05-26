from crypt import methods
from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sqlite3 as sql

from matplotlib.pyplot import table

from scripts.scrapper import *
from scripts.calc_costs import *

# app - The flask application where all the magical things are configured.
app = Flask(__name__)

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "https://rhul.buggyrace.net"

SPECS_URL = "https://rhul.buggyrace.net/specs/"

ATTRIBUTES = [
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
	"algo"
]




# since bool attributes have to be treated differently, 
# best to have them in a separate list for easier management/correction
# when pushing to DB.
ATTRIBUTES_BOOL = [
    "fireproof",
	"insulated",
	"antibiotic",
	"banging"
]


# Options given to users as a list for easier way to code IF code block in HTML edit page.
# Since there are more than 1 multiple-choice attributes, it's best to implement it this 
# instead of hardcoding, as this way if, in the future, there are more options to be added,
# then this makes thins much easer. Plus, doing this dynamicall instead of hard-coding,
# makes things less likely to be coded wrong.
POWER_TYPE_OPS = [
    "none",
	"petrol",
	"fusion",
	"steam",
	"bio",
	"electric",
	"rocket",
	"hamster",
	"thermo",
	"solar",
	"wind"
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




#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

"""
@app.route('/exp/<val>/<val2>', methods = ['POST', 'GET'])
def exp_val(val, val2=None):
    if request.method == 'GET':
        return "Val is " + str(val) #+ " and " + val2

@app.route('/exp', methods = ['POST', 'GET'])
def exp():
    if request.method == 'GET':
        return "Val is NULL"
"""

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
        
        else:
            return "Not yet..."
        
        



"""
@app.route('/choose', methods = ['POST', 'GET'])
def choose(next_step=None):
"""





#------------------------------------------------------------
# editing a buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form with saved data filled out
#------------------------------------------------------------
@app.route('/edit', methods = ['POST', 'GET'])
def edit_buggy():
    if request.method == 'GET':
        
        # if no buggy_id is passed, i.e., this is the first time 
        # accessing page, first re-route to 'choose', which then 
        # will proved the buggy_id needed to continue.
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
                                vals=record)
    

    elif request.method == 'POST':
        msg=""

        # Said VARS can now be added onto the database with their relative
        # JSON names.
        try:
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()

                buggy_id = request.form['id']

                for att in ATTRIBUTES:
                    form_att = request.form[att]

                    # if user left it empty, simply ignore...
                    if form_att == "":
                        continue

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


@app.route('/create', methods = ['POST', 'GET'])
def create_buggy():
    if request.method == 'GET':

        return render_template("create.html", 
            power_type_ops=POWER_TYPE_OPS,
            flag_patts=FLAG_PATT,
            tyres=TYRES,
            armor=ARMOR,
            attacks=ATTACKS,
            ai=AI)
    
    elif request.method == 'POST':
        msg = ""

        try:
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()
                
                att_val_list = []
                att_name_list = []
                num_vals = ["qty_wheels",
                            "power_units",
                            "aux_power_units",
                            "hamster_booster",
                            "qty_tyres",
                            "qty_attacks"]

                for att in ATTRIBUTES[:-1]:
                    att_name_list.append(att)
                    if att in num_vals:
                        att_val_list.append( int( request.form[att] ) )
                        continue

                    att_val_list.append( request.form[att] )
                
                for att in ATTRIBUTES_BOOL:
                    att_name_list.append(att)
                    val = True if request.form.get(att) == "on" else False
                    att_val_list.append( val )

                att_name_list.append('algo')
                att_val_list.append( request.form['algo'] )

                exec_str_list = ', '.join('?' * len(att_val_list))
                exec_str_att_names = ', '.join( att_name_list )
                exec_str = "INSERT INTO buggies (%s) VALUES (%s);" % (exec_str_att_names, exec_str_list)
                
                cur.execute(exec_str, att_val_list)

                con.commit()

                msg = "Record successfully saved"
        
        except:
            con.rollback()
            msg = "error in update operation"
        
        finally:
            con.close()
            
        
        return render_template("updated.html", msg = msg)



#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    record = cur.fetchone(); 
    
    return render_template("buggy.html", buggy=record)


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
# a placeholder page for editing the buggy: you'll need
# to change this when you tackle task 2-EDIT
#------------------------------------------------------------
# @app.route('/edit')
# def edit_buggy():
#     return render_template("buggy-form.html")

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
