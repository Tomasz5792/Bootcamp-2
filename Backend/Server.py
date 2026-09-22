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


from flask import Flask, jsonify, render_template, request
import pandas as pd
import json
from Create_SQL import create_database, check_database
import datetime


#app = Flask(__name__)
app = Flask(__name__, template_folder="../Frontend/templates", static_folder="../Frontend/static") #frontend html

conn = create_database()
#check_database(conn)  # shows the sql tables for debugging purposes


#################
#################
##### Pages #####
#################
#################


#homepage
#http://127.0.0.1:5000/
@app.route("/")
def home_page():
    return render_template("Home.html")

#homepage
#http://127.0.0.1:5000/login
@app.route("/login")
def login_page():
    return render_template("Login.html")

#signup page
#SignUp.html
#http://127.0.0.1:5000/signup
@app.route("/signup")
def signup_page():
    return render_template("SignUp.html")



#customer homepage
#CustomerHome.html
#customer home page
#http://127.0.0.1:5000/home
@app.route("/home")
def customer_home():
    return render_template("CustomerHome.html")

#customer booking page
#CustomerBooking.html
#http://127.0.0.1:5000/booking
@app.route("/booking")
def customer_booking():
    return render_template("CustomerBooking.html")



#staff home page
#StaffHome copy.html
#http://127.0.0.1:5000/staffhome
@app.route("/staffhome")
def staff_home():
    return render_template("StaffHome.html")

#staff rental page
#StaffRental.html
#http://127.0.0.1:5000/staff/rental
@app.route("/staff/rental")
def staff_rental():
    return render_template("StaffRental.html")

#staff reports page
#StaffReports.html
#http://127.0.0.1:5000/staff/reports
@app.route("/staff/reports")
def staff_reports():
    return render_template("StaffReports.html")


##################################################
### Test Pages for API testing and development ###
##################################################

#test page
#http://127.0.0.1:5000/test
@app.route("/test")
def test_page():
    return render_template("test/Test.html")

#test HTTP Request page
#http://127.0.0.1:5000/testHTTPRequest
@app.route("/testHTTPRequest")
def test_pageHTTPRequest():
    return render_template("test/TestHTTPRequest.html")



##############################
##############################
##### API json endpoints #####
##############################
##############################

####################
# Helper Functions #
####################

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


# show vehicles available for rent  
### doesn't check if their rented later
# http://127.0.0.1:5000/vehicle/available
@app.route('/vehicles/available')
def get_available_vehicles():
    """GETs all available vehicles and returns as a JSON

    Args:
        None

    Returns:
        JSON: JSON object containing all available vehicles in the database
    """
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
    df = pd.read_sql(query, conn)
    return df.to_json(orient="records")


# show vehicles available for rent filtered by location, type and date to and from.
# http://127.0.0.1:5000/vehicle/available/search?loc=Bristol&type=Compact&from=2026-09-15&to=2026-09-25
# http://127.0.0.1:5000/vehicle/available/search?loc=Manchester&type=SUV&from=2026-09-21&to=2026-10-05
# http://127.0.0.1:5000/vehicle/available/search?loc=Manchester&type=Coupe&from=2026-09-19&to=2026-09-30
# http://127.0.0.1:5000/vehicle/available/search
@app.route('/vehicle/available/search')
def search_available_vehicles():
    """GETs all available vehicles filtered by location, type, from and to and returns as a JSON.
    Does this by filtering on the last status before <from> being availabe and there being no status changes between <from> and <to>

    Example requests:
        /vehicle/available/search
        /vehicle/available/search?loc=Bristol&type=Compact
        /vehicle/available/search?loc=Manchester&type=SUV&from=2026-09-21&to=2026-10-05

    Args (query params):
        loc (str, optional): Bristol, Manchester, Luton
        type (str, optional): Compact, Budget, Truck, SUV, Sport, Family, Van, Coupe
        from (str, optional): start date (YYYY-MM-DD) if no date uses today
        to (str, optional): end date (YYYY-MM-DD) if no date uses today + 1

    Returns:
        str: JSON object of matching available vehicles.
    """
    loc = request.args.get('loc')
    vehicle_type = request.args.get('type')
    date_from = request.args.get('from', datetime.datetime.today().strftime('%Y-%m-%d'))
    date_to = request.args.get('to', (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'))

    query = """
    SELECT
        v.*,
        s.status_date_time,
        s.status_location
    FROM vehicles v
    JOIN status s
        ON v.vehicle_id = s.vehicle_id
        AND s.status_date_time = (
            SELECT MAX(s3.status_date_time)
            FROM status s3
            WHERE s3.vehicle_id = v.vehicle_id
            AND s3.status_date_time < ?
        )
    WHERE s.status = 'AVAILABLE'
    AND NOT EXISTS (
        SELECT 1
        FROM status s2
        WHERE s2.vehicle_id = v.vehicle_id
        AND s2.status_date_time >= ?
        AND s2.status_date_time <= ?
    )
    """
    params = [date_from, date_from, date_to]

    if loc:
        query += " AND s.status_location  = ?"
        params.append(loc)

    if vehicle_type:
        query += " AND v.category = ?"
        params.append(vehicle_type)

    df = pd.read_sql(query, conn, params=params)
    return df.to_json(orient="records")


# Updating and Working | Please test
# show vehicles currently rented out (preferably organised per branch)
# http://127.0.0.1:5000/vehicles/rented
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
    df = pd.read_sql(query, conn)
    return df.to_json(orient="records")


# Updating and Working | Please test
# show reports for number of vehicles per branch
# http://127.0.0.1:5000/reports/branch
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

# rent a specific vehicle by registration number (vrm)
# http://127.0.0.1:5000/vehicles/<vrm>/rent
# http://127.0.0.1:5000/vehicles/JA82VXV/rent
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


# Return a specific vehicle by registration number (vrm)
# http://127.0.0.1:5000/vehicles/<vrm>/return
# http://127.0.0.1:5000/vehicles/JA82VXV/return
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

#api coll to give vehicule types
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


if __name__ == "__main__":
    app.run(debug=True)
    