# Opens a Serial Connection to stop the Devkit

import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200)
ser.write(b"STOP\n")
time.sleep(0.1)
ser.close()