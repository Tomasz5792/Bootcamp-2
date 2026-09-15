from flask import Flask, jsonify
import pandas as pd
 
app = Flask(__name__)
 
vehicles = pd.read_csv('Data/vehicle.csv')
print(vehicles.head())
 
# Home page
@app.route('/')
def home():
    return "Car-Go API Running"

# Get all vehicles
@app.route('/vehicle')
def get_vehicles():
    return vehicles.to_json(orient='records')

# Get a specific vehicle by its VRM
@app.route('/vehicle/<vrm>')
def get_vehicle_by_vrm(vrm):
    vehicle = vehicles[vehicles['vrm'] == vrm]
    if vehicle.empty:
        return jsonify({'error': 'Vehicle not found'}), 404
    return vehicle.to_json(orient='records')
app.run(debug=True)

