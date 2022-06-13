# data in JSON: https://rhul.buggyrace.net/specs/data/types.json

import json
import urllib.request

JSON_DATA_URL = "https://rhul.buggyrace.net/specs/data/types.json"


# algo and flag colours/patterns are not counted 
# since they do not cost anything to begin with...
BOOL = ["antibiotic", "banging", "fireproof", "insulated"]

"""
    cost_of_tyres = number of wheels x type of tyres
    cost_of_attack = number of attacks x qty_attacks
    cost_of_hamsters = 5 x hamster_booster
    cost_of_aux_power_type = aux_power_type x aux_power_units
    cost_of_powers = power_type x power_units
"""

# This function calculate the total cost of the buggy,
# first by iterating over bool values, as its easier,
# then through each individual attribute which has a cost
# value attatched:
#   - tyres
#   - armour
#   - attacks
#   - hasmter boosters
#   - power type
#   - aux power type (a backup power type)
def calc_total_cost_wtf(user_choices, att_costs):
    total_cost = 0

    # retrive json of all atts costs
    # then turn it into JSON format for easier use.
    url_html = urllib.request.urlopen(JSON_DATA_URL)
    data = url_html.read()
    att_costs = json.loads(data.decode('utf-8'))

    # calc bool vals
    if user_choices.antibiotic:
        total_cost += att_costs['special']['antibiotic']['cost']
    
    if user_choices.banging.data:
        total_cost += att_costs['special']['banging']['cost']
    
    if user_choices.fireproof.data:
        total_cost += att_costs['special']['fireproof']['cost']

    if user_choices.insulated.data:
        total_cost += att_costs['special']['insulated']['cost']

    # calc tyres
    user_num_tyres = user_choices.qty_tyres.data
    user_tyre_type = user_choices.tyres.data
    tyre_type_cost = att_costs['tyres'][user_tyre_type]['cost']
    total_cost += user_num_tyres * float(tyre_type_cost)


    # calc armour
    # since you can only have 1 type we just add to total
    # HOWEVER, the cost changes when the num of wheels in a buggy
    # is >4. Which each wheel above 4, 10% of cost is added per wheel.
    user_armour = user_choices.armour.data
    user_num_wheels = user_choices.qty_wheels.data

    # if num of wheel >4, percentage addition is made but if 4, then it's simply
    # final calculation multipled by 1, so nothing changes unless it's >4. 
    remainder_wheels = user_num_wheels - 4
    remainder_wheels_cost = (remainder_wheels/10) +1 
    #^convert to % form, since each wheel is 10%, only divide by 10.
    # adding 1 so percentage is added on top of original value, instead of simply calculating its percentage.

    armour_cost = att_costs['armour'][user_armour]['cost']
    user_armour_cost = float(armour_cost) * remainder_wheels_cost
    total_cost += user_armour_cost


    # calc attack
    user_num_attacks = user_choices.qty_attacks.data
    user_attack = user_choices.attack.data
    cost_attack = att_costs['attack'][user_attack]['cost']
    total_cost += float(user_num_attacks) * float(cost_attack)


    # calc hasmter boosters
    user_num_hams = user_choices.hamster_booster.data
    cost_of_hams = att_costs['special']['hamster_booster']['cost']
    total_cost += user_num_hams * float(cost_of_hams)
    

    ## because 'none' is not included in the 'power_type' portion of 
    ## of the JSON, an IF condition must be made.
    # calc aux power type
    user_aux_type = user_choices.aux_power_type.data
    if user_aux_type != "none":
        user_num_aux_powers = user_choices.aux_power_units.data
        cost_of_aux_type = att_costs['power_type'][user_aux_type]['cost']
        total_cost += user_num_aux_powers * float(cost_of_aux_type)


    # calc power types
    user_power_type = user_choices.power_type.data
    user_num_powers = user_choices.power_units.data
    cost_of_power_type = att_costs['power_type'][user_power_type]['cost']
    total_cost += user_num_powers * float(cost_of_power_type)

    return total_cost


# This function calculates the total mass of a buggy
# depending on any attribute which carries mass,
# which are the following:
#   - tyres
#   - armour (see special increase if wheel > 4)
#   - attacks
#   - power type
#   - aux power type (a backup power type)
def calc_total_mass_wtf(user_choices, att_costs):
    total_mass = 0
    
    # calc tyres
    user_num_tyres = user_choices.qty_tyres.data
    user_tyre_type = user_choices.tyres.data
    tyre_type_mass = att_costs['tyres'][user_tyre_type]['mass']
    total_mass += user_num_tyres * float(tyre_type_mass)

    # calc armour, since you can only have 1 type we just add to total
    # HOWEVER, the mass changes when the num of wheels in a buggy
    # is >4. Which each wheel above 4, 10% of mass is added per wheel.
    user_armour = user_choices.armour.data
    user_num_wheels = user_choices.qty_wheels.data

    # if num of wheel >4, percentage addition is made but if 4, then it's simply
    # final calculation multipled by 1, so nothing changes unless it's >4. 
    remainder_wheels = user_num_wheels - 4
    remainder_wheels_cost = (remainder_wheels/10) +1 
    #^convert to % form, since each wheel is 10%, only divide by 10.
    # adding 1 so percentage is added on top of original value, instead of simply calculating its percentage.

    armour_mass = att_costs['armour'][user_armour]['mass']
    user_armour_mass = float(armour_mass) * remainder_wheels_cost
    total_mass += user_armour_mass

    # calc attack
    user_num_attacks = user_choices.qty_attacks.data
    user_attack = user_choices.attack.data
    mass_attack = att_costs['attack'][user_attack]['mass']
    total_mass += user_num_attacks * float(mass_attack)

    ## because 'none' is not included in the 'power_type' portion of 
    ## of the JSON, but still an option for the aux power type, 
    ## an IF condition must be made.
    # calc aux power type
    user_aux_type = user_choices.aux_power_type.data
    if user_aux_type != "none":
        user_num_aux_powers = user_choices.aux_power_units.data
        mass_of_aux_type = att_costs['power_type'][user_aux_type]['mass']
        total_mass += user_num_aux_powers * float(mass_of_aux_type)

    # calc power types
    user_power_type = user_choices.power_type.data
    user_num_powers = user_choices.power_units.data
    mass_of_power_type = att_costs['power_type'][user_power_type]['mass']
    total_mass += user_num_powers * float(mass_of_power_type)


    return total_mass


def calc_cost_mass_wtf(buggy_wtform):
    # retrive json of all atts weights (but in JSON called mass)
    # then turn it into JSON format for easier use.
    url_html = urllib.request.urlopen(JSON_DATA_URL)
    data = url_html.read()
    att_costs = json.loads(data.decode('utf-8'))

    total_cost = calc_total_cost_wtf(buggy_wtform, att_costs)
    
    total_mass = calc_total_mass_wtf(buggy_wtform, att_costs)

    return [total_cost, total_mass]