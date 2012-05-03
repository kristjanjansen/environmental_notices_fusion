#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import codecs
import csv
import cgi
import random
import cStringIO
import os
# import logging
# import logging.config

from datetime import date, timedelta, datetime
from BeautifulSoup import BeautifulSoup, Tag, NavigableString

from fusiontables.authorization.clientlogin import ClientLogin
from fusiontables.sql.sqlbuilder import SQL
from fusiontables.fileimport.fileimporter import CSVImporter
from fusiontables.ftclient import *

# Must be set
INDEX_URL = "http://www.ametlikudteadaanded.ee/"
DATAFILE_NAME = os.path.join(os.path.dirname(__file__), 'datafile.csv')
MAX_ITEMS = 30

CATEGORIES = [
    u'Kaevandused ja maardlad', 
    u'Hooned ja ehitised', 
    u'Teede ehitusega seotud tegevus',
    u'Veekogudega seotud arendus',
    u'Tööstus',
    u'Riigikaitse rajatis',
    u'Avalikku ruumi puudutav planeering',
    u'Jäätmetega seotud teade', 
    u'Saasteloaga seotud teade']

CATEGORIES_KEYWORDS = [
    [u'lubjakivi', 'maardla', u'karjäär', 'maavara', 'kaevandamise', 'kaevandamine', u'mäeeraldis'],
    [u'ehitusõigus', 'hoonestustingimus', 'kruntideks jaotamine', 'elamu'],
    [u'maanteeamet'],
    [u'paadikanal', 'lautri', 'lauter', 'paadisilla','paadisild', u'paisjärv','saneerimisprojekt', 'vee erikasutus',],
    [u'töötlemis', u'töötlemine', 'nafta', 'saasteaine'],
    [u'kaitseministeerium', u'harjutusvälja', u'harjutusväli'],
    [u'loodusrada', 'puhkeala', 'infomaja', 'teemaplaneering', 'puhkemajandus'],
    [u'jäätme', u'prügi'],
    [u'saasteloa']  
    ]

AT_TYPES = {
    "580082": "Geneetiliselt muundatud organismide keskkonda viimise teated",
    "170163": "Geoloogilise uuringu loa taotlemisteated",
    "170162": "Geoloogilise uuringu load",
    "170249": "Jahipiirkonna kasutusõiguse loa taotlemisteated",
    "170250": "Jahipiirkonna kasutusõiguse lubade teated",
    "532826": "Jäätmekavade algatamise teated",
    "170175": "Jäätmeloa andmise teated",
    "170174": "Jäätmeloa taotlemisteated",
    "170176": "Kaevandamisloa taotlemisteated",
    "170177": "Kaevandamisloa väljastamisteated",
    "170178": "Keskkonnamõju hindamise teated",
    "170251": "Loodusobjekti kaitse alla võtmise teated",
    "170190": "Maa riigi omandisse jätmise teated",
    "170191": "Maakonnaplaneeringu kehtestamisteated",
    "170207": "Saasteloa taotlemisteated",
    "170208": "Saasteloa väljastamisteated",
    "301254": "Saastuse kompleksloa taotlemise teated",
    "301253": "Saastuse kompleksloa väljastamise teated",
    "170212": "Vee erikasutusloa taotlemise teated",
    "170213": "Vee erikasutusloa väljastamisteated",
    "301251": "Veemajanduskava algatamise menetluse teated",
    "301252": "Veemajanduskava kinnitamise teade",
}

