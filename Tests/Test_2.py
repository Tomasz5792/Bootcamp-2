# For individual vehicles:
# - show details of specific vehicle (according to car reg)
# - rent a specific vehicle
# - return a specific vehicle
# - add a new vehicle to the rental fleet
# - remove a specific vehicle from the rental fleet

# For multiple vehicles:
# - show all vehicles
# - show vehicles available for rent (preferably organised per branch)
# - show vehicles currently rented out (preferably organised per branch)

#http://127.0.0.1:5000/

from flask import Flask, jsonify
import json

app = Flask(__name__)

with open("Data/vehicle.json") as vehicle_file:
    data = json.load(vehicle_file)

@app.route("/")
def home_page():
    return "<p>Car company home page.</p>"

# Get all vehicles
# #http://127.0.0.1:5000/vehicles
@app.route("/vehicles")
def get_vehicles():
    return jsonify(data)

# Get a specific vehicle by its vin
# #http://127.0.0.1:5000/vehicles/JN1CV6EK8EM995741
@app.route("/vehicles/<vin>")
def get_vehicles_by_vin(vin):
    for vehicle in data:
        if vehicle["vin"] == vin:
            return jsonify(vehicle)
    return jsonify({"error": "Vehicle not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)