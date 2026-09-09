import psutil
from typing import Dict, Any

def check_system_health() -> Dict[str, Any]:
    """
    Inspects real CPU and Memory utilization percentages using psutil.

    Returns structured system health diagnostic metrics.
    """
    try:
        # Sample CPU over 0.5s interval
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()

        ram_percent = memory.percent
        ram_total_gb = round(memory.total / (1024 ** 3), 1)
        ram_used_gb = round(memory.used / (1024 ** 3), 1)
        ram_free_gb = round(memory.available / (1024 ** 3), 1)

        status = "HEALTHY"
        if cpu_percent > 85 or ram_percent > 85:
            status = "HIGH RESOURCE USAGE"
        elif cpu_percent > 70 or ram_percent > 70:
            status = "MODERATE ELEVATED LOAD"

        return {
            "tool_name": "System Health Tool",
            "cpu_usage_percent": cpu_percent,
            "ram_usage_percent": ram_percent,
            "ram_total_gb": ram_total_gb,
            "ram_used_gb": ram_used_gb,
            "ram_free_gb": ram_free_gb,
            "status": status,
            "details": f"CPU Usage: {cpu_percent}% | RAM Usage: {ram_percent}% ({ram_used_gb}/{ram_total_gb} GB)"
        }
    except Exception as e:
        return {
            "tool_name": "System Health Tool",
            "status": "ERROR",
            "details": f"Failed to sample system health: {str(e)}"
        }

if __name__ == "__main__":
    print(check_system_health())
