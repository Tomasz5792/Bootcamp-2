import sqlite3
import pandas as pd
import random # for getting a random customer
import datetime

def create_database():
    """
    Creates an in-memory SQLite database and populates it with data from CSV files.  
    Tables are created for vehicles, customers, and their rental status history.

    Args:
        None
    
    Returns:
        sqlite3.Connection: Connection object to the in-memory SQLite database
    """
    
    # Initialize connection allowing multi-threading (crucial for Flask)
    conn = sqlite3.connect(':memory:', check_same_thread=False)

    # 1. Load initial data from CSV files into Pandas DataFrames
    vehicles = pd.read_csv('Data/vehicle.csv')
    customers = pd.read_csv('Data/customer.csv')

    # 2. Convert Pandas DataFrames directly into SQL tables
    vehicles.to_sql('vehicles', conn, if_exists='replace', index=False)
    customers.to_sql('customers', conn, if_exists='replace', index=False)

    cursor = conn.cursor()
    
    # 3. Create the 'status' table to track rental history and locations
    # Note: Removed the FOREIGN KEY constraints to avoid schema conflicts 
    # since 'vehicles' and 'customers' were created dynamically by pandas.
    cursor.execute('''
        CREATE TABLE status (
            rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            vehicle_id INTEGER,
            status_date_time DATETIME,
            status_location TEXT,
            status TEXT CHECK(status IN ('AVAILABLE', 'RENTED', 'RETURNED', 'DAMAGED', 'SERVICEREQ'))
        )
    ''')

    # Fetch all valid customer IDs to assign random history
    cursor.execute("SELECT customerId FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]

    # 4. Populate the 'status' table with initial historical data
    for index, row in vehicles.iterrows():
        
        # Randomly assign a customer_id from the customers table
        customer_id = random.choice(customer_ids)  
        vehicle_id = row['vehicle_id']
        
        # Generate a random date/time within the last 30 days
        status_date_time = (datetime.datetime.now()
                            - pd.Timedelta(days=random.randint(1, 30))
                            - pd.Timedelta(seconds=random.randint(0, 86399))
                            ).strftime('%Y-%m-%d %H:%M:%S')  
        
        # Extract initial branch and status from the vehicles dataframe
        status_location = row.get('branch', 'Unknown') 
        status = row.get('status', 'AVAILABLE')

        # Insert the generated record into the status table
        cursor.execute(
            "INSERT INTO status (customer_id, vehicle_id, status_date_time, status_location, status) "
            "VALUES (?, ?, ?, ?, ?)",
            (customer_id, vehicle_id, status_date_time, status_location, status)
        )
            
    # 5. Clean up the 'vehicles' table by removing redundant columns
    # We drop these because this data is now managed dynamically in the 'status' table
    try:
        cursor.execute("ALTER TABLE vehicles DROP COLUMN status")
        cursor.execute("ALTER TABLE vehicles DROP COLUMN branch")
    except sqlite3.OperationalError:
        # Ignore error if columns don't exist (e.g. running the script twice)
        pass

    conn.commit()

    # 6. Export the finalized SQL tables back to CSV for backup/debugging
    vehicles_df = pd.read_sql('SELECT * FROM vehicles', conn)
    customers_df = pd.read_sql('SELECT * FROM customers', conn)
    status_df = pd.read_sql('SELECT * FROM status', conn)

    vehicles_df.to_csv('Data/current/vehicles_export.csv', index=False)
    customers_df.to_csv('Data/current/customers_export.csv', index=False)
    status_df.to_csv('Data/current/status_export.csv', index=False)

    return conn


def check_database(conn):
    """
    Utility function to print out a preview of the database tables
    for debugging purposes.
    """
    print("--- Vehicles Table Preview ---")
    print(pd.read_sql('SELECT * FROM vehicles LIMIT 5', conn))

    print("\n--- Customers Table Preview ---")
    print(pd.read_sql('SELECT * FROM customers LIMIT 5', conn))

    print("\n--- Status Table Preview ---")
    print(pd.read_sql('SELECT * FROM status LIMIT 10', conn))


if __name__ == "__main__":
    conn = create_database()
    check_database(conn)