#https://www.w3schools.com/python/ref_module_sqlite3.asp
#https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html

import sqlite3
import pandas as pd

conn = sqlite3.connect(':memory:')

vehicles = pd.read_csv('Data/vehicle.csv')
#print(vehicles.head())

vehicles.to_sql('vehicles', conn, if_exists='replace', index=False)

cursor = conn.cursor()
cursor.execute('SELECT * FROM vehicles LIMIT 5')
rows = cursor.fetchall()

for row in rows:
    print(row)