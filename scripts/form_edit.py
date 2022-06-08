from consts import ATTRIBUTES, ATTRIBUTES_BOOL, ATTRIBUTES_WHOLE

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