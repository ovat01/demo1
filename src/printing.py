import win32print
import os
import sys
import subprocess

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_printers():
    """Returns a list of available printers."""
    try:
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        return [printer[2] for printer in printers]
    except Exception as e:
        print(f"Error getting printers: {e}")
        return []

def print_pdf(file_path, printer_name):
    """
    Prints a PDF file directly using SumatraPDF command-line tool.
    This method is highly reliable and independent of Windows shell associations.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo no se encuentra: {file_path}")

    try:
        # Locate the SumatraPDF executable within the project
        sumatra_path = resource_path(os.path.join("vendor", "SumatraPDF.exe"))

        if not os.path.exists(sumatra_path):
            raise FileNotFoundError(f"SumatraPDF.exe not found at {sumatra_path}")

        # Command to print silently to a specific printer
        command = [
            sumatra_path,
            '-print-to', printer_name,
            '-silent',
            '-exit-when-done',
            os.path.abspath(file_path)
        ]

        # Execute the command without showing a console window
        # We use a timeout to prevent the process from hanging indefinitely
        subprocess.run(command, check=True, timeout=120,
                       creationflags=subprocess.CREATE_NO_WINDOW)

    except FileNotFoundError as e:
        raise e # Re-raise to be specific in the error message
    except subprocess.TimeoutExpired:
        raise Exception("El proceso de impresión tardó demasiado en responder.")
    except subprocess.CalledProcessError as e:
        # This error is raised if SumatraPDF returns a non-zero exit code (an error)
        raise Exception(f"SumatraPDF.exe encontró un error al imprimir: {e}")
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred during printing: {e}")
        raise
