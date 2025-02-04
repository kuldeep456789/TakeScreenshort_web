import psutil
from datetime import datetime
from typing import List, Dict, Optional
import platform

class ProcessMonitor:
    def __init__(self):
        self.system = platform.system()

    def list_running_processes(self, detailed: bool = False) -> List[Dict]:
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time', 'status']):
                try:
                    proc_info = {
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'status': proc.info['status']
                    }
                    
                    if detailed:
                        proc_info.update({
                            'cpu_usage': f"{proc.info['cpu_percent']:.1f}%",
                            'memory_usage': f"{proc.info['memory_percent']:.1f}%",
                            'start_time': datetime.fromtimestamp(proc.info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                        })
                    
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
            return sorted(processes, key=lambda x: x['name'].lower())
        except Exception as e:
            print(f"Error listing processes: {str(e)}")
            return []

    def is_app_running(self, app_name: str) -> Dict:
        """
        Check if a specific application is running and get its details.
        
        Args:
            app_name (str): Name of the application to check
            
        Returns:
            Dict: Process details if found, empty dict if not found
        """
        app_name = app_name.lower()
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if proc.info['name'] and app_name in proc.info['name'].lower():
                    return {
                        'running': True,
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_usage': f"{proc.info['cpu_percent']:.1f}%",
                        'memory_usage': f"{proc.info['memory_percent']:.1f}%"
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return {'running': False}

    def get_system_resources(self) -> Dict:
        """
        Get current system resource usage.
        
        Returns:
            Dict: System resource information
        """
        return {
            'cpu_usage': f"{psutil.cpu_percent()}%",
            'memory_usage': f"{psutil.virtual_memory().percent}%",
            'disk_usage': f"{psutil.disk_usage('/').percent}%",
            'battery': self._get_battery_info()
        }

    def _get_battery_info(self) -> Optional[Dict]:
        """
        Get battery information if available.
        
        Returns:
            Optional[Dict]: Battery information or None if not available
        """
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': f"{battery.percent}%",
                    'power_plugged': battery.power_plugged,
                    'time_left': str(battery.secsleft) if battery.secsleft != -1 else 'Unknown'
                }
        except Exception:
            pass
        return None

def main():
    monitor = ProcessMonitor()
    
    # Example usage
    print("=== System Resources ===")
    resources = monitor.get_system_resources()
    for key, value in resources.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print("\n=== Running Processes (Detailed) ===")
    processes = monitor.list_running_processes(detailed=True)
    for proc in processes[:10]:  # Show first 10 processes
        print(f"PID: {proc['pid']}, Name: {proc['name']}")
        if 'cpu_usage' in proc:
            print(f"CPU: {proc['cpu_usage']}, Memory: {proc['memory_usage']}")
            print(f"Started: {proc['start_time']}")
        print("-" * 50)
    
    # Check specific application
    app_to_check = "chrome.exe" if platform.system() == "Windows" else "Chrome"
    app_status = monitor.is_app_running(app_to_check)
    
    if app_status['running']:
        print(f"\n{app_to_check} is running:")
        print(f"PID: {app_status['pid']}")
        print(f"CPU Usage: {app_status['cpu_usage']}")
        print(f"Memory Usage: {app_status['memory_usage']}")
    else:
        print(f"\n{app_to_check} is not running")

if __name__ == "__main__":
    main()