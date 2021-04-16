# -*- coding: utf-8 -*-
"""

@author: timpr
"""

import names
import random as rand
from datetime import datetime, timedelta

class CustomerTable(object):
    """
    An customer table class, corresponding to a MySQL table used to store customer details on Tim's Shoes website
    
    """
    def __init__(self, mycursor, num_customers, start_date):
        """
        Initialize an CustomerTable object 
        
        Parameters:
            mycursor (MySQL Cursor): a cursor to perform database operations from Python
            num_customers (int): the number of customers to create in the table
            start_date (datetime): the earliest data a customer could have registered on the site
    
        """  
        self.mycursor = mycursor
        self.num_customers = num_customers
        self.start_date = start_date
        self.end_date = datetime.today()
        
        # Create customer table using randomly generated entries
        self.customer_list = []
        for customer in range(self.num_customers):
            self.customer_list.append(self.create_new_customer(self.start_date, self.end_date))
        
        # Insert values into customer MySQL table
        self.insert_customer_data(self.customer_list)

    def create_new_customer(self, cust_start_date, cust_end_date):
        """
        Creates random data for a new registered customer
        
        Parameters:
            cust_start_date (datetime): the earliest date the customer can register
            cust_end_date (datetime): the latest date the customer can register
            
        Returns
            first_name (string): the first name of the customer
            last_name (string): the last name of the customer
            email (string): the email address of the customer
            phone_num (string): the phone number of the customer
            signup_date (datetime): the date the customer registered

        """
        self.cust_start_date = cust_start_date
        self.cust_end_date = cust_end_date
        self.day_range = (self.cust_end_date - self.cust_start_date).days
        
        self.first_name = names.get_first_name()
        self.last_name = names.get_last_name()
        self.email = self.first_name + "." + self.last_name + "@gmail.com"
    
        self.phone_num = "" 
        for i in range(0,10):
            self.phone_num += str(rand.randint(0,9))
            
        self.signup_date = self.start_date + timedelta(days = rand.randrange(self.day_range))
        
        return(self.first_name, self.last_name, self.email, self.phone_num, self.signup_date)
    
    def insert_customer_data(self, new_customer_list):
        """
        Inserts a list of customer data into the customer MySQL table
        
        Parameters:
            new_customer_list (List<Tuple>): A list containing a tuple for each new customer entry,
                                             formatted to matched MySQL customer table columns
        
        Returns:
            None
        
        """
        self.new_customer_list = new_customer_list
        
        self.sql = '''INSERT INTO customers (customer_first_name, customer_last_name, customer_email, 
            customer_phone, signup_date) VALUES (%s, %s, %s, %s, %s)'''
    
        # Insert values into customer table        
        self.mycursor.executemany(self.sql, self.new_customer_list)
        
        return

    def run_customer_growth_campaign(self, camp_start_date, current_users):
        """
        Start a marketing effort to increase the number of registered customers 
        at a higher rate than usual.
        
        Parameters:
            camp_start_date (datetime): the beginning of the marketing campaign
            current_users (int): the number of users currently registered on the site
        
        Returns:
            None
        
        """
        
        self.camp_start_date = camp_start_date
        self.current_users = current_users
        
        # Randomly select campaign length
        self.camp_length = 30
        self.camp_end_date = self.camp_start_date + timedelta(days = self.camp_length)
        
        # Randomly choose an effectiveness level for the marketing campaign
        self.effectivness = rand.choice(["no_impact", "low_impact", "moderate_impact", "high_impact"])
        if self.effectivness == "no_impact":
            self.new_customers = 0
        elif self.effectivness == "low_impact":
            self.new_customers = int(self.current_users * 0.001 * (1+ rand.random()))
        elif self.effectivness == "moderate_impact":
            self.new_customers = int(self.current_users * 0.005 * (1+ rand.random()))
        else:
            self.new_customers = int(self.current_users * 0.02 * (1+ rand.random()))
       
        # Create random new customers who registered during campaign
        self.campaign_customers = []
        for new_cust in range(self.new_customers):
            self.campaign_customers.append(self.create_new_customer(self.camp_start_date,                                                         
                                                                    self.camp_end_date))
 
        # Add customers to customers MySQL table
        self.insert_customer_data(self.campaign_customers)
        
        return