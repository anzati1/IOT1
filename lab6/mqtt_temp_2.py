import time
import json
import paho.mqtt.client as mqtt
from gpiozero import LED
import os
import glob

class DS18B20:
    def __init__(self):
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        
        base_dir = '/sys/bus/w1/devices/'
        try:
            device_folder = glob.glob(base_dir + '28*')[0]
            self.device_file = device_folder + '/w1_slave'
        except IndexError:
            print("cannot find DS18B20 sensor")
            self.device_file = None

    def read_temp_raw(self):
        try:
            with open(self.device_file, 'r') as f:
                lines = f.readlines()
            return lines
        except (FileNotFoundError, TypeError):
            print("Error: Could not read from sensor")
            return None

    def read_temp(self):
        if self.device_file is None:
            return None, None

        lines = self.read_temp_raw()
        if lines is None:
            return None, None
            
        try:
            while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = self.read_temp_raw()
                if lines is None:
                    return None, None

            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                temp_f = temp_c * 9.0 / 5.0 + 32.0
                return round(temp_c, 2), round(temp_f, 2)
            
        except (IndexError, ValueError) as e:
            print(f"Error reading temperature: {str(e)}")
            return None, None

# Initialize LED and Temperature Sensor
led = LED(17)  # Using GPIO17 for the LED
sensor = DS18B20()  # Create instance of temperature sensor class

# MQTT Configuration
id = 'abegeorge'  # Unique ID for this device
client_name = id + 'temperature_client'
client_telemetry_topic = id + '/telemetry'

# Create MQTT client and connect
mqtt_client = mqtt.Client(client_name, protocol=mqtt.MQTTv5)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()
print("MQTT connected!")

def main():
    """Main function to monitor temperature and send telemetry"""
    try:
        while True:
            # Read temperature
            celsius, fahrenheit = sensor.read_temp()
            
            if celsius is not None:
                # Create telemetry message with both Celsius and Fahrenheit
                telemetry = {
                    'temperature_c': celsius,
                    'temperature_f': fahrenheit,
                    'timestamp': time.time()
                }
                
                # Send telemetry to MQTT broker
                mqtt_client.publish(client_telemetry_topic, json.dumps(telemetry))
                print(f"Sent telemetry: {telemetry}")
                
                # Control LED based on temperature
                if celsius > 25:
                    led.on()
                    print("Temperature > 25°C, LED ON")
                else:
                    led.off()
                    print("Temperature ≤ 25°C, LED OFF")
            else:
                print("Failed to read temperature, trying again")
            
            # Wait for 3 seconds before next reading
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Cleanup
        led.close()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    main() 