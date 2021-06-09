# -*- coding: utf-8 -*-
"""

@author: timpr
"""

import names
import random as rand
from datetime import datetime

class Customer(object):
    """
    A customer class, corresponding to a  Tim's Shoes customer
    
    """
    def __init__(self, first_purchase_date):
        """
        Initialize a customer object
        
        Parameters:
            first_purchase_date (datetime): the date the customer first made a purchase
            customer_id (int): a unique id number for the customer
  
        """  
        self.first_purchase_date = first_purchase_date
        self.last_purchase_date = self.first_purchase_date
        self.first_name = names.get_first_name()
        self.last_name = names.get_last_name()
        self.email = self.first_name + "." + self.last_name + "@gmail.com"
    
        self.phone_num = "" 
        for i in range(0,10):
            self.phone_num += str(rand.randint(0,9))
        
        self.customer_id = "NULL"
        self.shoe_club_id = "NULL"
        self.shoe_club_signup_date = datetime.strptime("9999-01-01", "%Y-%m-%d")
        self.shoe_club_status = "Inactive"
        
    def set_last_purchase_date(self, last_purchase_date): 
        self.last_purchase_date = last_purchase_date
        return
    
    def set_shoe_club_id(self, shoe_club_id): 
        self.shoe_club_id = shoe_club_id
        return

    def set_shoe_club_signup_date(self, shoe_club_signup_date): 
        self.shoe_club_signup_date = shoe_club_signup_date
        return    
    
    def set_shoe_club_status(self, shoe_club_status): 
        self.shoe_club_status = shoe_club_status
        return  

    def set_customer_id(self, customer_id): 
        self.customer_id = customer_id
        return  
    
    def get_last_name(self):
        return(self.last_name)
    
    def get_customer_id(self):
        return(self.customer_id)

    def get_shoe_club_signup_date(self): 
        return (self.shoe_club_signup_date)   

    def get_shoe_club_status(self): 
        return (self.shoe_club_status)

    def log_customer_to_db(self, mycursor):
        """
        Inserts customer data into the Customer MySQL table
        
        Parameters:   
            mycursor (MySQL Cursor): a cursor to perform database operations from Python
        
        """        
        self.customer_sql = '''INSERT INTO customers (customer_id, customer_first_name, customer_last_name, 
                              customer_email, customer_phone, first_purchase_date, last_purchase_date, 
                              shoe_club_id, shoe_club_signup_date, shoe_club_status) VALUES (%s, %s, %s,
                              %s, %s, %s, %s, %s, %s, %s)'''

        self.customer_tuple = (self.customer_id, self.first_name, self.last_name, self.email,
                               self.phone_num, self.first_purchase_date, self.last_purchase_date,
                               self.shoe_club_id, self.shoe_club_signup_date, self.shoe_club_status)
        
        try:                                                                                     
            mycursor.execute(self.customer_sql, self.customer_tuple)
            return
        except Exception:
            return