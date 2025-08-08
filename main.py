import numpy as np
import json
import serial
import time
import matplotlib.pyplot as plt
from datetime import datetime

from useful_functions import * 

ser = serial.Serial('/dev/ttyACM0', 115200)
measurement_time = 180 #s
to_search = b"distance[cm]="
length = len(to_search)


results = []
timestamps = []

# Read UWB transmissions
ser.write(b"STOP\n")
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
ser.close()

date_timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
data = np.asarray([timestamps, results])
filename = "/Results/res_"+date_timestamp+".csv"
np.savetxt(filename, data, delimiter=",")

fig, ax = plt.subplots()
ax.plot(timestamps, results, marker = 'o')
ax.set_xlabel("Elapsed time (s)")
ax.set_ylabel("Distance (cm)")

plt.show()
