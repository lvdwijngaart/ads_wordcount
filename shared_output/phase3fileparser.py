from datetime import datetime
from math import ceil
import numpy as np
import matplotlib.pyplot as plt

filepath = "shared_output/latencies.txt"


# Read all lines
with open(filepath, "r") as f:
    lines = f.readlines()

timestamps = np.zeros(len(lines))
latencies = np.zeros(len(lines))
origin = None
for idx, line in enumerate(lines):
    parts = line.strip().split(",")
    timestamp = datetime.fromisoformat(parts[0])
    latency = float(parts[1])
    if not origin:
        origin = timestamp
    time = (timestamp - origin).total_seconds()
    timestamps[idx] = time
    latencies[idx] = latency

plt.figure(figsize=(12, 6))
plt.scatter(timestamps, latencies)
plt.xlabel("Time")
plt.ylabel("Latency (ms)")
plt.title("Average Latency of Request 1 to 20")
# plt.xticks(range(1, len(averages) + 1))
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()
