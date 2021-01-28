import numpy as np
import matplotlib.pyplot as plt
import csv

index_collumn = []
size_collumn = []

with open('dbsize.txt') as csvfile:
    csvfilereader = csv.reader(csvfile, delimiter=' ')
    for line in csvfilereader:
        index_collumn.append(int(line[0]))
        size_collumn.append(int(line[1]))

print(size_collumn[:2])

figure_length = 300

plt.plot(index_collumn[:figure_length], size_collumn[:figure_length], label="observed size")
# print(np.arange(int(min(index_collumn[:figure_length])), int(max(index_collumn[:figure_length]))+1, 20.0))
plt.xticks(np.arange(int(min(index_collumn[:figure_length])), int(max(index_collumn[:figure_length]))+1, 50.0))

plt.xlabel('Blocks Used')
plt.ylabel('Database Size')

plt.plot(index_collumn[:figure_length], (np.array(index_collumn[:figure_length])*323)+20480, label="(blocks*323)+20480")

plt.title("Database Size Scaling")

plt.legend()

plt.show(block=True)
