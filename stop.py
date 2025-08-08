#
# Opens a Serial Connection to stop the Devkit
#
#########################################

import serial

ser = serial.Serial('/dev/ttyACM0', 115200)
ser.write(b"STOP\n")
ser.close()