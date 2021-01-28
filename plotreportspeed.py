import numpy as np
import matplotlib.pyplot as plt
import csv
import statistics

index_collumn = []
speed1_collumn = []
speed2_collumn = []
speed3_collumn = []
speed4_collumn = []
speed5_collumn = []
speed6_collumn = []
speed7_collumn = []
speed8_collumn = []
speed9_collumn = []
speed10_collumn = []
meanspeed_collumn = []

with open('speeddata.txt') as csvfile:
    csvfilereader = csv.reader(csvfile, delimiter=' ')
    for line in csvfilereader:
        # index_collumn.append(int(line[0]))
        speed1_collumn.append(int(line[0]))
        speed2_collumn.append(int(line[1]))
        speed3_collumn.append(int(line[2]))
        speed4_collumn.append(int(line[3]))
        speed5_collumn.append(int(line[4]))
        speed6_collumn.append(int(line[5]))
        speed7_collumn.append(int(line[6]))
        speed8_collumn.append(int(line[7]))
        speed9_collumn.append(int(line[8]))
        speed10_collumn.append(int(line[9]))
        meanspeed_collumn.append(statistics.median([int(line[1]), int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6]), int(line[7]), int(line[8]), int(line[9]), int(line[0])])

# print(size_collumn[:2])
index_collumn = range(len(speed1_collumn))
figure_length = 300

plt.plot(index_collumn[:figure_length], meanspeed_collumn[:figure_length], label="observed size")
# print(np.arange(int(min(index_collumn[:figure_length])), int(max(index_collumn[:figure_length]))+1, 20.0))
plt.xticks(np.arange(int(min(index_collumn[:figure_length])), int(max(index_collumn[:figure_length]))+1, 50.0))

plt.xlabel('Blocks Used')
plt.ylabel('Database Size')

plt.plot(index_collumn[:figure_length], (np.array(index_collumn[:figure_length])*323)+20480, label="(blocks*323)+20480")

plt.title("Database Size Scaling")

plt.legend()

plt.show(block=True)
