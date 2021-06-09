# -*- coding: utf-8 -*-
"""

@author: timpr
"""
from datetime import datetime, timedelta
import random as rand
from classes.customer_class import Customer

class EventsTable(object):
    """
    An event table class, corresponding to a MySQL table used to store events on Tim's Shoes website
    
    """
    def __init__(self, mycursor, start_date):
        """
        Initialize an EventsTable object 
        
        Parameters:
            mycursor (MySQL Cursor): a cursor to perform database operations from Python
            start_date (datetime): the date the website went live
            
        """
        self.mycursor = mycursor
        self.date = start_date
        self.end_date = datetime.today()
        self.customer_list = []
        self.customer_id_allocation = 1
        self.camp_days_rem = 0
        
        self.item_ids = self.get_item_ids()
        
        self.device_dict = {"computer" : ["dell", "hp", "apple", "lenovo", 
                                          "microsoft", "asus", "asus", "other"],
                            "phone":    ["apple", "google", "huawei", "samsung", "htc",
                                         "nokia", "motorola", "other"],
                            "tablet":   ["apple", "amazon", "microsoft", "other"]
                            }
        
        self.shoe_club_join_prob = 0.25
        self.control_conversion_prob = 0.7
                
        # Base query to add events to the MySQL table
        self.event_sql = '''INSERT INTO events (event_date, event_time, event_type, customer_id,
                    product_id, device_type, device_info, order_number, ab_test_notes) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
       
        self.day_counter = 0
        # Randomly create events for each day
        while self.date < self.end_date:
            self.day_counter += 1
           
            # Run a new A/B test every 2 weeks
            if (self.day_counter - 1) % 14 == 0:
                self.test_conversion_prob, self.test_label = self.initiate_ab_test(self.day_counter)
            
            # Instigate bugs on randomly selected days
            self.impacted_device_type, self.impacted_device_info = self.instigate_bug()
            
            # Run an shoe club growth campaign once per year
            if self.day_counter % 365 == 0:
                self.shoe_club_join_prob, self.camp_days_rem = self.initiate_shoe_club_growth_campaign()
            elif self.camp_days_rem > 1:
                self.camp_days_rem -= 1
            elif self.camp_days_rem == 1:
               self.shoe_club_join_prob = 0.25 
               self.camp_days_rem -= 1
              
            # Randomly generate new customers making their first purchase on the day
            self.num_current_customers = len(self.customer_list)
            self.new_customers = self.generate_new_customers(self.num_current_customers, self.date)
            
            for new_cust in self.new_customers:                
                # Randomly simulate a view and event for the new customer
                new_cust.set_customer_id(self.customer_id_allocation)
                self.viewed_product = self.generate_viewed_product()
                self.click_time = self.generate_click_time()
                self.device_type, self.device_info = self.generate_user_device()                
                self.purchase_time = self.generate_purchase_time(self.click_time)
                
                # Log events to the database
                self.log_event_to_db(             
                                    self.date, 
                                    self.click_time, 
                                    "clickthrough",
                                    self.customer_id_allocation, 
                                    self.viewed_product, 
                                    self.device_type, 
                                    self.device_info, 
                                    "0", 
                                    ""
                                    )
                self.log_event_to_db(
                                    self.date, 
                                    self.purchase_time, 
                                    "purchase",
                                    self.customer_id_allocation, 
                                    self.viewed_product, 
                                    self.device_type, 
                                    self.device_info, 
                                    "0", 
                                    ""
                                    )
                
                # Randomly select some new customers to sign up for the shoe club
                if self.join_shoe_club(self.shoe_club_join_prob) == True:
                    new_cust = self.allocate_shoe_club_membership(new_cust, self.date)
                
                # Increment id allocation to ensure each customer is assigned a unique id
                self.customer_id_allocation += 1
                
            # Select a subset of the existing customers to view an item on the day
            if(self.num_current_customers > 0):
                self.ret_indexes = self.generate_returning_customer_index_list(self.num_current_customers)
                
                for i in self.ret_indexes:                     
                    # Simulate clickthroughs for each returning customer
                    self.viewed_product = self.generate_viewed_product()
                    self.click_time = self.generate_click_time()
                    self.device_type, self.device_info = self.generate_user_device()
                    
                    # Check for bug impacts
                    if (self.device_type == self.impacted_device_type and 
                        self.device_info in self.impacted_device_info):
                        continue
                    
                    self.ret_cust_id = self.customer_list[i].get_customer_id()
                    
                    # Select some customers to be in the A/B test control group for conversion
                    if self.assign_test_group() == True:
                        self.ret_cust_return_prob = self.test_conversion_prob
                        self.ret_cust_test_note = self.test_label + "_test"
                    else:
                        self.ret_cust_return_prob = self.control_conversion_prob
                        self.ret_cust_test_note = self.test_label + "_control"  
                    
                    self.log_event_to_db(             
                                        self.date, 
                                        self.click_time, 
                                        "clickthrough",
                                        self.ret_cust_id, 
                                        self.viewed_product, 
                                        self.device_type, 
                                        self.device_info, 
                                        "0", 
                                        self.ret_cust_test_note
                                        )
                                                                 
                    if(self.makes_purchase(self.ret_cust_return_prob) == True):
                        self.purchase_time = self.generate_purchase_time(self.click_time)    
                        self.customer_list[i].set_last_purchase_date(self.date)
                        self.log_event_to_db(
                                            self.date, 
                                            self.purchase_time, 
                                            "purchase",
                                            self.ret_cust_id, 
                                            self.viewed_product, 
                                            self.device_type, 
                                            self.device_info, 
                                            "0", 
                                            self.ret_cust_test_note
                                            )
                        
                        # Randomly select some returning customers to sign up for or churn from the shoe club
                        if self.customer_list[i].get_shoe_club_status() == "Inactive":
                            if self.join_shoe_club(self.shoe_club_join_prob) == True:
                                self.allocate_shoe_club_membership(self.customer_list[i], self.date)
                        else:
                            self.leave_shoe_club(self.customer_list[i])
                        
            self.customer_list.extend(self.daily_new_customers)
            self.date += timedelta(days = 1)
            
        # Add all the customer data to the database
        for cust in self.customer_list:
            cust.log_customer_to_db(self.mycursor)
    
    def get_item_ids(self):
        """
        Create a list of all the ids of items available in the shop

        Returns:
            item_ids (List<string>): a list of item ids

        """
        self.mycursor.execute('''SELECT 
                                   item_id 
                               FROM 
                                   items 
                               WHERE 
                                   inventory > 0
                            ''')
        self.item_ids = self.mycursor.fetchall()
        return(self.item_ids)
    
    def generate_new_customers(self, num_current_customers, current_date):
        """
        Randomly creates a list of new customers, the length being proportionate to the number
        of existing customers
        
        Parameters:
            num_current_customers (int): the current number of customers registered to the site 
            current_date (datetime): the current date

        Returns:
            daily_new_customers (List<Customer>): a list of new customer objects

        """
        self.new_customers = int((10 + num_current_customers/200)*rand.random())
        self.daily_new_customers = []
        for i in range(self.new_customers):
            self.daily_new_customers.append(Customer(current_date))
        return(self.daily_new_customers)
  
    def generate_viewed_product(self):
        """
        Randomly selects an item for a customer to view
        
        Parameters:
            None

        Returns:
            viewed_product (string): the id of the viewed product

        """        
        self.viewed_product = rand.choice(self.item_ids)[0]        
        return(self.viewed_product)

    def generate_user_device(self):
        """
        Randomly selects a user device for an event

        Returns:
            device_type (string): the type of device the user is using e.g. computer 
            device_info (string): the make of the device e.g. Apple
        """
        self.device_type = rand.choice(["computer", "phone", "tablet"])
        self.device_info = rand.choice(self.device_dict[self.device_type])
        return (self.device_type, self.device_info)

    def generate_click_time(self):
        """
        Generates a random time for an clickthrough event.
        
        Parameters:
            None
            
        Returns:
            event_time (string): An event time string in the form HH:MM:SS
        
        """
        # Choose a random day time for a click event
        self.event_datetime = datetime.today() + timedelta(hours = rand.randint(0,24)) +\
                              timedelta(minutes = rand.randint(0,60))
        self.event_time = datetime.strftime(self.event_datetime,"%H:%M:%S")
              
        return(self.event_time)        
        
    def generate_purchase_time(self, click_time):
        """
        Generates a random time for an item purchase, given the time the item was clicked into.
        
        Parameters:
            click_time (string): the time (HH:MM:SS) that the item was clicked into. 
                                
        Returns:
            event_time (string): An event time string in the form HH:MM:SS
        
        """
        self.click_time = click_time
        # Add on a small amount of time after the corresponding click event
        self.event_datetime = datetime.strptime(self.click_time, "%H:%M:%S") +\
                              timedelta(minutes = rand.randint(0,60))
        self.event_time = datetime.strftime(self.event_datetime, "%H:%M:%S")
                    
        return(self.event_time)

    def generate_returning_customer_index_list(self, num_current_customers):
        """
        Creates a list of indexes relating to returning customers from the customer list
        
        Parameters:
            num_current_customers (int): current number of registered customers
                                
        Returns:
            returning_customer_indexes (List<int>): A list of unique integers relating to 
                                                    returning customers from the customer list
        
        """        
        self.num_ret_custs = int(rand.random()*0.05*self.num_current_customers)
        self.returning_customer_indexes = rand.sample(range(0, self.num_current_customers - 1), 
                                                      self.num_ret_custs)
    
        return (self.returning_customer_indexes)
    
    def log_event_to_db(self, 
                        event_date, 
                        event_time, 
                        event_type,
                        customer_id, 
                        product_id, 
                        device_type, 
                        device_info, 
                        order_number, 
                        ab_test_note):
        """
        Inserts an event into the Events database table.
        
        Parameters:
            event_date (datetime): the day of the event
            event_time (string): the time of the event in HH:MM:SS format
            event_type (string): the type of event (clickthrough or purchase)
            customer_id (int): the unique id of the customer making the event
            product_id (int): the unique id of the product involved in the event
            device_type (string): the type of device the customer is using
            device_info (string): the make of the device
            order_number (string): the order number of the customers purchase
            ab_test_note (string): an identifier tag linking events to tests
            
        Returns:
            None
        
        """
        self.event = (
                      event_date, 
                      event_time, 
                      event_type,
                      customer_id, 
                      product_id, 
                      device_type, 
                      device_info, 
                      order_number, 
                      ab_test_note
                      )
        self.mycursor.execute(self.event_sql, self.event) 
        return
    
    def join_shoe_club(self, prob):
        """
        Randomly decides if a customer will join the shoe club on the day.
        
        Parameters:
            prob (float): the probability of the customer joining the shoe club, e.g. 0.7
        
        Returns:
            joins_club (boolean): true if they join the club, false otherwise
        
        """
        if rand.random() < prob:
            return (True)
        else:
            return (False)

    def allocate_shoe_club_membership(self, customer, current_date):
        """
        Assign shoe club membership parameters to a customer joining the shoe club. Mutates
        the input customer object
        
        Parameters:
            customer (Customer): a customer who is joining the shoe club
            date (datetime): the current date
        
        Returns:
            None
        
        """
        customer.set_shoe_club_id = customer.get_last_name() + str(int(1000*rand.random()))
        customer.set_shoe_club_signup_date(current_date)
        customer.set_shoe_club_status("Active")
        return

    def leave_shoe_club(self, customer):
        """
        Checks to see if a user churns from the shoe club. Mutates the input customer object
        
        Parameters:
            customer (Customer): a customer who is joining the shoe club
        
        Returns:
            None
        
        """
        if rand.random() < 0.005:
            customer.set_shoe_club_status("Inactive")
        return

    def makes_purchase(self, prob):
        """
        Randomly decides if a customer will purchase an item they have clicked into
        
        Parameters:
            prob (float): the probability of the customer making a purchase, e.g. 0.7
        
        Returns:
            makes_purchase (boolean): true if they make a purchase, false otherwise
        
        """
        if rand.random() < prob:
            return (True)
        else:
            return (False)

    def initiate_ab_test(self, day_counter):
        """
        Generate conversion rates for A/B test group
        
        Parameters:
            day_counter (int): the day number, counted from the stores opening day
        
        Returns:
            test_conversion_prob (float): the purchase probability for the test control group
            test_label (string): a label used to identify users who have been exposed to a test
        
        """
        self.test_conversion_prob = rand.choice([0.67,0.68,0.69,0.70,0.71,0.72,0.73,0.75,0.80])
        self.test_label = "Test_" + str(int((day_counter-1)/14 + 1))
        return(self.test_conversion_prob, self.test_label)

    def assign_test_group(self):
        """
        Allocated customers into the control or test group
                
        Returns:
            test_group (boolean): true if they are in the test group, false if they are in the control
        
        """
        if rand.random() < 0.5:
            return (True)
        else:
            return (False)

    def instigate_bug(self,):
        """
        With a low probability, creates a bug that prevents clicks or sales on certain devices. Bugs are assumed to be
        resolved within a day
        
        Return:
            impacted_device_type (string): the device type that is impacted by the bug
            impacted_device_info (List<string>): the particular devices that are impacted by the bug
        
        """
        if rand.random() < 0.01:
            self.impacted_device_type = rand.choice(["computer", "phone", "tablet"])
            
            # Randomly select the device type variants that will be impacted
            self.variants_impacted = rand.randint(1, len(self.device_dict[self.impacted_device_type]))
            self.impacted_device_info = rand.sample(self.device_dict[self.impacted_device_type], 
                                                    self.variants_impacted )
        else:
            self.impacted_device_type = ""
            self.impacted_device_info = []
        
        return (self.impacted_device_type, self.impacted_device_info)
    
    def initiate_shoe_club_growth_campaign(self):
        """
        Generate sign up rate for growth campaign period
                
        Returns:
            campaign_shoe_club_join_prob (float): the join probability for users during campaign
            campaign_length (string): the length of the shoe club membership growth campaign
        
        """
        self.campaign_shoe_club_join_prob = rand.choice([0.25,0.26,0.30,0.35,0.40])
        self.campaign_length = 30
        return(self.campaign_shoe_club_join_prob, self.campaign_length)
    