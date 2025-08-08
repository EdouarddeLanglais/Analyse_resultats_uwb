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

# Setup
if mode == "receiver":
    calibration_string1 = "CALKEY ant0.ch5.ant_delay " + settings['receiver_calibration']['ch5_antenna_delay'] + "\n"
    calibration_string2 = "CALKEY ant0.ch9.ant_delay " + settings['receiver_calibration']['ch9_antenna_delay'] + "\n"
    com_mode = "RESPF"

elif mode == "initiator":
    calibration_string1 = "CALKEY ant0.ch5.ant_delay " + settings['initiator_calibration']['ch5_antenna_delay'] + "\n"
    calibration_string2 = "CALKEY ant0.ch9.ant_delay " + settings['initiator_calibration']['ch9_antenna_delay'] + "\n"
    com_mode = "INITF"

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

# Start ranging
ser.write(b"STOP\n")
time.sleep(0.1)

com_settings = settings['com_settings']

com_channel = "CHAN="+str(com_settings['channel'])              # UWB channel
com_prf = "PRFSET="+com_settings['prf']                         # Pulse Repetition Frequency set
com_pcode = "PCODE="+str(com_settings['preamble_code'])         # Preable Code Index
com_slot = "SLOT="+str(com_settings['ranging_slot_duration'])   # Ranging slot duration in RSTU, 1ms = 1200 RSTU
com_block = "BLOCK="+str(com_settings['ranging_block'])         # Ranging block duration
com_round = "ROUND="+str(com_settings['round_duration'])        # Number of ranging operation in one slot
com_ranging_type = "RRU="+com_settings['ranging_type']          # Ranging type preferred

com_line = com_mode+" "+com_channel+" "+com_prf+" "+com_pcode+" "+com_slot+" "+com_block+" "+com_round+" "+com_ranging_type+"\n"

ser.write(com_line.encode('ascii'))
time.sleep(0.1)
ser.write(b"STOP\n")
time.sleep(0.1)
ser.write(b"SAVE\n")
time.sleep(0.1)
ser.write(com_line.encode('ascii'))

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
