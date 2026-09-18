#https://www.w3schools.com/python/ref_module_sqlite3.asp
#https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html

import sqlite3
from flask import app
import pandas as pd
import random # for geting a random customer
import datetime

def create_database():
    """Creates in-memory SQLite databases and populates them with data from CSV files.  
    Tables are created for vehicles, customers, and status.

    Args:
        None
    
    Returns:
        sqlite3.Connection: Connection object to the in-memory SQLite database
    """
    #conn = sqlite3.connect(':memory:')
    conn = sqlite3.connect(':memory:', check_same_thread=False)

    #dataframes
    vehicles = pd.read_csv('Data/vehicle.csv')
    customers = pd.read_csv('Data/customer.csv')

    #dataframes to sql
    vehicles.to_sql('vehicles', conn, if_exists='replace', index=False)
    customers.to_sql('customers', conn, if_exists='replace', index=False)


    #create rental table
    #needs to:
    # - rent a specific vehicle
    # - return a specific vehicle
    # --- how does this work if the car is returned in another city?

    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE status (
            rental_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            vehicle_id INTEGER,
            status_date_time DATETIME,
            return_location TEXT,
            status TEXT CHECK(status IN ('RENTED', 'RETURNED', 'DAMAGED', 'SERVICEREQ')),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
            UNIQUE (vehicle_id, status_date_time)
        )
    ''')

    cursor.execute("SELECT customerId FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]



    #adding vehicle data into the status table
    for index, row in vehicles.iterrows():

        if row['status'] != 'AVAILABLE':

            customer_id = random.choice(customer_ids)  # randomly assign a customer_id from the customers table
            vehicle_id = row['vehicle_id']
            status_date_time = (datetime.datetime.now()
                                - pd.Timedelta(days=random.randint(1, 30))
                                - pd.Timedelta(seconds=random.randint(0, 86399))
                                ).strftime('%Y-%m-%d %H:%M:%S')  # random date within the last 30 days
            return_location = None
            status = row['status']  # adds statusses which are not AVAILABLE

            cursor.execute(
            "INSERT INTO status (customer_id, vehicle_id, status_date_time, return_location, status) "
            "VALUES (?, ?, ?, ?, ?)",
            (customer_id, vehicle_id, status_date_time, return_location, status)
        )
    conn.commit()

    return conn


def check_database(conn):
    # show first 5 rows of vehicles, customers and status tables
    print("vehicles:")
    print(pd.read_sql('SELECT * FROM vehicles LIMIT 5', conn))

    print("\ncustomers:")
    print(pd.read_sql('SELECT * FROM customers LIMIT 5', conn))

    print("\nstatus:")
    print(pd.read_sql('SELECT * FROM status LIMIT 5', conn))


if __name__ == "__main__":
    conn = create_database()
    check_database(conn)