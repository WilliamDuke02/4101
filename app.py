from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pandas as pd

app = Flask(__name__)

def fetch_column_values(column_name, filter_column=None, filter_value=None):
    with sqlite3.connect('merged_data.db') as conn:
        cursor = conn.cursor()
        query = f'SELECT DISTINCT "{column_name}" FROM merged_currentvins_modified'
        params = ()
        if filter_column and filter_value:
            query += f' WHERE "{filter_column}" = ?'
            params = (filter_value,)
        cursor.execute(query, params)
        return [row[0] for row in cursor.fetchall()]

@app.route('/')
def index():
    manufacturers = fetch_column_values('Vehicle Manufacturer')
    return render_template('index.html', manufacturers=manufacturers)

@app.route('/fetch_options', methods=['POST'])
def fetch_options():
    column = request.form.get('column')
    filter_column = request.form.get('filter_column')
    filter_value = request.form.get('filter_value')
    options = fetch_column_values(column, filter_column, filter_value)
    return {'options': options}

@app.route('/export', methods=['POST'])
def export_to_excel():
    selections = {key: value for key, value in request.form.items() if value != "Any"}
    query_parts = [f'"{key}" = ?' for key in selections.keys()]
    query = f"SELECT * FROM merged_currentvins_modified WHERE {' AND '.join(query_parts)}" if selections else "SELECT * FROM merged_currentvins_modified"
    
    try:
        with sqlite3.connect('merged_data.db') as conn:
            df = pd.read_sql_query(query, conn, params=list(selections.values()))
            file_name = f'exported_data_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            df.to_excel(file_name, index=False)
            return f"Data exported to '{file_name}'."
    except Exception as e:
        return f"Error during export: {e}"

if __name__ == '__main__':
    app.run(debug=True)
