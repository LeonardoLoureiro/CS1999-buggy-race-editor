import sqlite3

DATABASE_FILE = "database.db"

# important:
#-------------------------------------------------------------
# This script initialises your SQLite database for you, just
# to get you started... there are better ways to express the
# data you're going to need... especially outside SQLite.
# For example... maybe flag_pattern should be an ENUM (which
# is available in most other SQL databases), or a foreign key
# to a pattern table?
#
# Also... the name of the database (here, in SQLite, it's a
# filename) appears in more than one place in the project.
# That doesn't feel right, does it?
#-------------------------------------------------------------

connection = sqlite3.connect(DATABASE_FILE)
print("- Opened database successfully in file \"{}\"".format(DATABASE_FILE))

# using Python's triple-quote for multi-line strings:

connection.execute("""

  CREATE TABLE IF NOT EXISTS buggies (
    id                    INTEGER PRIMARY KEY,
    qty_wheels            INTEGER DEFAULT 4,
    power_type            VARCHAR(10) DEFAULT 'petrol',
    power_units           INTEGER DEFAULT 1,
    aux_power_type        VARCHAR(10) DEFAULT 'none',
    aux_power_units       INTEGER DEFAULT 0,
    hamster_booster       INTEGER DEFAULT 0,
    flag_color            VARCHAR(8) DEFAULT '#ffffff',
    flag_pattern          VARCHAR(10) DEFAULT 'plain',
    flag_color_secondary  VARCHAR(8) DEFAULT '#000000',
    tyres                 VARCHAR(10) DEFAULT 'knobbly',
    qty_tyres             INTEGER DEFAULT 4,
    armour                VARCHAR(12) DEFAULT 'none',
    attack                VARCHAR(10) DEFAULT 'none',
    qty_attacks           INTEGER DEFAULT 0,
    fireproof             BOOLEAN DEFAULT FALSE,
    insulated             BOOLEAN DEFAULT FALSE,
    antibiotic            BOOLEAN DEFAULT FALSE,
    banging               BOOLEAN DEFAULT FALSE,
    algo                  VARCHAR(10) DEFAULT 'steady',
    cost                  FLOAT DEFAULT 64.00,
    mass                  FLOAT DEFAULT 82.00,
    name                  VARCHAR(35) DEFAULT 'car'
  )
""")

print("- Table \"buggies\" exists OK")

cursor = connection.cursor()

cursor.execute("SELECT * FROM buggies LIMIT 1")
rows = cursor.fetchall()
if len(rows) == 0:
  cursor.execute("INSERT INTO buggies (qty_wheels) VALUES (4)")
  connection.commit()
  print("- Added one 4-wheeled buggy")
else:
  print("- Found a buggy in the database, nice")

print("- OK, your database is ready")

connection.close()
