'''

@author: heikko
'''

from authorization.clientlogin import ClientLogin
from sql.sqlbuilder import SQL
import ftclient
from fileimport.fileimporter import CSVImporter

if __name__ == "__main__":

    import sys, getpass
    username = sys.argv[1]
    password = sys.argv[2]
  
    token = ClientLogin().authorize(username, password)
    ft_client = ftclient.ClientLoginFTClient(token)
   
    #import a table from CSV file
    tableid = 644334
    CSVImporter(ft_client).importMoreRows("datafile.csv", tableid)
    print tableid
  
