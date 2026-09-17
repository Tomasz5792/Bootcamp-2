from flask import Flask, jsonify, request
import pandas as pd

app = Flask(__name__)

# Load the vehicle data from a CSV file
vehicles = pd.read_csv('vehicle.csv')
print(vehicles.head())

API_KEYS = {
"employee123": "EMPLOYEE",
"customer123": "CUSTOMER"
}

# This runs before EVERY request
@app.before_request
def authenticate():

# Allow access to homepage without a key
    if request.path == "/":
        return
    api_key = request.headers.get("X-API-Key")

    if api_key not in API_KEYS:
        return jsonify({"error": "Invalid API Key"}), 401

# Define the API endpoints
# HomePage
@app.route('/')
def home():
    return "Car-Go API Running"

# Get all vehicles
@app.route('/vehicle')
def get_vehicles():
    return vehicles.to_json(orient='records')

# Get a vehicle by its Registration Mark (VRM)
@app.route('/vehicle/<vrm>')
def get_vehicle_by_vrm(vrm):
    vehicle = vehicles[vehicles['vrm'] == vrm]
    if vehicle.empty:
        return jsonify({'error': 'Vehicle not found'}), 404
    return vehicle.to_json(orient='records')

# Get available vehicles
@app.route('/vehicle/available')
def get_available_vehicles():
    available_vehicles = vehicles[vehicles['status'] == "AVAILABLE"]
    return available_vehicles.to_json(orient='records')

# Get rented vehicles
@app.route('/vehicle/rented')
def get_rented_vehicles():
    rented_vehicles = vehicles[vehicles['status'] == "RENTED"]
    return rented_vehicles.to_json(orient='records')

# Get reports for branch and status
@app.route('/reports/branch')
def get_branch_report():
    branch_report = vehicles["branch"].value_counts()
    return branch_report.to_json()

# Get reports for status
@app.route('/reports/status')
def get_status_report():
    status_report = vehicles["status"].value_counts()
    return status_report.to_json()

# Rent a vehicle
@app.route("/vehicle/<vrm>/rent")
def rent_vehicle(vrm):

    # Find vehicle regardless of upper/lower case
    mask = vehicles["vrm"].str.upper() == vrm.upper()

    # Check vehicle exists
    if not mask.any():
        return jsonify({
            "error": "Vehicle not found"
        }), 404

    # Get current status
    current_status = vehicles.loc[
        mask,
        "status"
    ].iloc[0]

    # Vehicle must be available before it can be rented
    if current_status != "AVAILABLE":
        return jsonify({
            "error": f"Vehicle cannot be rented because status is {current_status}"
        }), 400

    # Update status
    vehicles.loc[
        mask,
        "status"
    ] = "RENTED"

    # Return updated vehicle record
    return vehicles.loc[mask].to_json(
        orient="records"
    )

# Return a vehicle
@app.route("/vehicle/<vrm>/return")
def return_vehicle(vrm):

    mask = vehicles["vrm"].str.upper() == vrm.upper()

    if not mask.any():
        return jsonify({
            "error": "Vehicle not found"
        }), 404

    current_status = vehicles.loc[
        mask,
        "status"
    ].iloc[0]

    if current_status != "RENTED":
        return jsonify({
            "error": f"Vehicle cannot be returned because status is {current_status}"
        }), 400

    vehicles.loc[
        mask,
        "status"
    ] = "AVAILABLE"

    return vehicles.loc[mask].to_json(
        orient="records"
    )

@app.route("/vehicle", methods=["POST"])
def add_vehicle():
    global vehicles
    new_vehicle = request.get_json()
    vehicles = pd.concat([vehicles, pd.DataFrame([new_vehicle])], ignore_index=True)
    return jsonify({"message": "vehicle added successfully"}), 201

@app.route("/vehicle/<vrm>", methods=["DELETE"])
def delete_vehicle(vrm):
    global vehicles
    mask = vehicles["vrm"].str.upper() == vrm.upper()

    if not mask.any():
        return jsonify({
            "error": "Vehicle not found"
        }), 404

    vehicles = vehicles[~mask]
    return jsonify({"message": "vehicle deleted successfully"}), 200

# Run the Flask application
app.run(debug=True)