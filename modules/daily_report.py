# -*- coding: utf-8 -*-
"""

@author: timpr
"""

import numpy as np
import matplotlib.pyplot as plt
import mysql.connector
from datetime import datetime

def produce_daily_report(mycursor, report_date):
    """
    Produces a html report for a particular date, summarizing sales 
    data and comparing to historical values 
    
    Parameters:
        mycursor (MySQL Cursor): a cursor to perform database operations from Python
        report_date (datetime): the date that the report is being run on.
        
    Returns:
        None
    
    """
    # Create a temporary table to store daily data for querying
    date_string = datetime.strftime(report_date, "%Y-%m-%d")
    mycursor.execute('''CREATE TABLE daily_summary AS 
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
                    	     events.event_date = "''' + date_string + '''"''')
        
    # Extract key output for the day
    # No. of clickthroughs
    mycursor.execute('''SELECT 
                         COUNT(event_date) 
                      FROM 
                          daily_summary 
                      WHERE 
                          event_type = "clickthrough"''')
    num_clickthroughs = mycursor.fetchall()[0][0]
    
    # No. of purchases
    mycursor.execute('''SELECT 
                            COUNT(event_date) 
                        FROM 
                            daily_summary 
                        WHERE 
                            event_type = "purchase"''')
    num_purchases = mycursor.fetchall()[0][0]
    
    purchase_conversion_rate = round(100*(num_purchases/num_clickthroughs),2)
    
    # Sales by brand
    mycursor.execute('''SELECT 
                          item_brand, 
                          SUM(item_price) 
                      FROM 
    	                  daily_summary 
                      WHERE 
                          event_type = 'purchase' 
                      GROUP BY 
    	                  item_brand''')
    brand_sales = mycursor.fetchall()

    # Calculate total daily revenue    
    total_revenue= 0
    for brand in brand_sales:
        total_revenue += brand[1]
    
    # Create pie chart breaking down sales by brand
    chart_name = "pie_chart.png"
    pie_chart = create_pie_chart(brand_sales, chart_name)
    
    # Generate HTML report summarizing results
    generate_html_report(pie_chart, 
                          num_clickthroughs, 
                          num_purchases, 
                          purchase_conversion_rate, 
                          total_revenue,
                          chart_name)
    
    # Delete temporary table to clean up database
    mycursor.execute("DROP TABLE daily_summary") 
        
    return

def create_pie_chart(brand_sales, chart_name):
    """
    Creates a pie chart with associated labeling for daily sales
    
    Parameters:
        brand_sales (List<Tuple<string, float>): a list of tuples, each tuple containing a brand name
                                                 and the total sales revenue for that brand
        chart_name (string): the name of the file to save the pie chart image to
        
    Returns:
        None
    
    """
    labels_list = []
    values_list = []
    
    for brand in brand_sales:
        labels_list.append(brand[0])
        values_list.append(brand[1])
 
    plt.pie(np.array(values_list), labels = labels_list)
    plt.savefig(chart_name)
    
    return


def generate_html_report(report_pie, num_clickthroughs, num_purchases, 
                         purchase_conversion_rate, total_revenue, chart_name):
    """
    Writes daily summary report to html
    
    Parameters:
        report_pie (PyPlot Pie Chart): a pie graph showing a breakdown of brand sales
        num_clickthroughs (int): the number of item clickthroughs for the day
        num_purchases (int): the number of item purchases for the day
        purchase_conversion_rate (float): the rate of customers purchasing items after clicking through
        total_revenue (float): the total sales revenue for the day
        chart_name (string): the filename of the pie chart associated with the daily report
    
    Returns:
        None
    
    """
        
    html_string = '''
                 <html>
                     <head>
                         <link rel = "stylesheet" href = "daily_rep_styles.css">
                         <title>Tim's Shoes Daily Report</title>
                     </head>
                     <body>
                         <div class = "topdiv">
                             <h1>Tim's Shoes</h1>
                             <p>Daily Summary Report<p>
                         </div>
                         <div>
                             <h3></h3>
                             <table class = "summarytable">
                                 <col style="width:50%">
            	                 <col style="width:50%">
                                 <tr>
                                     <th>CLICKTHROUGHS</th>
                                     <th>PURCHASES</th>
                                 </tr>                     
                                 <tr>
                                     <td>''' + str(num_clickthroughs) + '''</td>
                                     <td>''' + str(num_purchases) + '''</td>
                                 </tr>
                             </table>
                             <table class = "summarytable">
                                 <col style="width:50%">
            	                 <col style="width:50%">
                                 <tr>
                                     <th>CONVERSION RATE</th>
                                     <th>TOTAL REVENUE</th>
                                 </tr>                     
                                 <tr>
                                     <td>''' + str(round(purchase_conversion_rate,1)) + '''%</td>
                                     <td>$ ''' + str(round(total_revenue,2)) + '''</td>
                                 </tr>
                             </table>
                         </div>
                         <div class = "figure">
                             <img src = "''' + chart_name + '''" alt = "Pie Chart" 
                             style= "width:700px;height:450px;">
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
    
    css_file = open("daily_rep_styles.css", "w")
    css_file.write(css_string)
    html_file = open("daily_report.html", "w")
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
    produce_daily_report(mycursor, test_date)