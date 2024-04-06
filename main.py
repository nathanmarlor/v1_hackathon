import time
from flask import Flask, jsonify, request

app = Flask(__name__)

# Define the devices and their fixed power usage
devices = {
    'Light': 5,
    'Fridge': 50,
    'TV': 100,
    'Oven': 1500
}

# Global variables
switched_on = []
combined_load_history = []
detected_devices_history = []

# Simulated ML model for device detection
def detect_devices(combined_load):
    detected = []
    remaining_load = combined_load

    # Sort devices by power in descending order
    sorted_devices = sorted(devices.items(), key=lambda x: x[1], reverse=True)

    for device, power in sorted_devices:
        if power <= remaining_load:
            detected.append(device)
            remaining_load -= power

    return detected

# API endpoint to get the current state
@app.route('/state', methods=['GET'])
def get_state():
    return jsonify({
        'combined_load': combined_load_history[-1] if combined_load_history else 0,
        'switched_on_devices': switched_on,
        'detected_devices': detected_devices_history[-1] if detected_devices_history else []
    })

# API endpoint to turn a device on
@app.route('/devices/<device>/on', methods=['POST'])
def turn_device_on(device):
    if device in devices:
        if device not in switched_on:
            switched_on.append(device)
        return jsonify({'message': f'{device} turned on'})
    else:
        return jsonify({'message': 'Device not found'}), 404

# API endpoint to turn a device off
@app.route('/devices/<device>/off', methods=['POST'])
def turn_device_off(device):
    if device in devices:
        if device in switched_on:
            switched_on.remove(device)
        return jsonify({'message': f'{device} turned off'})
    else:
        return jsonify({'message': 'Device not found'}), 404

# Simulation loop
def simulation_loop():
    while True:
        # Calculate combined load
        combined_load = sum(devices[device] for device in switched_on)

        # Detect devices using the simulated ML model
        detected_devices = detect_devices(combined_load)

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