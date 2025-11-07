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
        # Not running in a bundle, so the base path is the project root
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
    Prints a PDF file directly using SumatraPDF, ensuring the path to the
    executable is correctly resolved for both development and the packaged .exe.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo no se encuentra: {file_path}")

    try:
        # Correctly find SumatraPDF.exe inside the 'tools' folder,
        # which is where PyInstaller is told to put it.
        sumatra_path = resource_path(os.path.join("tools", "SumatraPDF.exe"))

        if not os.path.exists(sumatra_path):
            # This error will now show the correct path it's looking for.
            raise FileNotFoundError(f"SumatraPDF.exe not found at {sumatra_path}")

        # Using a list of arguments is safer than a single command string
        # as it avoids issues with shell interpretation.
        command = [
            sumatra_path,
            '-print-to', printer_name,
            '-silent',
            '-exit-when-done',
            os.path.abspath(file_path)
        ]

        # creationflags avoids showing a console window for the subprocess.
        subprocess.run(command, check=True, timeout=120,
                       creationflags=subprocess.CREATE_NO_WINDOW)

    except FileNotFoundError as e:
        raise e
    except subprocess.TimeoutExpired:
        raise Exception("El proceso de impresión tardó demasiado en responder.")
    except subprocess.CalledProcessError as e:
        raise Exception(f"SumatraPDF.exe encontró un error. Verifique la impresora y el archivo.\nError: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado durante la impresión: {e}")
        raise
