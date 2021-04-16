# -*- coding: utf-8 -*-
"""

@author: timpr
"""

def initiate_base_tables(mycursor):
    """
    Sets up tables for use in Tim's shoes database schema

    Parameters:
        mycursor (MySQL Cursor): a cursor to perform database operations from Python
     
    Returns:
        None

    """
    # Initiate columns for customers table
    mycursor.execute('''CREATE TABLE customers (customer_id INT AUTO_INCREMENT PRIMARY KEY,
                                              customer_first_name VARCHAR(255),
                                              customer_last_name VARCHAR(255),
                                              customer_email VARCHAR(255),
                                              customer_phone VARCHAR(255),
                                              signup_date DATE)''')    

    # Initiate columns for items table
    mycursor.execute('''CREATE TABLE items (item_id INT AUTO_INCREMENT PRIMARY KEY, 
                                          item_name VARCHAR(255), 
                                          item_price FLOAT, 
                                          availability VARCHAR(255), 
                                          item_brand VARCHAR(255), 
                                          item_type VARCHAR(255))''')
        
    # Initiate columns for events table
    mycursor.execute('''CREATE TABLE events (event_id INT AUTO_INCREMENT PRIMARY KEY, 
                                          event_date DATE, 
                                          event_time TIME, 
                                          event_type VARCHAR(255), 
                                          customer_id INT, 
                                          product_id INT, 
                                          device_type VARCHAR(255), 
                                          device_info VARCHAR(255), 
                                          ab_test_notes VARCHAR(255))''')
    
    return