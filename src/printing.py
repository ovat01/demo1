import win32print
import os
import sys
import subprocess

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
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
    Prints a PDF file directly using SumatraPDF, wrapping arguments in quotes
    to handle complex names and paths reliably.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo no se encuentra: {file_path}")

    try:
        sumatra_path = resource_path(os.path.join("vendor", "SumatraPDF.exe"))
        if not os.path.exists(sumatra_path):
            raise FileNotFoundError(f"SumatraPDF.exe not found at {sumatra_path}")

        # Construct the command as a single string with explicit quotes
        # This is the most reliable way to handle names with spaces and special characters.
        command = (
            f'"{sumatra_path}" '
            f'-print-to "{printer_name}" '
            f'-silent -exit-when-done '
            f'"{os.path.abspath(file_path)}"'
        )

        # Execute the command using shell=True, which correctly interprets the quoted string
        subprocess.run(command, check=True, timeout=120,
                       creationflags=subprocess.CREATE_NO_WINDOW, shell=True)

    except FileNotFoundError as e:
        raise e
    except subprocess.TimeoutExpired:
        raise Exception("El proceso de impresión tardó demasiado en responder.")
    except subprocess.CalledProcessError as e:
        raise Exception(f"SumatraPDF.exe encontró un error al imprimir. Verifique la impresora y el archivo.\nError: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado durante la impresión: {e}")
        raise
