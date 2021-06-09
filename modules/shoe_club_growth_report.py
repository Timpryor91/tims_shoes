# -*- coding: utf-8 -*-
"""

@author: timpr
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mysql.connector
from datetime import datetime, timedelta, date

def produce_shoe_club_growth_report(mycursor, camp_start_date, camp_end_date):
    """
    Produces a html report summarizing shoe club membership growth trends achieved by a 
    marketing campaign
    
    Parameters:
        mycursor (MySQL Cursor): a cursor to perform database operations from Python
        camp_start_date (datetime): the date that the marketing campaign started
        camp_end_date (datetime): the date that the marketing campaign finished
        
    Returns:
        None
    
    """
    campaign_length = (camp_end_date - camp_start_date).days
    
    # Extract data for dates surrounding the test for visual comparison
    day_range = 30
    plot_start_date = camp_start_date - timedelta(days = day_range)
    plot_start_date_string = datetime.strftime(plot_start_date, "%Y-%m-%d")
    plot_end_date = camp_end_date + timedelta(days = day_range)
    plot_end_date_string = datetime.strftime(plot_end_date, "%Y-%m-%d")
    
    # Determine the number of members at the plot start date
    mycursor.execute('''SELECT
                            COUNT(customer_id)
                        FROM
                            customers
                        WHERE
                            shoe_club_signup_date < "''' + plot_start_date_string + '''"
                        AND
                            shoe_club_status = "Active"    
                     ''')
    initial_members = mycursor.fetchall()[0][0]
    
    # Determine number of new customers added each day in the period of interest
    mycursor.execute('''SELECT 
                            shoe_club_signup_date,
                            COUNT(customer_id) 
                        FROM 
                  	        customers 
                        WHERE 
                            shoe_club_signup_date >= "''' + plot_start_date_string + '''" 
                        AND 
                            shoe_club_signup_date <= "''' + plot_end_date_string + '''" 
                        GROUP BY 
                            shoe_club_signup_date 
                        ORDER BY 
                            shoe_club_signup_date''')
    daily_members = mycursor.fetchall()
    
    # Construct a dictionary with the total number of customers on each day of the period of interest
    daily_members_dict = {}
    for day in daily_members:
        if (day[0] == plot_start_date.date()):
            daily_members_dict[day[0]] = day[1] + initial_members
        else:
            daily_members_dict[day[0]] = day[1] + daily_members_dict[day[0] - timedelta(days = 1)]
    
    # Determine average number of customers added during campaign
    avg_camp_new_membs = (daily_members_dict[camp_end_date.date()] - 
                          daily_members_dict[camp_start_date.date()]) / campaign_length
    
    # Determine average number of customers added in periods surrounding campaign
    pre_camp_new_membs = (daily_members_dict[camp_start_date.date() - timedelta(days = 1)] 
                          - daily_members_dict[plot_start_date.date()]) / day_range
    post_camp_new_membs = (daily_members_dict[plot_end_date.date()] 
                          - daily_members_dict[camp_end_date.date() + timedelta(days = 1)]) / day_range
    
    avg_non_camp_new_membs = (pre_camp_new_membs + post_camp_new_membs)/2
    
    # Create a plot showing the growth of customers in the period of interest
    plot_name = "shoe_club_growth_plots.png"
    create_growth_plot(daily_members_dict, plot_name, camp_start_date, camp_end_date)
    
    # Generate HTML report summarizing results
    generate_html_report(avg_camp_new_membs, avg_non_camp_new_membs, plot_name)
            
    return

def create_growth_plot(daily_customer_dict, plot_name, camp_start_date, camp_end_date):
    """
    Creates a plot showing the growth of total registered customers in the period around the customer
    growth marketing campaign
    
    Parameters:
        daily_customer_dict (Dict<datetime: int>): the number of clickthrough events for control group
        plot_name (string): the filename to save the plot under
        camp_start_date (datetime): the date that the marketing campaign went live
        camp_end_date (datetime): the date that the marketing campaign finished
        
    Returns:
        None
    
    """
    # Create lists for plot points
    plot_dates = []
    plot_vals = []
    for day in daily_customer_dict:
        plot_dates.append(day)
        plot_vals.append(daily_customer_dict[day])

    # Create plot    
    fig, ax = plt.subplots()
    ax.plot(plot_dates, plot_vals, marker = ".", markersize = 0.2, color = 'blue')
    # plt.plot(plot_dates, plot_vals, marker = ".", markersize = 0.2, color = 'blue')
    plt.xlabel('Date')
    plt.ylabel('Total Customers Registered')
    x_label_format = mdates.DateFormatter("%Y-%m-%d")
    ax.xaxis.set_major_formatter(x_label_format)
    
    # Create vertical lines to demarcate campaign period
    plt.vlines(camp_start_date.date(), 0.7*daily_customer_dict[camp_start_date.date()], 
               1.2*daily_customer_dict[camp_end_date.date()], linestyles = 'dashed', colors = "red")
    plt.vlines(camp_end_date.date(), 0.7*daily_customer_dict[camp_start_date.date()], 
               1.2*daily_customer_dict[camp_end_date.date()], linestyles = 'dashed', colors = "red")
    
    fig.autofmt_xdate()    
    plt.savefig(plot_name)
    
    return

def generate_html_report(avg_camp_new_custs, avg_non_camp_new_custs, plot_name):
    """
    Writes A/B test summary report to html
    
    Parameters:
        avg_camp_new_custs (float): the average number of new daily customers registering during the campaign
        avg_non_camp_new_custs (float): the average number of new daily customers registering outside of campaign
        plot_name (string): the filename of the plot chart associated with the campaign
    
    Returns:
        None
    
    """
        
    html_string = '''
                 <html>
                     <head>
                         <link rel = "stylesheet" href = "growth_test_styles.css">
                         <title>Tim's Shoes</title>
                     </head>
                     <body>
                         <div class = "topdiv">
                             <h1>Tim's Shoes</h1>
                             <p>Shoe Club Growth Campaign Report: ''' + str(camp_start_date.date()) + ''' - 
                             ''' + str(camp_end_date.date()) + '''<p>
                         </div>
                         <div>
                             <h3></h3>
                             <table class = "summarytable">
                                 <col style="width:50%">
            	                 <col style="width:50%">
                                 <tr>
                                     <th>MEMBERS ADDED DURING CAMPAIGN</th>
                                     <th>MEMBERS ADDED OUTSIDE OF CAMPAIGN</th>
                                 </tr>                     
                                 <tr>
                                     <td>''' + str(round(avg_camp_new_custs,2)) + ''' cust/day</td>
                                     <td>''' + str(round(avg_non_camp_new_custs,2)) + ''' cust/day</td>
                                 </tr>                            
                         </div>
                         <p></p>
                         <div class = "figure">
                             <img src = "''' + plot_name + '''" alt = "Growth Chart" 
                             style= "width:432px;height:288px;">
                             <p></p>
                         </div>
                     </body>
                 </html> 
                 '''
    
    css_string = '''                
                .topdiv {
                  /*Styling the top "header" for my page*/
                  border-top-style: solid;
                  border-bottom-style: solid;
                  border-color: black;
                  border-width: 1px;
                  padding-left: 5px;
                  font-family: "Courier New", Courier, monospace;
                  text-align: center;
                  vertical-aling: top;
                }
                
                h1 {
                  text-align: center;
                  color: black;
                }
                
                .summarytable {
                  margin-left: auto; 
                  margin-right: auto;
                  width: 60%;
                  text-align: center;
                  height: 100px;
                  border: 1px solid black;
                  border-collapse: collapse;
                  font-family: "Courier New", Courier, monospace;
                  font-size: 20px
                }
                
                .figure {
                  display: block;
                  margin-left: auto; 
                  margin-right: auto;
                  width: 30%;
                }
                
                '''
    
    css_file = open("growth_test_styles.css", "w")
    css_file.write(css_string)
    html_file = open("shoe_club_growth_report.html", "w")
    html_file.write(html_string)
    
    return

if __name__ == "__main__":
    mydb = mysql.connector.connect(host="localhost",
                                   user="root",
                                   password="Tt556677",
                                   database = "timsshoes",
                                   connection_timeout = 28800
                                   )    
    mycursor = mydb.cursor()
    camp_start_date = datetime.strptime('2020-01-01', "%Y-%m-%d")
    camp_end_date = camp_start_date + timedelta(days = 30)
    produce_shoe_club_growth_report(mycursor, camp_start_date, camp_end_date)