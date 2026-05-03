import subprocess

try:
    subprocess.run(["git", "restore", "landing/views.py"], check=True)
    print("Restored landing/views.py")
except Exception as e:
    print(f"Failed to restore: {e}")
