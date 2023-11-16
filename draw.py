import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np  # Import the numpy library

def autopct_func(pct, allvalues):
    absolute = int(pct/100.*np.sum(allvalues))
    return "{:.1f}%\n({:d} counts)".format(pct, absolute)

def draw_pie_chart(db_name):
    # Connect to the existing database
    connection = sqlite3.connect(db_name)
    
    # Query the database to get the count of each unique value in the 'Technology' column
    query = "SELECT Technology, COUNT(*) FROM merged_currentvins GROUP BY Technology;"
    df = pd.read_sql_query(query, connection)
    
    # Close the connection to the database
    connection.close()
    
    # Plotting the pie chart
    plt.figure(figsize=(10, 10))
    plt.pie(df['COUNT(*)'], labels=df['Technology'], autopct=lambda pct: autopct_func(pct, df['COUNT(*)']), startangle=140)
    plt.title('Distribution of Technologies')
    
    # Save the pie chart to a .png file
    plt.savefig('pie_chart.png')

def draw_bar_chart(db_name):
    # Connect to the existing database
    connection = sqlite3.connect(db_name)
    
    # Query the database to get the count of each unique value in the 'Vehicle Name' column
    query = "SELECT [Vehicle Name], COUNT(*) FROM merged_currentvins GROUP BY [Vehicle Name];"
    df = pd.read_sql_query(query, connection)
    
    # Close the connection to the database
    connection.close()
    
    # Sort the DataFrame based on the count, in descending order
    df = df.sort_values(by='COUNT(*)', ascending=False)
    
    # Plotting the bar chart
    plt.figure(figsize=(15, 10))
    plt.bar(df['Vehicle Name'], df['COUNT(*)'], width=0.8)
    plt.xticks(rotation=90, fontsize=8)  # Rotate labels and reduce font size for better visibility
    plt.yticks(fontsize=10)
    plt.title('Count of Vehicles by Name', fontsize=14)
    plt.xlabel('Vehicle Name', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    
    # Adjust spacing between data points
    plt.tight_layout()
    
    # Save the bar chart to a .png file
    plt.savefig('bar_chart.png')

def draw_stacked_bar_chart(db_name):
    # Connect to the existing database
    connection = sqlite3.connect(db_name)

    # Query the database to get the count of each unique vehicle name for each model year
    query = """
    SELECT [Vehicle Name], "MODEL-YEAR" AS ModelYear, COUNT(*) AS count
    FROM merged_currentvins
    GROUP BY [Vehicle Name], "MODEL-YEAR"
    ORDER BY "MODEL-YEAR", [Vehicle Name];
    """
    df = pd.read_sql_query(query, connection)

    # Close the connection to the database
    connection.close()

    # Pivot the data to get a matrix format suitable for the stacked bar chart
    pivot_df = df.pivot(index='ModelYear', columns='Vehicle Name', values='count').fillna(0)

    # Plotting the stacked bar chart
    ax = pivot_df.plot(kind='bar', stacked=True, figsize=(15, 10))
    plt.title('Vehicle Model Growth Over Time', fontsize=14)
    plt.xlabel("Model Year", fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)
    plt.legend(title='Vehicle Name', title_fontsize='13', fontsize='10', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Adjust spacing
    plt.tight_layout()

    # Save the stacked bar chart to a .png file
    plt.savefig('stacked_bar_chart.png')

if __name__ == "__main__":
    db_name = 'merged_data.db'  # Replace with your database name
    draw_pie_chart(db_name)
    draw_bar_chart(db_name)  # Call the new function to draw the bar chart
    draw_stacked_bar_chart(db_name)
