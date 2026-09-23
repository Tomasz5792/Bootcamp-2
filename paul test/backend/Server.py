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

from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from urllib.parse import quote 
import pandas as pd
import json
from Create_SQL import create_database, check_database
import datetime

# Initialize Flask App with specific template and static folders
app = Flask(__name__, template_folder="../Frontend/templates", static_folder="../Frontend/static")
app.secret_key = "cheie_super_secreta_pentru_sesiuni" # Required for session management

# Initialize and populate the in-memory SQLite database
conn = create_database()
# check_database(conn)  # Uncomment to show the sql tables for debugging purposes

#################
#################
##### Pages #####
#################
#################

# --- B2C PAGES (Customer Facing) ---

# Homepage
# http://127.0.0.1:5000/
@app.route("/")
def home_page():
    """Renders the main public landing page."""
    return render_template("Home.html")

# Login Page
# http://127.0.0.1:5000/login
@app.route("/login")
def login_page():
    """Renders the login interface for customers and staff."""
    return render_template("login.html")

# Sign-Up Page
# http://127.0.0.1:5000/signup
@app.route("/signup")
def signup_page():
    """Renders the registration form for new customers."""
    return render_template("SignUp.html")

# Customer Home Page (Legacy/Alternative)
# http://127.0.0.1:5000/home
@app.route("/home")
def customer_home():
    """Renders an alternative customer dashboard."""
    return render_template("CustomerHome.html")

# Vehicle Search & Booking Page
# http://127.0.0.1:5000/booking
@app.route("/booking")
def customer_booking():
    """Renders the search results interface for available vehicles."""
    return render_template("CustomerBooking.html")

# Booking Confirmation Info Page
# http://127.0.0.1:5000/booking/confirm
@app.route("/booking/confirm")
def booking_confirm():
    """
    Renders the booking confirmation and payment page. 
    Redirects unauthenticated users to login, preserving the intended destination.
    """
    vrm = request.args.get('vrm')
    date_from = request.args.get('from')
    date_to = request.args.get('to')

    if not session.get('logged_in'):
        current_url = request.full_path
        login_url_with_next = url_for('login_page') + "?next=" + quote(current_url)
        return redirect(login_url_with_next)

    return render_template("BookingConfirm.html", vrm=vrm, date_from=date_from, date_to=date_to)


# --- B2B PAGES (Secure Staff Portal) ---

@app.route("/staffhome")
def staff_home():
    """Renders the staff dashboard. Requires Admin authorization."""
    if not session.get('logged_in') or session.get('role') != 'admin':
        return redirect(url_for('login_page'))
    return render_template("StaffHome.html")

@app.route("/staff/rental")
def staff_rental():
    """Renders the fleet management tool. Requires Admin authorization."""
    if not session.get('logged_in') or session.get('role') != 'admin':
        return redirect(url_for('login_page'))
    return render_template("StaffRental.html")

@app.route("/staff/reports")
def staff_reports():
    """Renders the business analytics dashboard. Requires Admin authorization."""
    if not session.get('logged_in') or session.get('role') != 'admin':
        return redirect(url_for('login_page'))
    return render_template("StaffReports.html")


##################################################
### Test Pages for API testing and development ###
##################################################

# http://127.0.0.1:5000/test
@app.route("/test")
def test_page():
    return render_template("test/Test.html")

# http://127.0.0.1:5000/testHTTPRequest
@app.route("/testHTTPRequest")
def test_pageHTTPRequest():
    return render_template("test/TestHTTPRequest.html")


##############################
##############################
##### API JSON ENDPOINTS #####
##############################
##############################

####################
# Helper Functions #
####################

def get_vehicle_by_vrm(vrm):
    """Retrieves full vehicle details based on its Registration Mark (VRM)."""
    query = """
    SELECT *
    FROM vehicles
    WHERE UPPER(vrm) = UPPER(?)
    """
    df = pd.read_sql(query, conn, params=(vrm,))
    return df

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
    FROM status
    WHERE status_location IS NOT NULL AND status_location != ''
    ORDER BY name ASC
    """
    df = pd.read_sql(query, conn)
    return df.to_json(orient="records")

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

@app.route("/vehicles")
def get_vehicles():
    """GETs the entire vehicle inventory."""
    df = pd.read_sql('SELECT * FROM vehicles', conn)
    return df.to_json(orient="records")

@app.route("/vehicles/<vrm>")
def get_vehicle(vrm):
    """GETs detailed information for a specific vehicle by VRM."""
    vehicle = get_vehicle_by_vrm(vrm)
    if vehicle.empty:
        return jsonify({"error": "Vehicle not found"}), 404
    return vehicle.to_json(orient="records")

@app.route('/vehicles/available')
def get_available_vehicles():
    """GETs all vehicles whose latest status is 'AVAILABLE'."""
    query = """
    SELECT v.*
    FROM vehicles v
    JOIN status s ON v.vehicle_id = s.vehicle_id
    WHERE s.status='AVAILABLE'
    AND s.status_date_time= (
        SELECT MAX(s2.status_date_time)
        FROM status s2
        WHERE s2.vehicle_id=v.vehicle_id
    )
    """
    df = pd.read_sql(query, conn)
    return df.to_json(orient="records")

@app.route('/vehicle/available/search')
def search_available_vehicles():
    """
    GETs available vehicles filtered by Location, Category, and Date range.
    Ensures vehicles are not rented during the requested timeframe.
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


