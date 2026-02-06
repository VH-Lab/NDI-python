import sys
import platform
import os
import subprocess
import tempfile

def console(filename):
    """
    Pops up an external terminal window that displays a log file.

    CONSOLE(FILENAME)

    Pops up a console window that displays a log file.
    Right now, only MacOS is supported.
    """

    system = platform.system()

    if system == 'Darwin': # MacOS
        # Create temporary applescript file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.scpt', delete=False) as f:
            script_content = f"""tell application "Terminal"
    activate
    do script "tail -f {filename}"
end tell"""
            f.write(script_content)
            temp_filename = f.name

        try:
            subprocess.run(['osascript', temp_filename], check=True)
        finally:
            os.remove(temp_filename)

    elif system == 'Linux':
        # Try some common terminal emulators
        terminals = ['gnome-terminal', 'xterm', 'konsole']
        launched = False
        for term in terminals:
            try:
                # This is a very basic attempt and might need adjustment for specific terminals
                if term == 'gnome-terminal':
                    subprocess.run([term, '--', 'tail', '-f', filename])
                elif term == 'xterm':
                    subprocess.run([term, '-e', f'tail -f {filename}'])
                elif term == 'konsole':
                    subprocess.run([term, '-e', 'tail', '-f', filename])
                launched = True
                break
            except FileNotFoundError:
                continue

        if not launched:
             raise NotImplementedError("Linux terminal launch not fully supported yet.")

    elif system == 'Windows':
         raise NotImplementedError("Windows not supported yet.")
    else:
         raise NotImplementedError(f"{system} not supported yet.")
