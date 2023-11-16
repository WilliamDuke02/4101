import sqlite3

def get_table_names(cursor):
    """
    Retrieves a list of all table names in the database.

    :param cursor: SQLite database cursor.
    :return: List of table names.
    """
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    return [table[0] for table in tables]

def print_table_data(cursor, table_name):
    """
    Prints the column names and the first ten rows of data from a specific table.

    :param cursor: SQLite database cursor.
    :param table_name: Name of the table to print data from.
    """
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [column_info[1] for column_info in cursor.fetchall()]

    # Print column names
    print(f"\nData from table '{table_name}':")
    print(" | ".join(columns))

    # Print rows of data
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 10;")
    rows = cursor.fetchall()
    for row in rows:
        print(" | ".join(map(str, row)))

def main(db_path):
    """
    Connects to the SQLite database and prints the first ten rows of each table.

    :param db_path: Path to the SQLite database file.
    """
    # Connect to the SQLite database
    connection = sqlite3.connect(db_path)

    try:
        cursor = connection.cursor()

        # Retrieve all table names
        table_names = get_table_names(cursor)

        # Print data from each table
        for table in table_names:
            print_table_data(cursor, table)

    except sqlite3.Error as e:
        print(f"An error occurred: {e.args[0]}")

    finally:
        # Close the database connection
        connection.close()

# Path to your SQLite database
db_path = '/mnt/c/Users/duck2/Desktop/git/test/merged_data.db'

# Execute the main function
main(db_path)
