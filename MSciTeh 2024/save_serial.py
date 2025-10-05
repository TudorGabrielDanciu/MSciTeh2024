import serial
import time

# Configure the serial connection
serial_port = 'COM5'
baud_rate = 115200
timeout = 1  # Read timeout in seconds

# Open the serial connection
ser = serial.Serial(serial_port, baud_rate, timeout=timeout)

# Open the output file
output_file = "testplumb2.txt"

try:
    with open(output_file, 'a') as file:
        print(f"Reading from {serial_port} at {baud_rate} baud rate... Press Ctrl+C to stop.")
        
        while True:
            # Read data from the serial port
            data = ser.readline().decode('utf-8').strip()
        


            if data:
                # Get the current timestamp
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                
                # Write the timestamp and data to the file
                file.write(f"{timestamp} - {data}\n")
                file.flush()
                
                # Optionally print to console
                print(f"{timestamp} - {data}")

except KeyboardInterrupt:
    # Handle the Ctrl+C gracefully
    print("\nData collection stopped by user.")

finally:
    # Ensure the serial port is closed properly
    ser.close()
    print(f"Serial port {serial_port} closed. Data saved to {output_file}.")

