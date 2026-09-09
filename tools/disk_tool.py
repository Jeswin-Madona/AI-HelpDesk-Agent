import shutil
import os
from typing import Dict, Any

def check_disk_space(path: str = None) -> Dict[str, Any]:
    """
    Inspects real local drive storage space and usage percentages.

    Returns structured disk diagnostic metrics.
    """
    if path is None:
        path = "C:\\" if os.name == "nt" else "/"

    try:
        total, used, free = shutil.disk_usage(path)
        
        gb = 1024 ** 3
        total_gb = round(total / gb, 1)
        used_gb = round(used / gb, 1)
        free_gb = round(free / gb, 1)
        percent_used = round((used / total) * 100, 1)

        status = "OK"
        if percent_used >= 90:
            status = "CRITICAL (LOW STORAGE)"
        elif percent_used >= 80:
            status = "WARNING (STORAGE ALMOST FULL)"

        return {
            "tool_name": "Disk Diagnostic Tool",
            "drive": path,
            "total_gb": total_gb,
            "used_gb": used_gb,
            "free_gb": free_gb,
            "percent_used": percent_used,
            "status": status,
            "details": f"Total: {total_gb} GB | Used: {used_gb} GB ({percent_used}%) | Free: {free_gb} GB"
        }
    except Exception as e:
        return {
            "tool_name": "Disk Diagnostic Tool",
            "drive": path,
            "status": "ERROR",
            "details": f"Failed to check disk space: {str(e)}"
        }

if __name__ == "__main__":
    print(check_disk_space())
