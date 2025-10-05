import serial
import time

# Date de configurare
serial_port = 'COM5'
baud_rate = 115200
timeout = 1  
output_file = "testplumb2.txt"

# Deschide conexiunea cu interfata seriala
ser = serial.Serial(serial_port, baud_rate, timeout=timeout)

try:
    with open(output_file, 'a') as file:
        print(f"Reading from {serial_port} at {baud_rate} baud rate... Press Ctrl+C to stop.")
        
        while True:
            # Citeste datele din serial
            data = ser.readline().decode('utf-8').strip()
        


            if data:
                # Obtine ora curenta
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                
                # Scrie datele si ora in fisier
                file.write(f"{timestamp} - {data}\n")
                file.flush()
                
                # Printeaza optional in consola
                # print(f"{timestamp} - {data}")

except KeyboardInterrupt:
    # Oprire colectare de date cu CTRL+C
    print("\nData collection stopped by user.")

finally:
    # Inchide interfata seriala
    ser.close()
    print(f"Serial port {serial_port} closed. Data saved to {output_file}.")

