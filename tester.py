# -*- coding: utf-8 -*-
"""

@author: timpr
"""

import mysql.connector
from datetime import datetime, timedelta
import random as rand
import numpy as np

import matplotlib.pyplot as plt
import scipy.stats as scs

# from modules.initiate_tables import initiate_base_tables
# from classes.customer_class import CustomerTable
# from classes.event_class import EventsTable
# from classes.item_class import ItemTable


if __name__ == "__main__":
    
   
    plot_vals1 = []
    for i in range(500, 700):
        plot_vals1.append(i)

    plot_vals2 = []
    for i in range(1100, 1300):
        plot_vals2.append(i)

    # list of pmf values
    dist1 = [scs.binom.pmf(r, 1000, 0.6) for r in plot_vals1]
    dist2 = [scs.binom.pmf(r, 2000, 0.6) for r in plot_vals2]
    
    plot_vals3 = []
    for val in plot_vals1:
        plot_vals3.append(val/10)
        
    plot_vals4 = []
    for val in plot_vals2:
        plot_vals4.append(val/20)
    
    plot_chart_1 = plt.bar(plot_vals3, dist1)
    plot_chart_2 = plt.bar(plot_vals4, dist2)
    
    plt.show()
    # x = np.linspace(0, 1000, 100)
    # y = scs.binom(1000, 0.5).pmf(x)
    # # ax.bar(x, y, alpha=0.5)
    # # ax.axvline(x=B_cr * A_total, c='blue', alpha=0.75, linestyle='--')
    # plt.xlabel('conversion rate')
    # plt.ylabel('probability')
  
