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


from flask import Flask, jsonify, render_template
import pandas as pd
#import json
from Create_SQL import create_database, check_database


#app = Flask(__name__)
app = Flask(__name__, template_folder="../Frontend/templates", static_folder="../Frontend/static") #frontend html

conn = create_database()
#check_database(conn)  # shows the sql tables for debugging purposes


#############
### Pages ###
#############

#Login.html
#http://127.0.0.1:5000/
@app.route("/homelogin")
def login_page():
    return render_template("HomeLogin.html")

#signup page
#SignUp.html
#http://127.0.0.1:5000/signup
@app.route("/signup")
def signup_page():
    return render_template("SignUp.html")



#homepage
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




##########################
### API json endpoints ###
##########################

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
    df = pd.read_sql(f"SELECT * FROM vehicles WHERE vrm = '{vrm}'", conn)
    if df.empty:
        return jsonify({'error': 'Vehicle not found'}), 404
    return df.to_json(orient="records")




# doesn't work needs updating using status table.  
# dont use status == AVAILABLE join vehicules to status to get the last status 

# show vehicles available for rent (preferably organised per branch)
#http://127.0.0.1:5000/vehicle/available
@app.route('/vehicle/available')
def get_available_vehicles():
    """GETs all available vehicles and returns as a JSON

    Args:
        None

    Returns:
        JSON: JSON object containing all available vehicles in the database
    """
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




# doesn't work needs updating using status table.  
# dont use status == AVAILABLE join vehicules to status to get the last status 
# Extension: find availiable over a certion perion of time.

# show vehicles currently rented out (preferably organised per branch)
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




# doesn't work needs updating using status table.  
# dont use status == AVAILABLE, join vehicules to status and location.
# Extension: find availiable over a certion perion of time.

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
    SELECT branch,
           COUNT(*) AS total_vehicles
    FROM vehicles
    GROUP BY branch
    """
    df = pd.read_sql(query,conn)
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
    query = """SELECT status,COUNT(*) AS totalFROM vehiclesGROUP BY status """

    df = pd.read_sql(query,conn)

    return df.to_json(orient="records")



if __name__ == "__main__":
    app.run(debug=True)
    