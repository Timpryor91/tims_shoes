# -*- coding: utf-8 -*-
"""

@author: timpr
"""
from datetime import datetime, timedelta
import random as rand

class EventsTable(object):
    """
    An event table class, corresponding to a MySQL table used to store events on Tim's Shoes website
    
    """
    def __init__(self, mycursor, start_date, customer_table):
        """
        Initialize an EventsTable object 
        
        Parameters:
            mycursor (MySQL Cursor): a cursor to perform database operations from Python
            start_date (datetime): the date the website went live
            
        """
        self.mycursor = mycursor
        self.date = start_date
        self.end_date = datetime.today()
        self.customer_table = customer_table
        self.event_list = []
        
        # Create list of item ids
        self.mycursor.execute('''SELECT 
                                   item_id 
                               FROM 
                                   items 
                               WHERE 
                                   availability = "Available"
                            ''')
        
        self.item_ids = self.mycursor.fetchall()
        
        self.device_dict = {"computer" : ["dell", "hp", "apple", "lenovo", 
                                          "microsoft", "asus", "asus", "other"],
                            "phone":    ["apple", "google", "huawei", "samsung", "htc",
                                         "nokia", "motorola", "other"],
                            "tablet":   ["apple", "amazon", "microsoft", "other"]
                            }
        
        # Initiate bug detail variables
        self.bug_impacted_device_type = None
        self.bug_impacted_info = None
        
        # Base query to add events to the MySQL table
        self.sql = '''INSERT INTO events (event_date, event_time, event_type, customer_id,
                    product_id, device_type, device_info, ab_test_notes) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
        
        self.day_counter = 0
        # Randomly create events for each day
        while self.date < self.end_date:
            self.day_counter += 1
            
            # Determine number of customers currently signed up to site
            self.date_string = datetime.strftime(self.date, "%Y-%m-%d")
            self.mycursor.execute('''SELECT 
                                      customer_id 
                                   FROM 
                                      customers 
                                   WHERE 
                                      signup_date <= '" + self.date_string + "' 
                                   ORDER BY 
                                      signup_date DESC''')
            
            self.customer_ids = self.mycursor.fetchall()
            self.num_customers = len(self.customer_ids)
           
            # Run customer growth marketing campaigns approximately every six months
            if self.day_counter % 180 == 0:
                self.customer_table.run_customer_growth_campaign(self.date, self.num_customers)
            
            # Run a new A/B test every month
            if (self.day_counter - 1) % 30 == 0:
                self.ab_test_name, self.click_multiplier, self.conv_multiplier = self.create_ab_test(self.day_counter)            

            # Intermittently introduce bugs impacting on sales in the website
            self.bug_event_stopped = None
            if rand.random() < 0.005:
                self.bug_event_stopped, 
                self.bug_impacted_device_type, 
                self.bug_impacted_info = self.create_bug()
            
            # Randomly generate click data     
            for customer in self.customer_ids:
                
                # Assume 10% of the customers will recieve A/B test change
                # Adjust base likelihoods for customers exposed to A/B test changes
                self.click_through_factor = rand.random()
                self.conv_factor = rand.random()
                if rand.random() <= 0.1:
                    self.click_through_factor *= self.click_multiplier
                    self.conv_factor *= self.conv_multiplier
                    self.ab_test_notes = self.ab_test_name
                else:
                    self.ab_test_notes = ""
                
                # Assume 5% of registered customers as a baseline clickthrough to an item on the day
                if self.click_through_factor > 0.95:
                    self.viewed_product = rand.choice(self.item_ids)[0]
                    self.event_time = self.generate_event_time(None)
                    self.device_type = rand.choice(["computer", "phone", "tablet"])
                    self.device_info = rand.choice(self.device_dict[self.device_type])

                    # Check for clickthrough bug impacts
                    if self.bug_event_stopped == "clickthrough":
                        if self.device_type == self.bug_impacted_device_type:
                            if self.device_info in self.bug_impacted_info:
                                continue
                    
                    # Add clickthrough event to database table list
                    self.event_list.append((self.date,
                                            self.event_time,
                                            "clickthrough",
                                            customer[0],
                                            self.viewed_product,
                                            self.device_type,
                                            self.device_info,
                                            self.ab_test_notes))
                    
                    # Assume 40% of customers purchase items after clickthrough as a baseline
                    if self.conv_factor > 0.6:
                        self.purchase_time = self.generate_event_time(self.event_time)
                        
                        # Check for purchase bug impacts
                        if self.bug_event_stopped == "purchase":
                            if self.device_type == self.bug_impacted_device_type:
                                if self.device_info in self.bug_impacted_info:
                                    continue
                        
                        self.event_list.append((self.date,
                                           self.purchase_time,
                                           "purchase",
                                           customer[0],
                                           self.viewed_product,
                                           self.device_type,
                                           self.device_info,
                                           self.ab_test_notes))            
            
            # Add the days items to the event list and reset the list to avoid double counts
            self.mycursor.executemany(self.sql, self.event_list) 
            self.event_list = []
            
            self.date += timedelta(days = 1)
  
    
    def create_ab_test(self, day_counter):
        """
        Runs an A/B test with the aim of increasing click events, or increasing sales
        conversions from click events.
        
        Parameters:
            day_counter (int): the number of days since the website went live
            
        Returns:
            test_name (string): the name of the current A/B test
            click_multiplier (float): the multiplier of click rate to use in the test
            conversion_multiplier (float): the multiplier of the conversion rate to use in the test
        
        """
        # Test name
        self.test_name = "A/B Test " + str(1 + (day_counter - 1) % 30)
        
        # Select test type
        self.test_type = rand.choice(["click_increase", "conversion_increase"])
        
        # Randomly choose parameters dictating the effectivness of the alternative tested
        if self.test_type == "click_increase":
            self.click_multiplier = 1 + rand.random()/5
            self.conversion_multiplier = 1
        elif self.test_type == "conversion_increase":
            self.click_multiplier = 1
            self.conversion_multiplier = 1 + rand.random()/3
        
        return(self.test_name, self.click_multiplier, self.conversion_multiplier)
    
    def create_bug(self):
        """
        Creates a bug that prevents clicks or sales on certain devices. Bugs are assumed to be
        resolved within a day
        
        Parameters:
            None
        
        Return:
            event_stopped (string): the event type that is impacted by the bug (clickthrough or purchase)
            impacted_device_type (string): the device type that is impacted by the bug
            impacted_device_info (List<string>): the particular devices that are impacted by the bug
        
        """
        
        self.event_stopped = rand.choice(["clickthrough", "purchase"])        
        self.impacted_device_type = rand.choice(["computer", "phone", "tablet"])
        
        # Randomly select the device type variants that will be impacted
        self.variants_impacted = rand.randint(1, len(self.device_dict[self.impacted_device_type]))
        self.impacted_device_info = rand.sample(self.device_dict[self.impacted_device_type], 
                                                self.variants_impacted )
        
        return (self.event_stopped, self.impacted_device_type, self.impacted_device_info)
    
    def generate_event_time(self, click_time):
        """
        Generates a random time for an event.
        
        Parameters:
            click_time (string): For a purchase event, the time (HH:MM:SS) that the item was clicked into. 
                                 None for click events
            
        Returns:
            event_time (string): An event time string in the form HH:MM:SS
        
        """
        
        self.click_time = click_time
        # Choose a random day time for a click event
        if click_time is None:
            self.event_datetime = datetime.today() + timedelta(hours = rand.randint(0,24)) +\
                                  timedelta(minutes = rand.randint(0,60))
            self.event_time = datetime.strftime(self.event_datetime,"%H:%M:%S")
        # For a purchase event, add on a small amount of time after the corresponding click event
        else:
            self.event_datetime = datetime.strptime(self.click_time, "%H:%M:%S") +\
                                  timedelta(minutes = rand.randint(0,60))
            self.event_time = datetime.strftime(self.event_datetime, "%H:%M:%S")
                    
        return(self.event_time)