import subprocess
import time
import os

# Create a directory for verification files
verification_dir = "/home/jules/verification"
os.makedirs(verification_dir, exist_ok=True)

screenshot_path = os.path.join(verification_dir, "verification.png")

try:
    # Start the Tkinter application in the background
    app_process = subprocess.Popen(
        ["python", "src/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Give the app a moment to launch and render
    time.sleep(5)

    # Take a screenshot of the entire screen
    # Using scrot, a command-line screenshot utility
    subprocess.run(["scrot", screenshot_path], check=True)

    print(f"Screenshot saved to {screenshot_path}")

    # Check if the process is still running before trying to terminate
    if app_process.poll() is None:
        app_process.terminate()
        # Wait a bit for the process to terminate gracefully
        try:
            app_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            app_process.kill() # Force kill if it doesn't terminate

    # Print any output from the app for debugging
    stdout, stderr = app_process.communicate()
    print("--- App stdout ---")
    print(stdout)
    print("--- App stderr ---")
    print(stderr)


except FileNotFoundError:
    print("Error: 'scrot' is not installed. Please install it to take screenshots.")
except subprocess.CalledProcessError as e:
    print(f"Error taking screenshot: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
