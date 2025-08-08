import numpy as np
import json
import os
import serial
import time
import matplotlib.pyplot as plt
from datetime import datetime

from useful_functions import * 


# Load Settings from Json file
with open('settings.json', 'r') as f:
    settings = json.load(f)

mode = settings['mode']
measurement_time = settings['measurement_time']
results_path = settings['results_path']

# Setup the serial link
ser = serial.Serial('/dev/ttyACM0', 115200)
ser.write(b"STOP\n")
time.sleep(0.1)

# Calibration Setup
if mode == "receiver":
    calibration_string1 = "CALKEY ant0.ch5.ant_delay " + settings['receiver_calibration']['ch5_antenna_delay'] + "\n"
    calibration_string2 = "CALKEY ant0.ch9.ant_delay " + settings['receiver_calibration']['ch9_antenna_delay'] + "\n"

elif mode == "initiator":
    calibration_string1 = "CALKEY ant0.ch5.ant_delay " + settings['initiator_calibration']['ch5_antenna_delay'] + "\n"
    calibration_string2 = "CALKEY ant0.ch9.ant_delay " + settings['initiator_calibration']['ch9_antenna_delay'] + "\n"

else:
    raise Exception("Error, unknown mode in settings.json, only 'receiver' and 'initiator' are authorized")

ser.write(calibration_string1.encode('ascii'))
time.sleep(0.1)
ser.write(calibration_string2.encode('ascii'))
time.sleep(0.1)



to_search = b"distance[cm]="
length = len(to_search)

results = []
timestamps = []

# Read UWB transmissions
ser.write(b"STOP\n")
time.sleep(0.1)
ser.write(b"RESPF CHAN=5 PRFSET=BPRF5 BLOCK=300\n")
start_measuring = time.perf_counter()
timestamp = 0

while timestamp < measurement_time:
    line = ser.readline()
    print(line)
    timestamp = time.perf_counter() - start_measuring

    start = line.find(to_search)
    if start != -1:
        start += length

        end = line.find(b",", start)
        if end != -1:
            results.append(get_number_from_string(line, start, end, int))
            timestamps.append(timestamp)

        else:
            end = line.find(b"]", start)
            if end != -1:
                results.append(get_number_from_string(line, start, end, int))
                timestamps.append(timestamp)

ser.write(b"STOP\n")
time.sleep(0.1)
ser.close()

directory = os.getcwd()
os.makedirs(directory+"/"+settings['results_path'], exist_ok=True)


date_timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
data = np.asarray([timestamps, results])
filename = directory+"/Results/res_"+date_timestamp+".csv"


np.savetxt(filename, data, delimiter=",")

fig, ax = plt.subplots()
ax.plot(timestamps, results, marker = 'o')
ax.set_xlabel("Elapsed time (s)")
ax.set_ylabel("Distance (cm)")

plt.show()
