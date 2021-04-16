# -*- coding: utf-8 -*-
"""

@author: timpr
"""
import matplotlib.pyplot as plt
import scipy.stats as scs
import mysql.connector
from datetime import datetime, timedelta

def produce_abtest_report(mycursor, test_start_date, test_end_date):
    """
    Produces a html report summarizing the results of an A/B test
    
    Parameters:
        mycursor (MySQL Cursor): a cursor to perform database operations from Python
        test_start_date (datetime): the date that the A/B test of interest started on
        test_end_date (datetime): the date that the A/B test of interest finished
        
    Returns:
        None
    
    """
    # Create a temporary table to store data for querying
    start_date_string = datetime.strftime(test_start_date, "%Y-%m-%d")
    end_date_string = datetime.strftime(test_end_date, "%Y-%m-%d")
    mycursor.execute('''CREATE TABLE ab_test_summary AS 
                          SELECT 
                    	      event_date, 
                              event_type, 
                              product_id, 
                              device_type, 
                              device_info, 
                              ab_test_notes 
                          FROM 
                    	     events 
                          WHERE 
                    	     event_date >= '" + start_date_string + "' 
                          AND 
                             event_date <= "''' + end_date_string + '''"''')
    
    # Test name
    mycursor.execute('''SELECT 
                          ab_test_notes 
                      FROM 
                          ab_test_summary 
                      WHERE 
                          ab_test_notes != '' 
                      LIMIT 1''')
    test_name = mycursor.fetchall()[0][0]   
    
    # Total clickthroughs during test
    mycursor.execute('''SELECT 
                          COUNT(event_date) 
                      FROM 
                          ab_test_summary 
                      WHERE 
                          event_type = "clickthrough"''')
    num_tot_clickthroughs = mycursor.fetchall()[0][0]

    # Total clickthroughs for users exposed to A/B test
    mycursor.execute('''SELECT 
                          COUNT(event_date) 
                      FROM 
                          ab_test_summary 
                      WHERE 
                          event_type = 'clickthrough' 
                      AND 
                          ab_test_notes != ""''')
    num_test_clickthroughs = mycursor.fetchall()[0][0]
    num_nontest_clickthroughs = num_tot_clickthroughs - num_test_clickthroughs
    
    # Total purchases during test
    mycursor.execute('''SELECT 
                          COUNT(event_date) 
                      FROM 
                          ab_test_summary 
                      WHERE 
                          event_type = "purchase"''')
    num_tot_purchases = mycursor.fetchall()[0][0]    
     
    # Total purchases for users exposed to A/B test
    mycursor.execute('''SELECT \
                          COUNT(event_date) 
                      FROM 
                          ab_test_summary 
                      WHERE 
                          event_type = 'purchase' 
                      AND 
                          ab_test_notes != ""''')
    num_test_purchases = mycursor.fetchall()[0][0]                   
    num_nontest_purchases = num_tot_purchases - num_test_purchases
    
    # Calculate test statistics
    # Refer to https://en.wikipedia.org/wiki/Statistical_hypothesis_testing
    pA = num_nontest_purchases / num_nontest_clickthroughs
    pB = num_test_purchases / num_test_clickthroughs
    nA = num_test_clickthroughs
    nB = num_nontest_clickthroughs
    p_hat = (nA*pA + nB*pB)/(nA + nB) 
    z = (pA - pB)/(p_hat*(1-p_hat)*((1/nA) + (1/nB)))**0.5
    
    # Determine if null hypothesis can be rejected (meaning test shows statistically significant improvement)
    if abs(z) > 1.96:
        test_outcome = "Adopt test change"
    else:
        test_outcome = "Test inconclusive"
    
    # Create a plot showing the distributions of the control group and test group
    plot_name = "distribution_plots.png"
    create_distribution_plots(nA, nB, pA, pB, plot_name)
    
    # Generate HTML report summarizing results
    generate_html_report(pA, pB, nA, nB, z, test_outcome, test_name, plot_name)
    
    # Delete temporary table to clean up database
    mycursor.execute("DROP TABLE ab_test_summary") 
        
    return

