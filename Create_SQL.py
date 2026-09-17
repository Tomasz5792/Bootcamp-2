#https://www.w3schools.com/python/ref_module_sqlite3.asp
#https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html

import sqlite3
from flask import app
import pandas as pd

def create_database():
    """Creates an in-memory SQLite database and populates it with data from CSV files.

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
        CREATE TABLE rentals (
            rental_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            vehicle_id INTEGER,
            rental_date DATE,
            return_date DATE,
            return_location TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
            UNIQUE (vehicle_id, rental_date)
        )
    ''')

    #adding some fake rental data
    cursor.execute("INSERT INTO rentals (customer_id, vehicle_id, rental_date, return_date, return_location) VALUES (1, 1, '2023-01-01', '2023-01-05', 'Bristol')")
    cursor.execute("INSERT INTO rentals (customer_id, vehicle_id, rental_date, return_date, return_location) VALUES (2, 2, '2023-02-01', '2023-02-05', 'Manchester')")
    conn.commit()

    return conn


def check_database(conn):
    # show first 5 rows of vehicles, customers and rentals tables
    print("Vehicles:")
    print(pd.read_sql('SELECT * FROM vehicles LIMIT 5', conn))

    print("\nCustomers:")
    print(pd.read_sql('SELECT * FROM customers LIMIT 5', conn))

    print("\nRentals:")
    print(pd.read_sql('SELECT * FROM rentals LIMIT 5', conn))


if __name__ == "__main__":
    conn = create_database()
    check_database(conn)