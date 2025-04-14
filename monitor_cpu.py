import psutil
import time

def monitor_cpu_realtime():
    while True:
        cpu_usage = psutil.cpu_percent(interval=1, percpu=True)
        for i, usage in enumerate(cpu_usage):
            print(f"CPU {i+1}: {usage}%", end="\t")
        print("\n")
        time.sleep(1)

monitor_cpu_realtime()
