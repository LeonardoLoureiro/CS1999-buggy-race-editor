# data in JSON: https://rhul.buggyrace.net/specs/data/types.json

import json
import urllib.request

JSON_DATA_URL = "https://rhul.buggyrace.net/specs/data/types.json"

USER_CHOICES = {
    "algo": "steady", 
    "armour": "wood", 
    "attack": "none", 
    "aux_power_type": "none", 
    "aux_power_units": 0, 
    "flag_color": "#ffffff", 
    "flag_color_secondary": "#000000", 
    "flag_pattern": "plain", 
    "hamster_booster": 0,  
    "power_type": "petrol", 
    "power_units": 1, 
    "qty_attacks": 0, 
    "qty_tyres": 4, 
    "qty_wheels": 4, 
    "tyres": "knobbly",
    "antibiotic": 1,
    "banging": 0, 
    "fireproof": 0, 
    "insulated": 1
}

# algo and flag colours/patterns are not counted 
# since they do not cost anything to begin with...
BOOL    = ["antibiotic", "banging", "fireproof", "insulated"]
# NORMAL  = ["tyres", "attack", "hamster_booster", "aux_power_type", "power_type"]

"""
    cost_of_tyres = number of wheels x type of tyres
    cost_of_attack = number of attacks x qty_attacks
    cost_of_hamsters = 5 x hamster_booster
    cost_of_aux_power_type = aux_power_type x aux_power_units
    cost_of_powers = power_type x power_units
"""

# 2 separate mechanisms:
#   - normal atts, which can be calculated streamlined
#   - bool vals which have to be done separately
def calc_total_cost(user_choices):
    total_cost = 0

    # retrive json of all atts costs
    # then turn it into JSON format for easier use.
    url_html = urllib.request.urlopen(JSON_DATA_URL)
    data = url_html.read()
    att_costs = json.loads(data.decode('utf-8'))

    # first calc bool vals as they're straightforward to do
    for bool_att in BOOL:
        user_bool_choice = user_choices[bool_att]

        if user_bool_choice:
            cost = att_costs['special'][bool_att]['cost']
        
        else:
            cost = "0"
        
        total_cost += int(cost)


    # calc tyres
    user_num_tyres = user_choices['qty_tyres']
    user_tyre_type = user_choices['tyres']
    tyre_type_cost = att_costs['tyres'][user_tyre_type]['cost']
    total_cost += user_num_tyres * int(tyre_type_cost)

    # calc armour, since you can only have 1 type we just add to total
    # HOWEVER, the cost changes when the num of wheels in a buggy
    # is >4. Which each wheel above 4, 10% of cost is added per wheel.
    user_armour = user_choices['armour']
    user_num_wheels = int(user_choices['qty_wheels'])

    # if num of wheel >4, percentage addition is made but if 4, then it's simply
    # final calculation multipled by 1, so nothing changes unless it's >4. 
    remainder_wheels = user_num_wheels - 4
    remainder_wheels_cost = (remainder_wheels/10) +1 
    #^convert to % form, since each wheel is 10%, only divide by 10.
    # adding 1 so percentage is added on top of original value, instead of simply calculating its percentage.

    armour_cost = att_costs['armour'][user_armour]['cost']
    user_armour_cost = int(armour_cost) * remainder_wheels_cost
    total_cost += user_armour_cost

    # calc attack
    user_num_attacks = user_choices['qty_attacks']
    user_attack = user_choices['attack']
    cost_attack = att_costs['attack'][user_attack]['cost']
    total_cost += user_num_attacks * int(cost_attack)

    # calc hasmter boosters
    user_num_hams = user_choices['hamster_booster']
    cost_of_hams = att_costs['special']['hamster_booster']['cost']
    total_cost += user_num_hams * int(cost_of_hams)
    

    ## because 'none' is not included in the 'power_type' portion of 
    ## of the JSON, an IF condition must be made.
    # calc aux power type
    user_aux_type = user_choices['aux_power_type']
    if user_aux_type != "none":
        user_num_aux_powers = user_choices['aux_power_units']
        cost_of_aux_type = att_costs['power_type'][user_aux_type]['cost']
        total_cost += user_num_aux_powers * int(cost_of_aux_type)

    # calc power types
    user_power_type = user_choices['power_type']
    user_num_powers = user_choices['power_units']
    cost_of_power_type = att_costs['power_type'][user_power_type]['cost']
    total_cost += user_num_powers * int(cost_of_power_type)

    
    return total_cost



# Things that have mass:
#   - tyres
#   - armour (see special increase if wheel > 4)
#   - motive power
#   - motive aux power
#   - offensive caps
def calc_total_mass(user_choices):
    total_mass = 0

    # retrive json of all atts weights (but in JSON called mass)
    # then turn it into JSON format for easier use.
    url_html = urllib.request.urlopen(JSON_DATA_URL)
    data = url_html.read()
    att_costs = json.loads(data.decode('utf-8'))

    
    # calc tyres
    user_num_tyres = user_choices['qty_tyres']
    user_tyre_type = user_choices['tyres']
    tyre_type_mass = att_costs['tyres'][user_tyre_type]['mass']
    total_mass += user_num_tyres * int(tyre_type_mass)

    # calc armour, since you can only have 1 type we just add to total
    # HOWEVER, the mass changes when the num of wheels in a buggy
    # is >4. Which each wheel above 4, 10% of mass is added per wheel.
    user_armour = user_choices['armour']
    user_num_wheels = int(user_choices['qty_wheels'])

    # if num of wheel >4, percentage addition is made but if 4, then it's simply
    # final calculation multipled by 1, so nothing changes unless it's >4. 
    remainder_wheels = user_num_wheels - 4
    remainder_wheels_cost = (remainder_wheels/10) +1 
    #^convert to % form, since each wheel is 10%, only divide by 10.
    # adding 1 so percentage is added on top of original value, instead of simply calculating its percentage.

    armour_mass = att_costs['armour'][user_armour]['mass']
    user_armour_mass = int(armour_mass) * remainder_wheels_cost
    total_mass += user_armour_mass

    # calc attack
    user_num_attacks = user_choices['qty_attacks']
    user_attack = user_choices['attack']
    mass_attack = att_costs['attack'][user_attack]['mass']
    total_mass += user_num_attacks * int(mass_attack)

    ## because 'none' is not included in the 'power_type' portion of 
    ## of the JSON, but still an option for the aux power type, 
    ## an IF condition must be made.
    # calc aux power type
    user_aux_type = user_choices['aux_power_type']
    if user_aux_type != "none":
        user_num_aux_powers = user_choices['aux_power_units']
        mass_of_aux_type = att_costs['power_type'][user_aux_type]['mass']
        total_mass += user_num_aux_powers * int(mass_of_aux_type)

    # calc power types
    user_power_type = user_choices['power_type']
    user_num_powers = user_choices['power_units']
    mass_of_power_type = att_costs['power_type'][user_power_type]['mass']
    total_mass += user_num_powers * int(mass_of_power_type)


    return total_mass


print(calc_total_mass(USER_CHOICES))