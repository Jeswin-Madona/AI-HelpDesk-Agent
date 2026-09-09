import socket
import urllib.request
from typing import Dict, Any

def check_internet_connection() -> Dict[str, Any]:
    """
    Performs a real network connectivity check by attempting a low-level
    socket connection to Google Public DNS (8.8.8.8:53) and an HTTP reachability test.

    Returns structured diagnostic results.
    """
    result = {
        "tool_name": "Internet Diagnostic Tool",
        "reachable": False,
        "dns_functional": False,
        "status": "FAILED",
        "details": ""
    }

    # Step 1: Socket Ping to 8.8.8.8 (Tests raw IP routing)
    try:
        socket.setdefaulttimeout(2.5)
        host = socket.gethostbyname("8.8.8.8")
        s = socket.create_connection((host, 53), 2.5)
        s.close()
        raw_ip_ok = True
    except Exception:
        raw_ip_ok = False

    # Step 2: HTTP GET to google.com (Tests domain resolution + HTTP routing)
    try:
        req = urllib.request.Request("http://www.google.com", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3.0) as response:
            if response.status == 200:
                result["dns_functional"] = True
    except Exception:
        result["dns_functional"] = False

    if raw_ip_ok and result["dns_functional"]:
        result["reachable"] = True
        result["status"] = "GOOD"
        result["details"] = "Internet is fully operational (IP routing & DNS resolution working)."
    elif raw_ip_ok and not result["dns_functional"]:
        result["reachable"] = False
        result["status"] = "DNS FAILURE"
        result["details"] = "Connected to local gateway/IP routing works, but DNS resolution failed."
    else:
        result["reachable"] = False
        result["status"] = "FAILED"
        result["details"] = "No internet connection detected (unreachable public IP & gateway)."

    return result

if __name__ == "__main__":
    print(check_internet_connection())
