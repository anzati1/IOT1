import json
import time
import paho.mqtt.client as mqtt

# MQTT Configuration
id = 'abegeorge'  # Unique ID for this device
client_telemetry_topic = id + '/telemetry'
server_command_topic = id + '/commands'
client_name = id + 'temperature_server'

# Create MQTT client and connect
mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()
print("MQTT server connected!")

def handle_telemetry(client, userdata, message):
    """Handle incoming telemetry messages"""
    try:
        payload = json.loads(message.payload.decode())
        print("Message received:", payload)
        
        # Send command based on temperature
        command = {'led_on': payload['temperature'] > 25}
        print("Sending command:", command)
        client.publish(server_command_topic, json.dumps(command))
    except Exception as e:
        print(f"Error handling telemetry: {e}")

# Subscribe to telemetry topic
mqtt_client.subscribe(client_telemetry_topic)
mqtt_client.on_message = handle_telemetry

def main():
    """Main function to keep the server running"""
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nServer terminated by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    main() 