# logging.config.fileConfig('logging.conf')
# logger = logging.getLogger('scraper')

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class Scraper:
    
    #the main AT url
    index_url = ''
    #current scraping url
    url = ''    
    #the number of max items to retrieve, limits the recursion occasionally/purposedly
    max_items = ''    
    #filename where to write the current scraping result
    filename = ''
    
    #geonames account
    genames_user = ''

    def geo_term_extract(self, desc):
        data = values ={
                 'maxRows':'1',
                 'fuzzy':'1',
                 'country':'EE',
                 'featureClass':'P',
                 'operator':'OR',
                 'username':self.geonames_user,
                 'q':desc.encode('utf-8')}
        data=urllib.urlencode(values)
    
        link = u"http://api.geonames.org/search"
        xmldata = urllib.urlopen(link, data)
        soup = BeautifulSoup(xmldata)
    #   print soup.prettify()
        lng = '0'
        lat = '0'
        if len(soup.findAll("lat")) > 0:
            lng = soup.findAll("lng")[0].text
            lat = soup.findAll("lat")[0].text
            lat_f = float(lat)
            lng_f = float(lng)
            lat = '%.5f' % ((lat_f * 10000 + random.uniform(1,80))/10000)
            lng = '%.5f' % ((lng_f * 10000 + random.uniform(1,80))/10000)
        
        soup2 = BeautifulSoup()
        tag1 = Tag(soup2, "Point")
        tag2 = Tag(soup2, "coordinates")
        soup2.insert(0, tag1)
        tag1.insert(0, tag2)
        text = NavigableString(lng + "," + lat)
        tag2.insert(0, text)
    #   print soup2
        result = (soup2.__str__()).encode("utf-8")
        return [result, lat, lng]

    def assign_category(self, desc):
        cat = ''
        id = 0
        for i, row in enumerate(CATEGORIES):
            for item in CATEGORIES_KEYWORDS[i]:     
                if desc.find(item) > 0:
                    cat = row
                    id = i+1
                    break;
            if cat != '':
                break;
        return str(id), cat


    def scrape_table(self, soup):
      
        username = os.environ['GOOGLE_USERNAME']
        password = os.environ['GOOGLE_PASSWORD']

        token = ClientLogin().authorize(username, password)
        ft_client = ClientLoginFTClient(token)
      
        tableid = 1011748
        
        try:
            data_table = soup.findAll("table", { "width" : "100%" })[4]
            rows = data_table.findAll("tr")
        except:
            rows = []            
            self.url = ''
            # logger.warning("Content not found")
            
        csvfile = open(self.filename, 'a')
        csvwriter = UnicodeWriter(csvfile)

        record = {}
        for i in range(len(rows)):
            if i % 3 == 0:
                table_cells = rows[i].findAll("td")
                if table_cells[0]['width']:
                    if table_cells[0]['width'] != "35":
                        #print table_cells
                        link = self.index_url + table_cells[2].find("a")['href']
                        record['ID'] = link[22 + len(self.index_url):len(link)]
                        record['Date'] = table_cells[0].text[6:len(table_cells[0].text)]
                        record['Type'] = cgi.escape(table_cells[1].text)
                        desc_row_cells = rows[i+1].findAll("td")
                        desc = desc_row_cells[0]

                        a = desc.renderContents()
                        a = a.decode("utf-8")
                        if a.startswith(u'<br />'):
                            a = a[7:len(a)]

                        record['Description'] = a # desc.text #desc.text[0:100]

                        geo = self.geo_term_extract(desc.text)
                        record['Geometry'] = geo[0]

                        category = self.assign_category(desc.text)
                        record['CategoryId'] = category[0]
                        record['Category'] = category[1]
                        record['Lat'] = geo[1]
                        record['Lng'] = geo[2]
                        #print record

                    #    ft_client.query(SQL().insert(tableid, dict(record)))

                        csvwriter.writerow(
                            [record['ID'], record['Date'], record['Type'], record['Description'], 
                            record['Geometry'], record['Category'], record['CategoryId'], 
                            record['Lat'], record['Lng']])
        csvfile.close()


    def scrape_and_look_for_next_link(self, link, start):

        if (start < self.max_items):
            # logger.info(link)            
            html = urllib.urlopen(link)
            soup = BeautifulSoup(html)
            # print soup.prettify()
            self.scrape_table(soup)
            start = start + 10
            if self.url != '':
                next_link = self.url + "&srange=" + str(start) + "-" + str(start + 9)
                self.scrape_and_look_for_next_link(next_link, start)
            #else:
                # logger.info("Exiting at: " + str(start - 10) +'-'+ str(start - 1))
        #else:
            # logger.info("Exiting at: " + str(start - 10) +'-'+ str(start - 1))

    def __init__(self, days_past=1, max_items=10, filename=DATAFILE_NAME, index_url = INDEX_URL):
        header = ['Id', 'Date', 'Type', 'Description', 'Geometry', 'Category', 'CategoryId', 'Lat', 'Lng']
        self.filename = filename
        self.index_url = index_url
        self.max_items = max_items
        datafile = open(self.filename, 'w')        
        writer = UnicodeWriter(datafile)
        writer.writerow(header)
        datafile.close()

        d_today = date.today()  
        s_date = d_yesterday = d_today - timedelta(days = days_past)
        e_date = d_yesterday = d_today - timedelta(days = 1)
    
        self.url = self.index_url + u"index.php?act=1"
        self.url = self.url + "&salguskpvavald=" + s_date.strftime("%d.%m.%Y") + "&sloppkpvavald=" + e_date.strftime("%d.%m.%Y")
        self.url = self.url + "&steateliigid=" + ";".join(AT_TYPES.keys())
        
        # print self.url
# How to run
#scraper = Scraper(1, 10)
#scraper.geonames_user = GEONAMES_USERNAME
#scraper.scrape_and_look_for_next_link(scraper.url, 1)


