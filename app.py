from flask import Flask, render_template, request, jsonify
import os
import sqlite3 as sql

import scripts.scrapper as scrapper

# app - The flask application where all the magical things are configured.
app = Flask(__name__)

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "https://rhul.buggyrace.net"


#------------------------------------------------------------
# the poster page
#------------------------------------------------------------
@app.route('/poster')
def poster():
   return render_template('poster.html')

#------------------------------------------------------------
# INFO page
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
# Prices page
#------------------------------------------------------------
@app.route('/specs')
def specs():
    tables = scrapper.get_tables()

    # get info from db so user can compare against info from tables
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    record = cur.fetchone();

    return render_template('specs.html', specs=tables, buggy=record)




#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------
@app.route('/new', methods = ['POST', 'GET'])
def create_buggy():
    if request.method == 'GET':
        return render_template("buggy-form.html")
    elif request.method == 'POST':
        msg=""

        # Variable which are requested from the form and assigned as variables,
        # which can then be pushed onto the database

        ## VARS ##
        qty_wheels = request.form['qty_wheels']
        power_units = request.form['power_units']
        flag_color = request.form['flag_color']
        power_type = request.form['power_type']
        aux_power_type = request.form['aux_power_type']
        aux_power_units = request.form['aux_power_units']
        hamster_booster = request.form['hamster_booster']
        flag_pattern = request.form['flag_pattern']
        flag_color_secondary = request.form['flag_color_secondary']
        tyres = request.form['tyres']
        qty_tyres = request.form['qty_tyres']
        armour = request.form['armour']
        attack = request.form['attack']
        qty_attacks = request.form['qty_attacks']

        # boolean vals need to be treated differently due to the way HTML uses checkboxes...
        fireproof = True if request.form.get('fireproof') == "on" else False
        insulated = True if request.form.get('insulated') == "on" else False
        antibiotic = True if request.form.get('antibiotic') == "on" else False
        banging = True if request.form.get('banging') == "on" else False

        algo = request.form['algo']
        ## /VARS ##
        
        # Said VARS can now be added onto the database with their relative
        # JSON names.
        try:
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()

                # number of wheels
                cur.execute(
                    "UPDATE buggies set qty_wheels=? WHERE id=?",
                    (qty_wheels, DEFAULT_BUGGY_ID)
                )

                # power units
                cur.execute(
                    "UPDATE buggies set qty_wheels=? WHERE id=?",
                    (power_units, DEFAULT_BUGGY_ID)
                )

                # colour of the buggy's flag
                cur.execute(
                    "UPDATE buggies set flag_color=? WHERE id=?",
                    (flag_color, DEFAULT_BUGGY_ID)
                )
                
                # Power Type
                cur.execute(
                    "UPDATE buggies set power_type=? WHERE id=?",
                    (power_type, DEFAULT_BUGGY_ID)
                )

                # Aux Power Type
                cur.execute(
                    "UPDATE buggies set aux_power_type=? WHERE id=?",
                    (aux_power_type, DEFAULT_BUGGY_ID)
                )

                # Aux Power Units
                cur.execute(
                    "UPDATE buggies set aux_power_units=? WHERE id=?",
                    (aux_power_units, DEFAULT_BUGGY_ID)
                )

                # Hamster Booster
                cur.execute(
                    "UPDATE buggies set hamster_booster=? WHERE id=?",
                    (hamster_booster, DEFAULT_BUGGY_ID)
                )

                # Flag Pattern
                cur.execute(
                    "UPDATE buggies set flag_pattern=? WHERE id=?",
                    (flag_pattern, DEFAULT_BUGGY_ID)
                )

                # Flag Color Secondary
                cur.execute(
                    "UPDATE buggies set flag_color_secondary=? WHERE id=?",
                    (flag_color_secondary, DEFAULT_BUGGY_ID)
                )

                # Tyres
                cur.execute(
                    "UPDATE buggies set tyres=? WHERE id=?",
                    (tyres, DEFAULT_BUGGY_ID)
                )

                # Number of Tyres
                cur.execute(
                    "UPDATE buggies set qty_tyres=? WHERE id=?",
                    (qty_tyres, DEFAULT_BUGGY_ID)
                )

                # Armour
                cur.execute(
                    "UPDATE buggies set armour=? WHERE id=?",
                    (armour, DEFAULT_BUGGY_ID)
                )

                # Attack
                cur.execute(
                    "UPDATE buggies set attack=? WHERE id=?",
                    (attack, DEFAULT_BUGGY_ID)
                )

                # Number of Attacks
                cur.execute(
                    "UPDATE buggies set qty_attacks=? WHERE id=?",
                    (qty_attacks, DEFAULT_BUGGY_ID)
                )

                # Fireproof
                cur.execute(
                    "UPDATE buggies set fireproof=? WHERE id=?",
                    (fireproof, DEFAULT_BUGGY_ID)
                )

                # Insulated
                cur.execute(
                    "UPDATE buggies set insulated=? WHERE id=?",
                    (insulated, DEFAULT_BUGGY_ID)
                )

                # Antibiotic
                cur.execute(
                    "UPDATE buggies set antibiotic=? WHERE id=?",
                    (antibiotic, DEFAULT_BUGGY_ID)
                )

                # Banging
                cur.execute(
                    "UPDATE buggies set banging=? WHERE id=?",
                    (banging, DEFAULT_BUGGY_ID)
                )

                # Algo
                cur.execute(
                    "UPDATE buggies set algo=? WHERE id=?",
                    (algo, DEFAULT_BUGGY_ID)
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
    return render_template("buggy.html", buggy = record)

#------------------------------------------------------------
# a placeholder page for editing the buggy: you'll need
# to change this when you tackle task 2-EDIT
#------------------------------------------------------------
@app.route('/edit')
def edit_buggy():
    return render_template("buggy-form.html")

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
