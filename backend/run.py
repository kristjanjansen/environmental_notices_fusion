#!/usr/bin/env python
# -*- coding: utf-8 -*-

from authorization.clientlogin import ClientLogin
from sql.sqlbuilder import SQL
import ftclient
from fileimport.fileimporter import CSVImporter
from scraper import *

DATAFILE_NAME = 'data/datafile.csv'

DAYS_IN_PAST = 1
MAX_ITEMS = 30 #50-60 should be enough for a day

DEST_FT_TABLE_ID = 831071

if __name__ == "__main__":

    import sys, getpass
    if len(sys.argv) < 2:
        print "Usage: run.py <geonamesuser> <googleaccount> <googlepass> "
        sys.exit()
   
    scraper = Scraper(DAYS_IN_PAST, MAX_ITEMS, 'data/datafile.csv')
    scraper.geonames_user = sys.argv[1]
    scraper.scrape_and_look_for_next_link(scraper.url, 1)

    username = sys.argv[2]
    password = sys.argv[3]
    
    token = ClientLogin().authorize(username, password)
    ft_client = ftclient.ClientLoginFTClient(token)
   
    #import a table from CSV file
    tableid = DEST_FT_TABLE_ID
    CSVImporter(ft_client).importMoreRows(DATAFILE_NAME, tableid)
    print tableid

