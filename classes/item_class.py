# -*- coding: utf-8 -*-
"""

@author: timpr
"""

class ItemTable(object):
    """
    An item table class, corresponding to a MySQL table used to store customer details on Tim's Shoes website
    
    """
    def __init__(self, mycursor):
        """
        Initialize an ItemTable object 
        
        Parameters:
            mycursor (MySQL Cursor): a cursor to perform database operations from Python
    
        """  
        self.mycursor = mycursor
        
        self.product_list = [
                            ("Wave Rider 24", "129.95", "Available", "Mizuno", "running - training"),
                            ("Wave Rider 24 Waveknit", "129.95", "Available", "Mizuno", "running - training"),
                            ("Inspire 17 Waveknit", "134.95", "Available", "Mizuno", "running - training"),
                            ("Wave Sky Waveknit 4", "159.95", "Available", "Mizuno", "running - training"),
                            ("Wave Horizon 5", "159.95", "Available", "Mizuno", "running - training"),
                            ("Ultra Boost 21", "179.95", "Available", "Adidas", "running - training"),
                            ("SL20", "120.00", "Available", "Adidas", "running - training"),
                            ("Adizero Adios Pro", "199.95", "Available", "Adidas", "running - racing"),
                            ("Adizero Boston 9", "119.95", "Available", "Adidas", "running - racing"),
                            ("XCS Men's Spikes", "50.00", "Available", "Adidas", "track and field"),
                            ("Adizero HJ Unisex Spikes", "99.95", "Available", "Adidas", "track and field"),
                            ("Jumpstar Unisex Spikes", "64.95", "Available", "Adidas", "track and field"),
                            ("Adizero LJ Unisex Spikes", "109.95", "Available", "Adidas", "track and field"),
                            ("Adizero TJ/PV Unisex Spikes", "109.95", "Available", "Adidas", "track and field"),
                            ("Adizero Javelin Unisex", "109.95", "Available", "Adidas", "track and field"),
                            ("Throwstar Unisex Throw Shoes", "64.95", "Available", "Adidas", "track and field"),
                            ("SprintStar Men's Spikes", "64.95", "Available", "Adidas", "track and field"),
                            ("Adizero MD Unisex Spikes", "109.95", "Available", "Adidas", "track and field"),
                            ("DistanceStar Men's Spikes", "64.95", "Available", "Adidas", "track and field"),
                            ("Finesse Unisex Spikes", "109.95", "Available", "Adidas", "track and field"),
                            ("Adizero Avanti Men's Spikes", "45.95", "Available", "Adidas", "track and field"),
                            ("Hyper Speed", "89.95", "Available", "ASICS", "running - racing"),
                            ("Gel Kayano Lite", "159.95", "Available", "ASICS", "running - training"),
                            ("Novablast", "129.95", "Available", "ASICS", "running - training"),
                            ("Gel Kayano 27", "159.95", "Available", "ASICS", "running - training"),
                            ("Gel Nimbus 23", "149.95", "Available", "ASICS", "running - training"),
                            ("Metaspeed Sky", "249.95", "Available", "ASICS", "running - racing"),
                            ("Gel Nimbus Lite 2", "149.95", "Available", "ASICS", "running - training"),
                            ("Gel Cumulus 22", "119.95", "Available", "ASICS", "running - training"),
                            ("GT 2000 9 Knit", "119.95", "Available", "ASICS", "running - training"),
                            ("Magic Speed", "149.95", "Unavailable", "ASICS", "running - racing"),
                            ("EvoRide 2", "119.95", "Available", "ASICS", "running - training"),
                            ("Dynablast", "109.95", "Available", "ASICS", "running - training"),
                            ("Trabuco Max", "129.95", "Available", "ASICS", "running - training"),
                            ("Noosa Tri", "129.95", "Available", "ASICS", "running - racing"),
                            ("Hypersprint 7 Spikes", "64.95", "Available", "ASICS", "track and field"),
                            ("Javelin Pro 2", "139.95", "Available", "ASICS", "track and field"),
                            ("High Jump Pro 2", "109.95", "Available", "ASICS", "track and field"),
                            ("Hyper MD 7 Spikes", "64.95", "Available", "ASICS", "track and field"),
                            ("Throw Pro 2", "99.95", "Available", "ASICS", "track and field"),
                            ("Hyperion Tempo", "149.95", "Available", "Brooks", "running - training"),
                            ("Adrenaline GTS 21", "129.95", "Available", "Brooks", "running - training"),
                            ("Launch 8", "99.95", "Available", "Brooks", "running - training"),
                            ("Glycerin 19", "149.95", "Available", "Brooks", "running - training"),
                            ("Hyperion Elite 2", "249.95", "Available", "Brooks", "running - racing"),
                            ("Ghost 13", "129.95", "Available", "Brooks", "running - training"),
                            ("QW-K v4 Spikes", "119.95", "Available", "Brooks", "track and field"),
                            ("ELMN8 v5 Spikes", "119.95", "Available", "Brooks", "track and field"),
                            ("Wire v6 Spikes", "119.95", "Available", "Brooks", "track and field"),
                            ("Mach 19 Spikes", "69.95", "Available", "Brooks", "track and field"),
                            ("Rocket X", "179.95", "Available", "HOKA ONE ONE", "running - training"),
                            ("Clifton 7", "129.95", "Available", "HOKA ONE ONE", "running - training"),
                            ("Arahi 5", "129.95", "Available", "HOKA ONE ONE", "running - training"),
                            ("Speedgoat 4", "144.95", "Available", "HOKA ONE ONE", "running - training"),
                            ("Torrent 2", "119.95", "Available", "HOKA ONE ONE", "running - training"),
                            ("Rincon 2", "114.95", "Available", "HOKA ONE ONE", "running - training"),
                            ("Bondi 7", "149.95", "Available", "HOKA ONE ONE", "running - training"),
                            ("Clifton 7", "129.95", "Available", "HOKA ONE ONE", "running - training"),
                            ("Fresh Foam Beacon 3", "119.95", "Available", "New Balance", "running - training"),
                            ("FuelCell Prism", "119.95", "Available", "New Balance", "running - racing"),
                            ("Fresh Foam Hierro 5", "100.95", "Available", "New Balance", "running - training"),
                            ("Fresh Foam 880 10", "99.95", "Available", "New Balance", "running - racing"),
                            ("FuelCell Rebel", "129.95", "Available", "New Balance", "running - training"),
                            ("FuelCell Propel 2", "99.95", "Available", "New Balance", "running - training"),
                            ("Fresh Foam 1080 11", "149.95", "Available", "New Balance", "running - training"),
                            ("1400 6", "99.95", "Available", "New Balance", "running - racing"),
                            ("XC Seven 3 Spikes", "49.95", "Available", "New Balance", "track and field"),
                            ("XC Seven 3 Spikeless", "49.95", "Available", "New Balance", "track and field"),
                            ("XC5K Spikes", "64.95", "Available", "New Balance", "track and field"),
                            ("LD5K Spikes", "119.95", "Available", "New Balance", "track and field"),
                            ("MD500 7 Spikes", "69.95", "Available", "New Balance", "track and field"),
                            ("MD800 7 Spikes", "119.95", "Available", "New Balance", "track and field"),
                            ("SD100 3 Spikes", "69.95", "Available", "New Balance", "track and field"),
                            ("Sigma Harmony 2 Spikes", "164.95", "Available", "New Balance", "track and field"),
                            ("Vazee Verge Spikes", "39.95", "Available", "New Balance", "track and field"),
                            ("Pegasus 37", "99.95", "Available", "Nike", "running - training"),
                            ("Infinity Run Flyknit 2", "159.95", "Available", "Nike", "running - training"),
                            ("Terra Kiger 7", "139.95", "Available", "Nike", "running - training"),
                            ("Alphafly Next%", "274.95", "Available", "Nike", "running - racing"),
                            ("Vaporfly Next%", "249.95", "Available", "Nike", "running - racing"),
                            ("Invincible Flyknit", "179.95", "Available", "Nike", "running - training"),
                            ("Zoom Tempo Next% Flyknit", "199.95", "Available", "Nike", "running - racing"),
                            ("Wildhorse", "129.95", "Available", "Nike", "running - training"),
                            ("React Miller", "104.95", "Available", "Nike", "running - training"),
                            ("Superfly Elite 2 Flyknit", "149.95", "Available", "Nike", "track and field"),
                            ("Dragonfly", "149.95", "Available", "Nike", "track and field"),
                            ("Zoom Victory", "179.95", "Available", "Nike", "track and field"),
                            ("Zoom Rival XC", "49.95", "Available", "Nike", "track and field"),
                            ("Zoom Rival Waffle", "49.95", "Available", "Nike", "track and field"),
                            ("Zoom Ja Fly 3", "124.95", "Available", "Nike", "track and field"),
                            ("Zoom Mamba 5", "124.95", "Available", "Nike", "track and field"),
                            ("Zoom Rotational 6", "99.95", "Available", "Nike", "track and field"),
                            ("Zoom Javelin Elite 3", "149.95", "Available", "Nike", "track and field"),
                            ("Pole Vault Elite", "39.95", "Available", "Nike", "track and field"),
                            ("High Jump Elite", "149.95", "Available", "Nike", "track and field")
                            ]
                  
        self.sql = '''INSERT INTO items (item_name, item_price, availability, item_brand, item_type) 
                    VALUES (%s, %s, %s, %s, %s)'''
        
        # Insert values into customer table        
        self.mycursor.executemany(self.sql, self.product_list)  
        
