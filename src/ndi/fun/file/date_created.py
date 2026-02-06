import os
import platform
import datetime
import subprocess

def date_created(file_path):
    """
    Gets the creation date of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        datetime.datetime: The creation time. Returns None if it cannot be determined.
    """
    if not os.path.exists(file_path):
        return None

    system = platform.system()

    if system == 'Windows':
        return datetime.datetime.fromtimestamp(os.path.getctime(file_path))
    elif system == 'Darwin': # macOS
        stat = os.stat(file_path)
        try:
            return datetime.datetime.fromtimestamp(stat.st_birthtime)
        except AttributeError:
            return datetime.datetime.fromtimestamp(stat.st_mtime)
    else: # Linux/Unix
        stat = os.stat(file_path)
        try:
            return datetime.datetime.fromtimestamp(stat.st_birthtime)
        except AttributeError:
            # Try stat command as fallback for Linux filesystems that support it but Python os.stat doesn't expose it well or older Python
            try:
                result = subprocess.check_output(['stat', '-c', '%w', file_path], stderr=subprocess.DEVNULL).decode().strip()
                if result == '-':
                    return datetime.datetime.fromtimestamp(stat.st_ctime)
                else:
                    # result format: 2021-01-01 10:00:00.123456789 -0500
                    # We can use split to get date and time
                    parts = result.split(' ')
                    date_str = parts[0]
                    time_str = parts[1]
                    # Python's fromisoformat might not handle high precision or timezone well
                    # For simplicity, let's just use the first 26 chars which covers microseconds
                    dt_str = f"{date_str} {time_str}"
                    # Truncate fractional seconds to 6 digits (microseconds) if needed
                    if '.' in time_str:
                        t_parts = time_str.split('.')
                        if len(t_parts[1]) > 6:
                            time_str = t_parts[0] + '.' + t_parts[1][:6]

                    return datetime.datetime.fromisoformat(f"{date_str} {time_str}")
            except Exception:
                 return datetime.datetime.fromtimestamp(stat.st_ctime)
