import time
from flask import Flask, jsonify, request
import pickle
import random
app = Flask(__name__)

# Define the devices and their fixed power usage
devices = {
    'Light': random.uniform(20,30),
    'Fridge': random.uniform(50,55),
    'TV': random.uniform(500,505),
    'Oven': random.uniform(2000,2005)
}

# Global variables
switched_on = []
combined_load_history = []
detected_devices_history = []
# Load the trained model from the file
with open('model_new.pkl', 'rb') as f:
    model = pickle.load(f)
# # Simulated ML model for device detection
# def detect_devices(combined_load):
#     detected = []
#     remaining_load = combined_load

#     # Sort devices by power in descending order
#     sorted_devices = sorted(devices.items(), key=lambda x: x[1], reverse=True)

#     for device, power in sorted_devices:
#         if power <= remaining_load:
#             detected.append(device)
#             remaining_load -= power

#     return detected

def detect_devices(combined_load, power_change):
    # Prepare the input data
    input_data = [[combined_load, power_change]]
    
    # Use the model to predict the device states
    predicted_label = model.predict(input_data)[0]
    
    # Convert the predicted label to a list of devices
    detected_devices = [device for device, state in zip(devices, predicted_label) if state == '1']
    
    return detected_devices

# API endpoint to get the current state
@app.route('/state', methods=['GET'])
def get_state():
    response =  jsonify({
        'combined_load': combined_load_history[-1] if combined_load_history else 0,
        'switched_on_devices': switched_on,
        'detected_devices': detected_devices_history[-1] if detected_devices_history else []
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# API endpoint to turn a device on
@app.route('/devices/<device>/on', methods=['POST','GET'])
def turn_device_on(device):
    if device in devices:
        if device not in switched_on:
            switched_on.append(device)
        
        response = jsonify({'message': f'{device} turned on'})
    else:
        response= jsonify({'message': 'Device not found'}), 404
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# API endpoint to turn a device off
@app.route('/devices/<device>/off', methods=['POST','GET'])
def turn_device_off(device):
    if device in devices:
        if device in switched_on:
            switched_on.remove(device)
        response= jsonify({'message': f'{device} turned off'})
    else:
        response= jsonify({'message': 'Device not found'}), 404
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Simulation loop
def simulation_loop():
    prev_load = 0
    while True:
        # Calculate combined load
        combined_load = sum(devices[device] for device in switched_on)
        # Calculate power change
        power_change = combined_load - prev_load
        prev_load = combined_load

        detected_devices = detect_devices(combined_load, power_change)

        # Store the current combined load and detected devices
        combined_load_history.append(combined_load)
        detected_devices_history.append(detected_devices)

        # Limit the history to the last 30 seconds
        if len(combined_load_history) > 30:
            combined_load_history.pop(0)
            detected_devices_history.pop(0)

        # Output the current state
        print(f"Second: {len(combined_load_history)}")
        print(f"Combined Load: {combined_load} watts")
        print(f"Switched On Devices: {', '.join(switched_on)}")
        print(f"Detected Devices: {', '.join(detected_devices)}")
        print("----------------------")

        # Wait for 1 second before the next iteration
        time.sleep(1)

if __name__ == '__main__':
    # Start the simulation loop in a separate thread
    import threading
    simulation_thread = threading.Thread(target=simulation_loop)
    simulation_thread.start()

    # Run the Flask app
    app.run()