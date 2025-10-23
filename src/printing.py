import win32print
import win32api
import os

def get_printers():
    """Returns a list of available printers."""
    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
    return [printer[2] for printer in printers]

def print_pdf(file_path, printer_name):
    """Prints a PDF file to the specified printer using the 'printto' verb."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo no se encuentra: {file_path}")

    try:
        # Using the "printto" verb is more reliable for specifying a printer.
        win32api.ShellExecute(
            0,
            "printto",
            f'"{file_path}"',
            f'"{printer_name}"',
            None,
            0
        )
    except Exception as e:
        # Log or handle the exception appropriately
        print(f"Error al imprimir: {e}")
        raise
