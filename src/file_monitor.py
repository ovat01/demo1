import os
import time
import threading

class FileMonitor:
    def __init__(self, folder_path, callback):
        self._folder_path = folder_path
        self._callback = callback
        self._running = False
        self._thread = None
        self._seen_files = set()

    def start(self):
        """Starts the file monitoring in a separate thread."""
        if not self._running:
            self._running = True
            self._seen_files = self._get_current_pdfs()
            self._thread = threading.Thread(target=self._monitor, daemon=True)
            self._thread.start()

    def stop(self):
        """Stops the file monitoring."""
        self._running = False
        if self._thread:
            self._thread.join()

    def _get_current_pdfs(self):
        """Gets the set of PDF files currently in the folder and all subfolders."""
        pdf_files = set()
        try:
            for root, _, files in os.walk(self._folder_path):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.add(os.path.join(root, file))
        except FileNotFoundError:
            return set()
        return pdf_files

    def _monitor(self):
        """The core monitoring loop that runs in the background."""
        while self._running:
            time.sleep(5)  # Check for new files every 5 seconds
            current_files = self._get_current_pdfs()

            # Check if there's any change (new files or removed files)
            if current_files != self._seen_files:
                self._seen_files = current_files
                self._callback()  # Notify the GUI to update the list