@app.route('/vehicles/rented')
def get_rented_vehicles():
    """GETs all vehicles currently out on rent."""
    query = """
    SELECT v.*
    FROM vehicles v
    JOIN status s ON v.vehicle_id = s.vehicle_id
    WHERE s.status='RENTED'
    AND s.status_date_time= (
        SELECT MAX(s2.status_date_time)
        FROM status s2
        WHERE s2.vehicle_id=v.vehicle_id
    )
    """
    df = pd.read_sql(query, conn)
    return df.to_json(orient="records")

@app.route("/vehicle/<vrm>/history")
def get_vehicle_history(vrm):
    """GETs the complete status history for a specific vehicle."""
    vehicle_id = get_vehicle_id(vrm)
    if vehicle_id is None:
        return jsonify({"error": "Vehicle not found"}), 404

    query = """
    SELECT *
    FROM status
    WHERE vehicle_id = ?
    ORDER BY status_date_time DESC
    """
    df = pd.read_sql(query, conn, params=(vehicle_id,))
    return df.to_json(orient="records")


####################
# Rental Actions   #
####################


@app.route("/vehicles/<vrm>/rent")
def rent_vehicle(vrm):
    """Processes a rental transaction by updating the vehicle's status to RENTED."""
    vehicle_id = get_vehicle_id(vrm)
    if vehicle_id is None:
        return jsonify({"error": "Vehicle not found"}), 404

    current_status = get_current_status(vehicle_id)
    if current_status != "AVAILABLE":
        return jsonify({"error": f"Vehicle cannot be rented because status is {current_status}"}), 400


    customer_id = session.get('customer_id')
    if not customer_id:
        return jsonify({"error": "User not authenticated in session"}), 401

    latest = get_latest_status(vehicle_id)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO status (customer_id, vehicle_id, status_date_time, status_location, status)
        VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?)
        """,
        (
            customer_id, 
            vehicle_id,
            latest.iloc[0]["status_location"],
            "RENTED"
        )
    )
    conn.commit()
    return jsonify({"message": "Vehicle rented successfully"})

@app.route("/vehicles/<vrm>/return")
def return_vehicle(vrm):
    """Processes a return transaction by updating the vehicle's status back to AVAILABLE."""
    vehicle_id = get_vehicle_id(vrm)
    if vehicle_id is None:
        return jsonify({"error":"Vehicle not found"}), 404

    current_status = get_current_status(vehicle_id)
    if current_status != "RENTED":
        return jsonify({"error": f"Vehicle cannot be returned because status is {current_status}"}), 400

    latest = get_latest_status(vehicle_id)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO status (customer_id, vehicle_id, status_date_time, status_location, status)
        VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?)
        """,
        (
            latest.iloc[0]["customer_id"],
            vehicle_id,
            latest.iloc[0]["status_location"],
            "AVAILABLE"
        )
    )
    conn.commit()
    return jsonify({"message":"Vehicle returned successfully"})


####################
# Staff Analytics  #
####################

@app.route('/reports/branch')
@app.route('/api/reports/branch-inventory')
def get_branch_report():
    """GETs an aggregated count of all vehicles distributed by physical branch."""
    query = """
    SELECT s.status_location as branch, COUNT(*) as car_count
    FROM status s
    INNER JOIN (
        SELECT vehicle_id, MAX(status_date_time) as max_date 
        FROM status GROUP BY vehicle_id
    ) latest ON s.vehicle_id = latest.vehicle_id AND s.status_date_time = latest.max_date
    GROUP BY s.status_location
    """
    df = pd.read_sql(query, conn)
    return df.to_json(orient="records")

@app.route('/reports/status')
def get_status_report():
    """GETs an aggregated count of all vehicles categorized by their current operational status."""
    query = """
    SELECT status, COUNT(*) AS total
    FROM status s
    WHERE s.status_date_time= (
        SELECT MAX(s2.status_date_time)
        FROM status s2
        WHERE s2.vehicle_id=s.vehicle_id
    )
    GROUP BY status
    """
    df = pd.read_sql(query, conn)
    return df.to_json(orient="records")


####################
# Fleet Management #
####################

@app.route("/api/vehicles/add", methods=["POST"])
def add_vehicle():
    """Adds a new vehicle to the fleet and sets its initial status to AVAILABLE."""
    data = request.get_json()
    cursor = conn.cursor()
    try:
        # Check for VRM duplication
        check = pd.read_sql("SELECT vehicle_id FROM vehicles WHERE UPPER(vrm) = ?", conn, params=(data['vrm'].upper(),))
        if not check.empty:
            return jsonify({"error": "Vehicle VRM already exists!"}), 400

        # Insert vehicle spec details
        cursor.execute(
            "INSERT INTO vehicles (vrm, make, model, category, numberSeats, fuelEconomy, colour, year, dayRate) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (data['vrm'].upper(), data['make'], data['model'], data['category'], 
             data['numberSeats'], data.get('fuelEconomy', 0), data['colour'], data['year'], data['dayRate'])
        )
        
        vehicle_id = cursor.lastrowid
        location = data.get('location', 'Bristol') 
        
        # Initialize vehicle in 'AVAILABLE' state
        cursor.execute(
            "INSERT INTO status (customer_id, vehicle_id, status_date_time, status_location, status) "
            "VALUES (1, ?, CURRENT_TIMESTAMP, ?, 'AVAILABLE')",
            (vehicle_id, location)
        )
        conn.commit()
        return jsonify({"message": "Vehicle added successfully and marked as AVAILABLE!"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400

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

@app.route("/vehicles/<vrm>", methods=["DELETE"])
def delete_vehicle(vrm):
    """Permanently deletes a vehicle and its entire operational history."""
    vehicle_id = get_vehicle_id(vrm)
    if vehicle_id is None:
        return jsonify({"error":"Vehicle not found"}), 404

    cursor = conn.cursor()
    # Remove dependencies first
    cursor.execute("DELETE FROM status WHERE vehicle_id = ?", (vehicle_id,))
    cursor.execute("DELETE FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
    conn.commit()

    return jsonify({"message":"Vehicle deleted successfully"})


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
            
            return jsonify({
                "success": True, 
                "message": "Welcome Admin!",
                "redirect_url": "/staffhome"
            }), 200

        # 2. STANDARD CASE: Customer Login
        query = "SELECT * FROM customers WHERE email = ?"
        df = pd.read_sql(query, conn, params=(email,))
        
        if not df.empty:
            customer = df.iloc[0].to_dict()
            session['logged_in'] = True
            
            # Resolve ID format discrepancy
            if 'customer_id' in customer:
                session['customer_id'] = int(customer['customer_id'])
            elif 'customerId' in customer:
                session['customer_id'] = int(customer['customerId'])
            else:
                session['customer_id'] = 1
                
            session['customer_name'] = str(customer.get('first_name', 'User'))
            session['role'] = 'customer' 
            
            return jsonify({
                "success": True, 
                "message": f"Welcome back, {session['customer_name']}!",
                "redirect_url": "/" 
            }), 200
        else:
            return jsonify({"success": False, "error": "Email not found. Please check or sign up."}), 401
            
    except Exception as e:
        print("Login Error:", str(e))
        return jsonify({"success": False, "error": f"SQL/Python Error: {str(e)}"}), 500


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

        # Generate a new sequential customerId (MAX + 1)
        cursor.execute("SELECT MAX(customerId) FROM customers")
        max_id_result = cursor.fetchone()[0]
        new_customer_id = 1 if max_id_result is None else max_id_result + 1

        # Insert new customer record
        cursor.execute(
            """
            INSERT INTO customers (
                customerId, first_name, last_name, dob, gender, email, 
                address, city, country, drivingLicenseNumber, 
                passportNumber, LicenseRetrictions
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                new_customer_id, data['first_name'], data['last_name'], data['dob'], data['gender'], 
                data['email'], data['address'], data['city'], data['country'], 
                data['drivingLicenseNumber'], data['passportNumber'], 
                data.get('LicenseRetrictions', 'None')
            )
        )
        conn.commit()
        
        return jsonify({
            "success": True, 
            "message": "Account created successfully! You can now log in.",
            "redirect_url": "/login"
        }), 201

    except Exception as e:
        conn.rollback()
        print("Signup Error:", str(e))
        return jsonify({"success": False, "error": "Database error: " + str(e)}), 500


@app.route("/logout")
@app.route("/api/logout", methods=["POST"])
def logout():
    """Clears the current user session and redirects to the public homepage."""
    session.clear() 
    
    # Handle API calls vs standard link clicks
    if request.method == "POST":
        return jsonify({"success": True, "message": "Logged out successfully"}), 200
    return redirect(url_for('home_page')) 

# Application Entry Point
if __name__ == "__main__":
    app.run(debug=True)