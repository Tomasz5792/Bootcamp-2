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

<<<<<<< Updated upstream
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
=======
def get_vehicle_id(vrm):
    """Retrieves the numeric primary key of a vehicle based on its VRM."""
    vehicle = get_vehicle_by_vrm(vrm)
    if vehicle.empty:
        return None
    return int(vehicle.iloc[0]["vehicle_id"])

def get_latest_status(vehicle_id):
    """Fetches the most recent status record for a specific vehicle."""
    query = """
    SELECT *
    FROM status
    WHERE vehicle_id = ?
    ORDER BY status_date_time DESC
    LIMIT 1
    """
    df = pd.read_sql(query, conn, params=(vehicle_id,))
    return df

def get_current_status(vehicle_id):
    """Extracts the string value of a vehicle's current status (e.g., 'AVAILABLE')."""
    latest = get_latest_status(vehicle_id)
    if latest.empty:
        return None
    return latest.iloc[0]["status"]

####################
# Search & Filters #
####################

@app.route('/api/locations')
def get_locations():
    """GETs all unique active branch locations from the database."""
    query = """
    SELECT DISTINCT status_location AS name
>>>>>>> Stashed changes
    FROM status
    WHERE status_location IS NOT NULL AND status_location != ''
    ORDER BY name ASC
    """
<<<<<<< Updated upstream

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
=======
    df = pd.read_sql(query, conn)
    return df.to_json(orient="records")
>>>>>>> Stashed changes

@app.route('/api/car-types')
def get_car_types():
    """GETs all unique vehicle categories from the database."""
    query = """
    SELECT DISTINCT category AS name
    FROM vehicles
    WHERE category IS NOT NULL AND category != ''
    ORDER BY name ASC
    """
    df = pd.read_sql(query, conn)
    return df.to_json(orient="records")

