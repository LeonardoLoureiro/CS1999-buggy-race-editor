import urllib.request
from bs4 import BeautifulSoup

SPECS_URL = "https://rhul.buggyrace.net/specs/"


# TODO:
#   Get current attributes and compare them to each tables' info
    

def get_tables():
    # raw html tables
    url_html = urllib.request.urlopen(SPECS_URL)
    
    ## Scrub html file and ony get what is needed, which are the tables with the prices, etc.
    # first turn 'raw' html into bs4 variable, so searching is easier
    bs4_html = BeautifulSoup(url_html, features="lxml")

    # removing hamster pic from 1st table. Sorry :/
    bs4_html.img.decompose()

    # now get all tables...
    tables = bs4_html.find_all("table")
    tables = tables[1:] 
    #^getting rid of 1st table, as it merely states all the different attributes 
    # and is not useful for this page

    return tables