from forms import BuggyAtts


from consts import ATTRIBUTES, ATTRIBUTES_BOOL, ATTRIBUTES_WHOLE, NUM_VALS, DEFAULT_VALS

    
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
        form_dict[att] = 1 if form_data.get(att) == "on" else 0

    return form_dict

# turn data from a db row into a dict.
def db_data_2_dict(db_data):
    db_dict = {}

    for i, att in enumerate(ATTRIBUTES_WHOLE):
        db_dict[att] = db_data[i]

    return db_dict

def set_defaults():
    default_form = BuggyAtts(
        qty_wheels = int(DEFAULT_VALS[1]),
        power_type = DEFAULT_VALS[2],
        power_units = int(DEFAULT_VALS[3]),
        aux_power_type = DEFAULT_VALS[4],
        aux_power_units = int(DEFAULT_VALS[5]),
        hamster_booster = int(DEFAULT_VALS[6]),
        flag_color = DEFAULT_VALS[7],
        flag_pattern = DEFAULT_VALS[8],
        flag_color_secondary = DEFAULT_VALS[9],
        tyres = DEFAULT_VALS[10],
        qty_tyres = int(DEFAULT_VALS[11]),
        armour = DEFAULT_VALS[12],
        attack = DEFAULT_VALS[13],
        qty_attacks = int(DEFAULT_VALS[14]),
        fireproof = DEFAULT_VALS[15],
        insulated = DEFAULT_VALS[16],
        antibiotic = DEFAULT_VALS[17],
        banging = DEFAULT_VALS[18],
        algo = DEFAULT_VALS[19],
        name = DEFAULT_VALS[20]
    )

    return default_form