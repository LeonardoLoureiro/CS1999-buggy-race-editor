import urllib.request
from bs4 import BeautifulSoup

def get_tables(url_extract_tables, find_str="table"):
    # raw html tables
    url_html = urllib.request.urlopen(url_extract_tables)
    
    ## Scrub html file and ony get what is needed, which are the tables with the prices, etc.
    # first turn 'raw' html into bs4 variable, so searching is easier
    bs4_html = BeautifulSoup(url_html, features="lxml")

    # removing hamster pic from 1st table in normal specs table. Sorry :/
    try:
        bs4_html.img.decompose()

    except:
        pass

    # now get all tables...
    tables = bs4_html.find_all(find_str)
    
    return tables