"""
Diagnostic Tools Package for AI Helpdesk Agent
Provides real system diagnostic utilities:
- internet_tool: Network connectivity & DNS reachability check
- disk_tool: Hard drive storage space & usage check
- system_tool: CPU & Memory utilization check
"""
from .internet_tool import check_internet_connection
from .disk_tool import check_disk_space
from .system_tool import check_system_health

__all__ = [
    'check_internet_connection',
    'check_disk_space',
    'check_system_health',
]
