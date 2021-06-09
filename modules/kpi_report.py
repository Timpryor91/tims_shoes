# -*- coding: utf-8 -*-
"""

@author: timpr
"""

import mysql.connector
from datetime import datetime, timedelta

def produce_kpi_snapshot_report(mycursor, report_date):
    """
    Produces a html report for a particular date summarizing kpis  
    
    Parameters:
        mycursor (MySQL Cursor): a cursor to perform database operations from Python
        report_date (datetime): the date that the report is being run on.
        
    Returns:
        None
    
    """
    # mycursor.execute("DROP TABLE weekly_events, monthly_events")     
    
    # Create a temporary table to store daily data for querying
    current_date_string = datetime.strftime(report_date, "%Y-%m-%d")
    previous_week_string = datetime.strftime(report_date - timedelta(days = 7), "%Y-%m-%d")
    previous_month_string = datetime.strftime(report_date - timedelta(days = 30), "%Y-%m-%d")
    mycursor.execute('''CREATE TABLE weekly_events AS 
                          SELECT 
                    	      events.event_date AS event_date, 
                              events.event_type AS event_type, 
                              events.product_id AS product_id, 
                              items.item_price AS item_price, 
                              items.item_brand AS item_brand 
                          FROM 
                    	      events 
                          INNER JOIN 
                	          items 
                          ON 
                    	      events.product_id = items.item_id 
                          WHERE 
                    	      events.event_date > "''' + previous_week_string + '''"
                          AND
                              events.event_date <= "''' + current_date_string + '''"''')
    
    mycursor.execute('''CREATE TABLE monthly_events AS 
                          SELECT 
                    	      events.event_date AS event_date, 
                              events.event_type AS event_type, 
                              events.product_id AS product_id, 
                              items.item_price AS item_price, 
                              items.item_brand AS item_brand 
                          FROM 
                    	      events 
                          INNER JOIN 
                	          items 
                          ON 
                    	      events.product_id = items.item_id 
                          WHERE 
                    	      events.event_date > "''' + previous_month_string + '''"
                          AND
                              events.event_date <= "''' + current_date_string + '''"''')        
    
    # Weekly succesful orders
    mycursor.execute('''SELECT 
                         COUNT(event_date) 
                      FROM 
                          weekly_events 
                      WHERE 
                          event_type = "purchase"''')
    weekly_successful_orders = mycursor.fetchall()[0][0]
    
    # Weekly average order value
    mycursor.execute('''SELECT 
                            SUM(item_price) 
                        FROM 
                            weekly_events
                        WHERE 
                            event_type = "purchase"''')
    weekly_average_order = mycursor.fetchall()[0][0] / weekly_successful_orders
        
    # Monthly conversion rate
    mycursor.execute('''SELECT 
                          COUNT(*) 
                      FROM 
    	                  monthly_events 
                      WHERE 
                          event_type = "clickthrough"''')
    monthly_clicks = mycursor.fetchall()[0][0]
    mycursor.execute('''SELECT 
                          COUNT(*) 
                      FROM 
    	                  monthly_events 
                      WHERE 
                          event_type = "purchase"''')
    monthly_conversion = mycursor.fetchall()[0][0] / monthly_clicks   

    # Monthly shoe club members
    mycursor.execute('''SELECT 
                          COUNT(*) 
                      FROM 
    	                  customers 
                      WHERE 
                          shoe_club_signup_date > "''' + previous_month_string + '''" 
                      AND
                          shoe_club_signup_date <= "''' + current_date_string + '''"''')    
    monthly_shoe_members = mycursor.fetchall()[0][0]
    image_name = "kpi_image.png"
    
    # Generate HTML report summarizing results
    generate_html_report(weekly_successful_orders,
                          weekly_average_order, 
                          monthly_conversion, 
                          monthly_shoe_members,
                          image_name) 
    
    # Delete temporary tables to clean up database
    mycursor.execute("DROP TABLE weekly_events, monthly_events") 
    
    
    return


def generate_html_report(weekly_successful_orders, weekly_average_order, 
                         monthly_conversion, monthly_shoe_members, image_name):
    """
    Writes daily summary report to html
    
    Parameters:
        weekly_successful_orders (int): the number of succesful orders in the past week
        weekly_average_order (float): the average value of order in the past week
        monthly_conversion (float): the purchase conversion rate over the past month
        monthly_shoe_members (int): the number of new shoe club members in the past month
        image_name (string): the filename of the image for the report
    
    Returns:
        None
    
    """
        
    html_string = '''
                 <html>
                     <head>
                         <link rel = "stylesheet" href = "kpi_snapshot_styles.css">
                         <title>Tim's Shoes Daily Report</title>
                     </head>
                     <body>
                         <div class = "topdiv">
                             <h1>Tim's Shoes</h1>
                             <p>KPI Snapshot Report<p>
                         </div>
                         <div>
                             <h3></h3>
                             <table class = "summarytable">
                                 <col style="width:50%">
            	                 <col style="width:50%">
                                 <tr>
                                     <th>WEEKLY SUCCESSFUL ORDERS</th>
                                     <th>WEEKLY AVERAGE ORDER VALUE</th>
                                 </tr>                     
                                 <tr>
                                     <td>''' + str(weekly_successful_orders) + '''</td>
                                     <td>$ ''' + str(round(weekly_average_order,1)) + '''</td>
                                 </tr>
                             </table>
                             <table class = "summarytable">
                                 <col style="width:50%">
            	                 <col style="width:50%">
                                 <tr>
                                     <th>MONTHLY CONVERSION RATE</th>
                                     <th>MONTHLY NEW SHOE CLUB MEMBERS</th>
                                 </tr>                     
                                 <tr>
                                     <td>''' + str(100*round(monthly_conversion,1)) + '''%</td>
                                     <td>''' + str(monthly_shoe_members) + '''</td>
                                 </tr>
                             </table>
                         </div>
                         <div class = "figure">
                             <img src = "''' + image_name + '''" alt = "Running Pic" 
                             style= "width:500px;height:500px;">
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
                  width: 35%;
                }
                
                '''
    
    css_file = open("kpi_snapshot_styles.css", "w")
    css_file.write(css_string)
    html_file = open("kpi_snapshot_report.html", "w")
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
    
    test_date = datetime.strptime('2020-06-03', "%Y-%m-%d")
    produce_kpi_snapshot_report(mycursor, test_date)