# -*- coding: utf-8 -*-
"""

@author: timpr
"""

import mysql.connector
from datetime import datetime

from modules.initiate_tables import initiate_base_tables
from classes.event_class import EventsTable
from classes.item_class import ItemTable


if __name__ == "__main__":
    # Establish connection to timsshoes MySQL database schema
    mydb = mysql.connector.connect(host="localhost",
                                   user="root",
                                   password="Tt556677",
                                   database = "timsshoes",
                                   connection_timeout = 28800
                                   )
        
    mycursor = mydb.cursor()
    
    # mycursor.execute('''DROP TABLE customers, events, items''')
    
    # Initate tables for database
    initiate_base_tables(mycursor)
    
    # Date of business launch
    start_date = datetime.strptime("2018-01-01", "%Y-%m-%d")
                         
    # Populate items table
    item_table = ItemTable(mycursor)
    
    # Populate events table
    events_table = EventsTable(mycursor, start_date)
    
    # Save additions to MySQL database
    mydb.commit()


