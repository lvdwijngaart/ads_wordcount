from datetime import datetime
from math import ceil
import numpy as np
import matplotlib.pyplot as plt

filepath = "shared_output/latencies.txt"


def bin_by(x, y, nbins=30):
    """
    Bin x by y.
    Returns the binned "x" values and the left edges of the bins
    """
    bins = np.linspace(y.min(), y.max(), nbins + 1)
    # To avoid extra bin for the max value
    bins[-1] += 1

    indicies = np.digitize(y, bins)

    output = []
    for i in range(1, len(bins)):
        output.append(x[indicies == i])

    # Just return the left edges of the bins
    bins = bins[:-1]

    return output, bins


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

binned_vals, bins = bin_by(
    latencies,
    timestamps,
)
averages = [np.average(x) for x in binned_vals]

plt.figure(figsize=(12, 6))
plt.scatter(timestamps, latencies)
plt.plot(bins, averages)
plt.xlabel("Time")
plt.ylabel("Latency (ms)")
plt.title("Average Latency of Request 1 to 20")

# plt.xticks(range(1, len(averages) + 1))
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()
