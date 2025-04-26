import subprocess
import sys
import datetime
from datetime import timezone

SCRIPTS = [
    'multi_world_fetch.py',
    'export.py'
]


def run_script(script_name):
    print(f"\nRunning {script_name}...")
    try:
        result = subprocess.run([sys.executable, script_name], check=True)
        print(f"{script_name} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {script_name} exited with code {e.returncode}")
        sys.exit(e.returncode)

def update_timestamp():
    with open ("LastUpdate.txt", "w") as text_file:
        text_file.write(str(now))
    

def main():
    for script in SCRIPTS:
        run_script(script)
    print("\nAll tasks completed successfully.")
    update_timestamp()


if __name__ == '__main__':
    main()
