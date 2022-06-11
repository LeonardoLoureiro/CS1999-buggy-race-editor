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
	"mass",
	"name"
]

# List of all attributes a buggy has, this way, no hard coding it again is needed
# and rather it can be iterated over. All attributed except those which are of bool
# nature.
ATTRIBUTES = ATTRIBUTES_WHOLE[1:15] + ['algo', 'name']



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
## Constants - Stuff that we need to know that won't ever change!


# basic const vars
DATABASE_FILE = "databases/buggies.db"
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "https://rhul.buggyrace.net"

SPECS_URL = "https://rhul.buggyrace.net/specs/"

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
    "steady",
	"buggy"
]