####################
# Vehicle Lookups  #
####################

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
@app.route('/api/reports/branch-inventory')
def get_branch_report():
    """GETs a report of the number of vehicles per branch and returns as a JSON

    Args:
        None
        
    Returns:
        JSON: JSON object containing the number of vehicles per branch in the database
        """
    
    query = """
    SELECT s.status_location AS branch,
            COUNT(*) AS car_count
    FROM status s
    INNER JOIN
    (
        SELECT vehicle_id,
           MAX(status_date_time) AS max_date
        FROM status
        GROUP BY vehicle_id
    ) latest
    ON s.vehicle_id = latest.vehicle_id
    AND s.status_date_time = latest.max_date
    GROUP BY s.status_location
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
        return jsonify(
            {"error": "Vehicle not found"}
        ), 404

    current_status = get_current_status(
        vehicle_id
    )

    if current_status != "AVAILABLE":
        return jsonify(
            {
                "error":
                f"Vehicle cannot be rented because status is {current_status}"
            }
        ), 400

    customer_id = session.get("customer_id")

    if not customer_id:
        return jsonify(
            {
                "error":
                "User not authenticated in session"
            }
        ), 401

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
            customer_id,
            vehicle_id,
            latest.iloc[0]["status_location"],
            "RENTED"
        )
    )

    conn.commit()

    return jsonify(
        {
            "message":
            "Vehicle rented successfully"
        }
    )


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

<<<<<<< Updated upstream
=======
# api call to give all locations
# http://127.0.0.1:5000/vehicle/locations
@app.route("/vehicle/locations")
def get_vehicle_locations():
    """GETs all vehicle locations

    Args:
        None

    Returns:
        JSON: JSON object containing all vehicle locations
    """
    query = """
    SELECT DISTINCT status_location
    FROM status
    """
    df = pd.read_sql(query, conn)
    return df.to_json(orient="records")

#api call to give vehicule types
# http://127.0.0.1:5000/vehicle/types
@app.route("/vehicle/types")
def get_vehicle_types():
    """GETs all vehicle types

    Args:
        None

    Returns:
        JSON: JSON object containing all vehicle types
    """
    query = """
    SELECT DISTINCT category
    FROM vehicles
    """
    df = pd.read_sql(query, conn)
    return df.to_json(orient="records")

# Add a new vehicle to the rental fleet
# http://127.0.0.1:5000/vehicles
@app.route("/vehicles", methods=["POST"])
def add_vehicle():

<<<<<<< Updated upstream
=======
####################
# Fleet Management #
####################

@app.route("/api/vehicles/add", methods=["POST"])
def add_vehicle():
    """Adds a new vehicle to the fleet and sets its initial status to AVAILABLE."""
>>>>>>> Stashed changes
    data = request.get_json()

    required_fields = [
        "make",
        "model",
        "colour",
        "vin",
        "year",
        "vrm",
        "category",
        "numberSeats",
        "dayRate",
        "fuelEconomy"
    ]

<<<<<<< Updated upstream
    for field in required_fields:

        if field not in data:

=======
@app.route("/api/vehicles/<vrm>/status", methods=["POST"])
def update_vehicle_status(vrm):
    """Manually forces a status update (e.g., sending a car to Maintenance)."""
    data = request.get_json()
    vehicle_id = get_vehicle_id(vrm)
    
    if not vehicle_id:
        return jsonify({"error": "Vehicle not found"}), 404
        
    new_status = data.get('status')
    new_location = data.get('location')
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO status (customer_id, vehicle_id, status_date_time, status_location, status) "
            "VALUES (1, ?, CURRENT_TIMESTAMP, ?, ?)",
            (vehicle_id, new_location, new_status)
        )
        conn.commit()
        return jsonify({"message": f"Status successfully updated to {new_status}"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400

# ==========================================
# CUSTOMER DASHBOARD API ROUTE
# ==========================================

@app.route("/api/customer/bookings")
def get_customer_bookings():
    """
    Retrieves all active rentals/bookings for the customer 
    currently logged into the active Flask session.
    """
    # Verify if the user is authenticated and has the 'customer' role
    if not session.get('logged_in') or session.get('role') != 'customer':
        return jsonify({"error": "Unauthorized"}), 401
        
    customer_id = session.get('customer_id')
    
    # SQL query to fetch vehicle details and latest status for the logged-in user
    query = """
        SELECT v.*, s.status_date_time, s.status_location, s.status
        FROM vehicles v
        JOIN status s ON v.vehicle_id = s.vehicle_id
        WHERE s.customer_id = ? AND s.status = 'RENTED'
        AND s.status_date_time = (
            SELECT MAX(s2.status_date_time)
            FROM status s2
            WHERE s2.vehicle_id = v.vehicle_id
        )
    """
    df = pd.read_sql(query, conn, params=(customer_id,))
    return df.to_json(orient="records")

####################
# AUTHENTICATION   #
####################

@app.route("/api/login", methods=["POST"])
def api_login():
    """Authenticates a user, routing Staff to the backend and Customers to the storefront."""
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password", "") 

        # 1. SPECIAL CASE: Admin / Staff Login
        if email == "admin" and password == "admin":
            session['logged_in'] = True
            session['customer_id'] = 0 
            session['customer_name'] = 'Administrator'
            session['role'] = 'admin' 
            
>>>>>>> Stashed changes
            return jsonify({
                "error": f"Missing field: {field}"
            }), 400

    # Check VRM doesn't already exist

    existing_vehicle = pd.read_sql(
        """
        SELECT *
        FROM vehicles
        WHERE UPPER(vrm) = UPPER(?)
        """,
        conn,
        params=(data["vrm"],)
    )

<<<<<<< Updated upstream
    if not existing_vehicle.empty:
=======
@app.route("/api/signup", methods=["POST"])
def api_signup():
    """Registers a new customer, generating a sequential ID, and inserts them into the database."""
    try:
        data = request.get_json()
        cursor = conn.cursor()
        
        # Check if the email already exists to prevent duplication
        cursor.execute("SELECT email FROM customers WHERE email = ?", (data['email'],))
        if cursor.fetchone():
            return jsonify({"success": False, "error": "This email is already registered."}), 400
>>>>>>> Stashed changes

        return jsonify({
            "error": "Vehicle already exists"
        }), 400

    cursor = conn.cursor()

    # Insert vehicle

<<<<<<< Updated upstream
    cursor.execute(
        """
        INSERT INTO vehicles
        (
            make,
            model,
            colour,
            vin,
            year,
            vrm,
            category,
            numberSeats,
            dayRate,
            fuelEconomy
        )
        VALUES
        (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            data["make"],
            data["model"],
            data["colour"],
            data["vin"],
            data["year"],
            data["vrm"],
            data["category"],
            data["numberSeats"],
            data["dayRate"],
            data["fuelEconomy"]
        )
    )
=======
@app.route("/logout")
@app.route("/api/logout", methods=["POST"])
def logout():
    """Clears the current user session and redirects to the public homepage."""
    session.clear() 
    
    # Handle API calls vs standard link clicks
    if request.method == "POST":
        return jsonify({"success": True, "message": "Logged out successfully"}), 200
    return redirect(url_for('home_page')) 
>>>>>>> Stashed changes

    conn.commit()

    # Retrieve newly-created vehicle

    vehicle_id = cursor.lastrowid

    # Create initial status record

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
        NULL,
        ?,
        CURRENT_TIMESTAMP,
        ?,
        'AVAILABLE'
    )
    """,
    (
        vehicle_id,
        data["branch"]
    )
)

    conn.commit()

    return jsonify({
        "message": "Vehicle added successfully",
        "vehicle_id": vehicle_id
    }), 201

>>>>>>> Stashed changes
if __name__ == "__main__":
    app.run(debug=True)
    