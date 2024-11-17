import psutil
import time
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates, nvmlDeviceGetMemoryInfo

def get_gpu_usage():
    try:
        nvmlInit()
        handle = nvmlDeviceGetHandleByIndex(0)  # Assuming 1 GPU; change index if multiple GPUs
        utilization = nvmlDeviceGetUtilizationRates(handle)
        memory = nvmlDeviceGetMemoryInfo(handle)
        return {
            "gpu_utilization_percent": utilization.gpu,  # GPU utilization percentage
            "gpu_memory_used_mb": memory.used / 1024**2,  # Used GPU memory in MB
            "gpu_memory_total_mb": memory.total / 1024**2  # Total GPU memory in MB
        }
    except Exception as e:
        return {"gpu_error": str(e)}

def get_system_usage():
    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    gpu = get_gpu_usage()

    system_stats = {
        "cpu_usage": cpu_usage,  # CPU usage percentage
        "ram_usage_percent": ram.percent,
        "ram_used_mb": ram.used / 1024**2,
        "ram_total_mb": ram.total / 1024**2,
        "hdd_usage_percent": disk.percent,
        "hdd_used_gb": disk.used / 1024**3,
        "hdd_total_gb": disk.total / 1024**3
    }

    if "gpu_error" in gpu:
        system_stats["gpu_error"] = gpu["gpu_error"]
    else:
        system_stats.update({
            "gpu_utilization_percent": gpu["gpu_utilization_percent"],
            "gpu_memory_used_mb": gpu["gpu_memory_used_mb"],
            "gpu_memory_total_mb": gpu["gpu_memory_total_mb"]
        })

    return system_stats

def main():
    """Return a single snapshot of system statistics."""
    return get_system_usage()

if __name__ == "__main__":
    monitor_system()  # If run independently, it will monitor in a loop.
