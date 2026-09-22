# For individual vehicles:
# - show details of specific vehicle (according to car reg) --------------------------------------------------- done
# - rent a specific vehicle
# - return a specific vehicle
# - add a new vehicle to the rental fleet
# - remove a specific vehicle from the rental fleet

# For multiple vehicles:
# - show all vehicles ----------------------------------------------------------------------------------------- done
# - show vehicles available for rent (preferably organised per branch)
# - show vehicles currently rented out (preferably organised per branch)

# Extensions:
# - Homepage -------------------------------------------------------------------------------------------------- done
# - show reports for number of vehicles per branch
# - show reports for number of vehicles per status (available, rented, returned, damaged, service required)
# - show reports for number of vehicles per status per branch
# - As above but for a specific time period (e.g. last week, last month, last year)
# - Create sign up for a new customer and add them to the customers table

# Security:
# - add authentication to the API
# - add authorization to the API (e.g. only allow certain users to add/remove vehicles)

# Documentation:
# - add documentation for the API - Postman collection


from flask import Flask, jsonify
import pandas as pd
#import json
from Create_SQL import create_database, check_database


app = Flask(__name__)
conn = create_database()
#check_database(conn)  # shows the sql tables for debugging purposes

# -----------------------------
# Helper Functions
# -----------------------------

def get_vehicle_by_vrm(vrm):
    
    query = """
    SELECT *
    FROM vehicles
    WHERE UPPER(vrm) = UPPER(?)
    """

    df = pd.read_sql(
        query,
        conn,
        params=(vrm,)
    )

    return df


def get_vehicle_id(vrm):

    vehicle = get_vehicle_by_vrm(vrm)

    if vehicle.empty:
        return None

    return int(
        vehicle.iloc[0]["vehicle_id"]
    )


def get_latest_status(vehicle_id):

    query = """
    SELECT *
    FROM status
    WHERE vehicle_id = ?
    ORDER BY status_date_time DESC
    LIMIT 1
    """

    df = pd.read_sql(
        query,
        conn,
        params=(vehicle_id,)
    )

    return df


def get_current_status(vehicle_id):

    latest = get_latest_status(vehicle_id)

    if latest.empty:
        return None

    return latest.iloc[0]["status"]



#homepage
#http://127.0.0.1:5000/
@app.route("/")
def home_page():
    return "<p>Car company home page.</p>"




# show all vehicles
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




# show details of specific vehicle (according to car reg)
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

    vehicle = get_vehicle_by_vrm(vrm)

    if vehicle.empty:
        return jsonify({
            "error": "Vehicle not found"
        }),404

    return vehicle.to_json(
        orient="records"
    )



  
# Updating and Working | Please test

# show vehicles available for rent (preferably organised per branch)
#http://127.0.0.1:5000/vehicle/available
@app.route('/vehicles/available')
def get_available_vehicles():
    """GETs all available vehicles and returns as a JSON

    Args:
        None

    Returns:
        JSON: JSON object containing all available vehicles in the database
    """
<<<<<<< Updated upstream
    df = pd.read_sql(
    """
    SELECT v.*, s.status
    FROM vehicles v
    JOIN status s
        ON v.vehicle_id = s.vehicle_id
    WHERE s.status='AVAILABLE'
    """,
    conn)
    return df.to_json(orient='records')
=======

    query = """
    SELECT
        v.*
    FROM vehicles v
    JOIN status s
        ON v.vehicle_id = s.vehicle_id
    WHERE s.status='AVAILABLE'
    AND s.status_date_time=
    (
        SELECT MAX(s2.status_date_time)
        FROM status s2
        WHERE s2.vehicle_id=v.vehicle_id
    )
    """

<<<<<<< Updated upstream
    df = pd.read_sql(query, conn)

    return df.to_json(orient="records")
>>>>>>> Stashed changes
=======
    df = pd.read_sql( query, conn)
    return df.to_json( orient="records")
>>>>>>> Stashed changes




# Updating and Working | Please test

# show vehicles currently rented out (preferably organised per branch)
#http://127.0.0.1:5000/vehicles/rented
@app.route('/vehicles/rented')
def get_rented_vehicles():
    """GETs all rented vehicles and returns as a JSON

    Args:
        None

    Returns:
        JSON: JSON object containing all rented vehicles in the database
    """

    query = """
    SELECT
        v.*
    FROM vehicles v
    JOIN status s
        ON v.vehicle_id = s.vehicle_id
    WHERE s.status='RENTED'
    AND s.status_date_time=
    (
        SELECT MAX(s2.status_date_time)
        FROM status s2
        WHERE s2.vehicle_id=v.vehicle_id
    )
    """

    df = pd.read_sql( query, conn)
    return df.to_json( orient="records")


