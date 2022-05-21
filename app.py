from crypt import methods
from flask import Flask, render_template, request, jsonify, redirect
import os
import sqlite3 as sql

import scripts.scrapper as scrapper

# app - The flask application where all the magical things are configured.
app = Flask(__name__)

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "https://rhul.buggyrace.net"

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



@app.route('/show-edit', methods=["GET", "POST"])
def show_edit():
    if request.method == "GET":
        return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)



#------------------------------------------------------------
# ask user to choose which buggy, by its id, to edit/view
#------------------------------------------------------------
@app.route('/choose', methods = ['POST', 'GET'])
def choose():
    if request.method == 'GET':
        con = sql.connect(DATABASE_FILE)
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT id FROM buggies")
        record = cur.fetchone() ;

        return render_template('choose.html', options=record)



#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------
@app.route('/edit', methods = ['POST', 'GET', 'PUT'])
def create_buggy():
    if request.method == 'GET':
        #exec_str = "SELECT * FROM buggies WHERE id IS "

        # get bool values from DB, so HTML 'knows' whether to check their respective checkboxes or not
        con = sql.connect(DATABASE_FILE)
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM buggies")
        record = cur.fetchone();

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

                for att in ATTRIBUTES:
                    form_att = request.form[att]

                    # if user left it empty, simply ignore...
                    if form_att == "":
                        continue

                    exec_str = "UPDATE buggies set %s=? WHERE id=?" % att

                    cur.execute(
                    exec_str,
                    (form_att, DEFAULT_BUGGY_ID)
                )

                # now a separate FOR loop for boolean values
                for att in ATTRIBUTES_BOOL:
                    form_att = True if request.form.get(att) == "on" else False

                    exec_str = "UPDATE buggies set %s=? WHERE id=?" % att

                    cur.execute(
                    exec_str,
                    (form_att, DEFAULT_BUGGY_ID)
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
    tables = scrapper.get_tables()

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
