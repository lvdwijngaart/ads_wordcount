import numpy as np
import matplotlib.pyplot as plt
filepath = "shared_output/latencies.txt"
# Read all lines
with open(filepath, "r") as f:
    lines = f.readlines()
data  = list(  [[] for _ in range(20)]  )  # 20 clients

for idx, line in enumerate(lines):

    latency = float(line.strip())
    data[idx % 20].append(latency)


averages = [sum(client_data) / len(client_data) if client_data else 0 for client_data in data]
print(averages)

plt.figure(figsize=(12, 6))
plt.bar(range(1, len(averages) + 1), averages)
plt.xlabel('Request Index')
plt.ylabel('Average Latency (ms)')
plt.title('Average Latency of Request 1 to 20')
plt.xticks(range(1, len(averages) + 1))
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()


