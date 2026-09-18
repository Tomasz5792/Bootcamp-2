# For individual vehicles:
# - show details of specific vehicle (according to car reg)                 - done
# - rent a specific vehicle
# - return a specific vehicle
# - add a new vehicle to the rental fleet
# - remove a specific vehicle from the rental fleet

# For multiple vehicles:
# - show all vehicles                                                       - done
# - show vehicles available for rent (preferably organised per branch)
# - show vehicles currently rented out (preferably organised per branch)


from flask import Flask, jsonify
import pandas as pd
#import json
from Backend.Create_SQL import create_database
from Backend.Create_SQL import check_database


app = Flask(__name__)
conn = create_database()
#check_database(conn)


#homepage
#http://127.0.0.1:5000/
@app.route("/")
def home_page():
    return "<p>Car company home page.</p>"


# - show all vehicles
#http://127.0.0.1:5000/vehicles
@app.route("/vehicles")
def get_vehicles():
    """GETs all vehicles and returns as a JSON

    Args:
        None

    Returns:
        JSON: JSON object containing all vehicles in the database
    """
    df = pd.read_sql('SELECT * FROM vehicles', conn)
    return df.to_json(orient="records")

# - show details of specific vehicle (according to car reg)
#http://127.0.0.1:5000/vehicles/JA82VXV
#http://127.0.0.1:5000/vehicles/empty
@app.route("/vehicles/<vrm>")
def get_vehicle(vrm):
    """GETs a specific vehicle and returns as a JSON
    
    Args:
        vrm (str): Vehicle registration number
        
    Returns:
        JSON: JSON object containing the details of the specific vehicle, else a 404 error.
    """
    df = pd.read_sql(f"SELECT * FROM vehicles WHERE vrm = '{vrm}'", conn)
    if df.empty:
        return jsonify({'error': 'Vehicle not found'}), 404
    return df.to_json(orient="records")

# - show vehicles available for rent (preferably organised per branch)
#http://127.0.0.1:5000/vehicle/available
@app.route('/vehicle/available')
def get_available_vehicles():
    """GETs all available vehicles and returns as a JSON

    Args:
        None

    Returns:
        JSON: JSON object containing all available vehicles in the database
    """
    df = pd.read_sql("SELECT * FROM vehicles WHERE status='AVAILABLE'",conn)

    return df.to_json(orient='records')

# - show vehicles currently rented out (preferably organised per branch)
#http://127.0.0.1:5000/vehicle/rented
@app.route('/vehicle/rented')
def get_rented_vehicles():
    """GETs all rented vehicles and returns as a JSON

    Args:
        None

    Returns:
        JSON: JSON object containing all rented vehicles in the database
    """
    df = pd.read_sql("SELECT * FROM vehicles WHERE status='RENTED'",conn)

    return df.to_json(orient='records')

# - show reports for number of vehicles per branch
#http://127.0.0.1:5000/reports/branch
@app.route('/reports/branch')
def get_branch_report():
    """GETs a report of the number of vehicles per branch and returns as a JSON

    Args:
        None
        
    Returns:
        JSON: JSON object containing the number of vehicles per branch in the database
        """
    query = """
    SELECT branch,
           COUNT(*) AS total_vehicles
    FROM vehicles
    GROUP BY branch
    """

    df = pd.read_sql(query,conn)

    return df.to_json(orient="records")

if __name__ == "__main__":
    app.run(debug=True)