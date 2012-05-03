#!/usr/bin/env python
# -*- coding: utf-8 -*-


from fusiontables.authorization.clientlogin import ClientLogin
from fusiontables.sql.sqlbuilder import SQL
from fusiontables.fileimport.fileimporter import CSVImporter
from fusiontables.ftclient import *

from scraper import *

import os

from pprint import pprint

DATAFILE_NAME = os.path.join(os.path.dirname(__file__), 'datafile.csv')

DAYS_IN_PAST = 20
MAX_ITEMS = 5 #50-60 should be enough for a day

DEST_FT_TABLE_ID = 1011748


if __name__ == "__main__":

    import sys, getpass
    if not os.environ['GEONAMES_USERNAME']:
        print "You need to set environment variables to run the application. See README.txt"
        sys.exit()
   
    scraper = Scraper(DAYS_IN_PAST, MAX_ITEMS, DATAFILE_NAME)
    scraper.geonames_user = os.environ['GEONAMES_USERNAME']
    scraper.scrape_and_look_for_next_link(scraper.url, 1)

    username = os.environ['GOOGLE_USERNAME']
    password = os.environ['GOOGLE_PASSWORD']
    
    token = ClientLogin().authorize(username, password)
    ft_client = ClientLoginFTClient(token)
    tableid = DEST_FT_TABLE_ID
    CSVImporter(ft_client).importMoreRows(DATAFILE_NAME, tableid)
    print tableid
