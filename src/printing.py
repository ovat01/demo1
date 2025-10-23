import win32print
import win32api
import os
import time

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
    Prints a PDF by temporarily setting the default printer, printing,
    and then restoring the original default printer.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo no se encuentra: {file_path}")

    original_printer = None
    try:
        # 1. Get and save the original default printer
        original_printer = win32print.GetDefaultPrinter()

        # 2. Set the selected printer as the new default
        win32print.SetDefaultPrinter(printer_name)

        # 3. Send the generic print command. Windows will use the new default printer.
        win32api.ShellExecute(
            0,
            "print",
            f'"{os.path.abspath(file_path)}"',
            None,
            ".",
            0
        )

        # Give the print spooler a moment to process the job before restoring
        time.sleep(3)

    except Exception as e:
        print(f"An error occurred during printing: {e}")
        # Re-raise the exception to be caught by the GUI
        raise

    finally:
        # 4. ALWAYS restore the original default printer
        if original_printer:
            win32print.SetDefaultPrinter(original_printer)
