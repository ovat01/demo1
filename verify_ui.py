import subprocess
import time
import pyscreenshot as ImageGrab
import os

def verify_ui():
    """
    Starts the application, waits for it to load, and takes a screenshot.
    """
    process = None
    try:
        # Start the application
        print("Starting the application...")
        process = subprocess.Popen(["python", "src/main.py"])

        # Wait for the application window to open
        print("Waiting for application to load...")
        time.sleep(5)  # Adjust sleep time if necessary

        # Create a directory for the screenshot
        screenshot_dir = "/home/jules/verification"
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, "verification.png")

        # Take a screenshot of the entire screen
        print(f"Taking screenshot and saving to {screenshot_path}...")
        im = ImageGrab.grab()
        im.save(screenshot_path)
        print("Screenshot saved successfully.")

    finally:
        # Terminate the application process
        if process:
            print("Terminating the application.")
            process.terminate()
            process.wait()

if __name__ == "__main__":
    verify_ui()