# Updating and Working | Please test

# show reports for number of vehicles per branch
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
    SELECT
        status_location,
        COUNT(*) AS total
    FROM status s
    WHERE s.status_date_time=
    (
        SELECT MAX(s2.status_date_time)
        FROM status s2
        WHERE s2.vehicle_id=s.vehicle_id
    )
    GROUP BY status_location
    """

    df = pd.read_sql(query, conn)
    return df.to_json(orient="records")


# Returns a report of the number of vehicles per status and returns as a JSON
@app.route('/reports/status')
def get_status_report():
    """GETs a report of the number of vehicles per status and returns as a JSON

    Args:
        None

    Returns:
        JSON: JSON object containing the number of vehicles per status in the database
    """

    query = """
    SELECT
        status,
        COUNT(*) AS total
    FROM status s
    WHERE s.status_date_time=
    (
        SELECT MAX(s2.status_date_time)
        FROM status s2
        WHERE s2.vehicle_id=s.vehicle_id
    )
    GROUP BY status
    """

    df = pd.read_sql(query, conn)
    return df.to_json(orient="records")

#rent a specific vehicle by registration number (vrm)
#http://127.0.0.1:5000/vehicles/<vrm>/rent
@app.route("/vehicles/<vrm>/rent")
def rent_vehicle(vrm):

    vehicle_id = get_vehicle_id(vrm)

    if vehicle_id is None:
        return jsonify({
            "error":"Vehicle not found"
        }),404

    current_status = get_current_status(
        vehicle_id
    )

    if current_status != "AVAILABLE":

        return jsonify({
            "error":
            f"Vehicle cannot be rented because status is {current_status}"
        }),400

    latest = get_latest_status(
        vehicle_id
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO status
        (
            customer_id,
            vehicle_id,
            status_date_time,
            status_location,
            status
        )
        VALUES
        (
            ?, ?, CURRENT_TIMESTAMP, ?, ?
        )
        """,
        (
            latest.iloc[0]["customer_id"],
            vehicle_id,
            latest.iloc[0]["status_location"],
            "RENTED"
        )
    )

    conn.commit()

    return jsonify({"message":"Vehicle rented successfully"})


#Return a specific vehicle by registration number (vrm)
#http://127.0.0.1:5000/vehicles/<vrm>/return
@app.route("/vehicles/<vrm>/return")
def return_vehicle(vrm):

    vehicle_id = get_vehicle_id(vrm)

    if vehicle_id is None:
        return jsonify({
            "error":"Vehicle not found"
        }),404

    current_status = get_current_status(
        vehicle_id
    )

    if current_status != "RENTED":

        return jsonify({
            "error":
            f"Vehicle cannot be returned because status is {current_status}"
        }),400

    latest = get_latest_status(
        vehicle_id
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO status
        (
            customer_id,
            vehicle_id,
            status_date_time,
            status_location,
            status
        )
        VALUES
        (
            ?, ?, CURRENT_TIMESTAMP, ?, ?
        )
        """,
        (
            latest.iloc[0]["customer_id"],
            vehicle_id,
            latest.iloc[0]["status_location"],
            "AVAILABLE"
        )
    )

    conn.commit()

    return jsonify({
        "message":"Vehicle returned successfully"
    })


#Delete a specific vehicle by registration number (vrm)
#http://127.0.0.1:5000/vehicles/<vrm>
@app.route(
    "/vehicles/<vrm>",
    methods=["DELETE"]
)
def delete_vehicle(vrm):

    vehicle_id = get_vehicle_id(vrm)

    if vehicle_id is None:
        return jsonify({
            "error":"Vehicle not found"
        }),404

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM status
        WHERE vehicle_id = ?
        """,
        (vehicle_id,)
    )

    cursor.execute(
        """
        DELETE FROM vehicles
        WHERE vehicle_id = ?
        """,
        (vehicle_id,)
    )

    conn.commit()

    return jsonify({
        "message":"Vehicle deleted successfully"
    })


#Get the rental history for a specific vehicle by registration number (vrm)
#http://127.0.0.1:5000/vehicles/<vrm>/history
@app.route("/vehicle/<vrm>/history")
def get_vehicle_history(vrm):

    vehicle_id = get_vehicle_id(vrm)

    if vehicle_id is None:
        return jsonify({
            "error": "Vehicle not found"
        }), 404

    query = """
    SELECT *
    FROM status
    WHERE vehicle_id = ?
    ORDER BY status_date_time DESC
    """

    df = pd.read_sql(
        query,
        conn,
        params=(vehicle_id,)
    )

    return df.to_json(orient="records")

if __name__ == "__main__":
    app.run(debug=True)
    