def create_distribution_plots(nA, nB, pA, pB, plot_name):
    """
    Creates a plot showing the presumed distribution of likely conversion rates for the test group
    compared with the likely distribution of the control group.
    
    Parameters:
        nA (int): the number of clickthrough events for control group
        nB (int): the number of clickthrough events for users exposed to test
        pA (float): the proportion of users from control group purchasing items after clickthrough
        pB (float): the proportion of users from the test group purchasing items after clickthrough
        
    Returns:
        None
    
    """
    # Calculate ranges to determine binomial distribution values for
    a_calc_vals = []
    for i in range(int(pA*nA) - int(0.1*pA*nA), int(pA*nA) + int(0.1*pA*nA), 1):
        a_calc_vals.append(i)
   
    b_calc_vals = []
    for i in range(int(pB*nB) - int(0.1*pB*nB), int(pB*nB) + int(0.1*pB*nB), 1):
        b_calc_vals.append(i)
    
    # Determine probabilities based on binomial pmf
    a_dist = [scs.binom.pmf(r, nA, pA) for r in a_calc_vals]
    b_dist = [scs.binom.pmf(r, nB, pB) for r in b_calc_vals]
    
    # Convert frequency of occurence values into conversion percentages
    a_plot_vals = []
    for val in a_calc_vals:
        a_plot_vals.append(100*val/nA)
    
    b_plot_vals = []
    for val in b_calc_vals:
        b_plot_vals.append(100*val/nB)
    
    # Generate plots for data
    plt.bar(a_plot_vals, a_dist, width = 0.1, color = "red")
    plt.bar(b_plot_vals, b_dist, width = 0.1, color = "blue")
    
    # Create legend
    legend_colors = {"Control Group": "red", "Test Group": "blue"}
    legend_labels = list(legend_colors.keys())
    legend_handles = [plt.Rectangle((0,0),1,1, color = legend_colors[label]) for label in legend_labels]
    plt.legend(legend_handles, legend_labels)
    
    # Add axis labels
    plt.xlabel('Conversion Rate')
    plt.ylabel('Probability')
    
    plt.savefig(plot_name)
    
    return

def generate_html_report(pA, pB, nA, nB, z, test_outcome, test_name, plot_name):
    """
    Writes A/B test summary report to html
    
    Parameters:
        nA (int): the number of clickthrough events for control group
        nB (int): the number of clickthrough events for users exposed to test
        pA (float): the proportion of users from control group purchasing items after clickthrough
        pB (float): the proportion of users from the test group purchasing items after clickthrough
        z (float): the z score for the test
        test_outcome (string): the conclusion drawn from the test
        test_name (string): the name of the active A/B test
        plot_name (string): the filename of the plot chart associated with the test
    
    Returns:
        None
    
    """
        
    html_string = '''
                 <html>
                     <head>
                         <link rel = "stylesheet" href = "ab_test_styles.css">
                         <title>Tim's Shoes</title>
                     </head>
                     <body>
                         <div class = "topdiv">
                             <h1>Tim's Shoes</h1>
                             <p>A/B Test Report - ''' + str(test_name) + '''<p>
                         </div>
                         <div>
                             <h3></h3>
                             <table class = "summarytable">
                                 <col style="width:50%">
            	                 <col style="width:50%">
                                 <tr>
                                     <th>CONTROL GROUP TEST SAMPLE SIZE</th>
                                     <th>TEST GROUP SAMPLE SIZE</th>
                                 </tr>                     
                                 <tr>
                                     <td>''' + str(nA) + '''</td>
                                     <td>''' + str(nB) + '''</td>
                                 </tr>
                             </table>
                             <table class = "summarytable">
                                 <col style="width:50%">
            	                 <col style="width:50%">
                                 <tr>
                                     <th>CONTROL GROUP CONVERSION RATE</th>
                                     <th>TEST GROUP CONVERSION RATE</th>
                                 </tr>                     
                                 <tr>
                                     <td>''' + str(round(pA,4)) + '''%</td>
                                     <td>''' + str(round(pB,4)) + '''%</td>
                                 </tr>
                             </table>
                             <table class = "summarytable">
                                 <col style="width:50%">
            	                 <col style="width:50%">
                                 <tr>
                                     <th>TEST Z SCORE (|z|)</th>
                                     <th>TEST OUTCOME RECOMMENDATION</th>
                                 </tr>                     
                                 <tr>
                                     <td>''' + str(round(abs(z),3)) + '''</td>
                                     <td>''' + str(test_outcome) + '''</td>
                                 </tr>
                             </table>                             
                         </div>
                         <div class = "figure">
                             <img src = "''' + plot_name + '''" alt = "Dist Chart" 
                             style= "width:1000px;height:500px;">
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
                  width: 23%;
                }
                
                '''
    
    css_file = open("ab_test_styles.css", "w")
    css_file.write(css_string)
    html_file = open("ab_test_report.html", "w")
    html_file.write(html_string)
    
    return


mydb = mysql.connector.connect(host="localhost",
                               user="root",
                               password="Tt556677",
                               database = "timsshoes",
                               connection_timeout = 28800
                               )    
mycursor = mydb.cursor()

test_start_date = datetime.strptime('2020-08-01', "%Y-%m-%d")
test_end_date = test_start_date + timedelta(days = 30)

produce_abtest_report(mycursor, test_start_date, test_end_date)