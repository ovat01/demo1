import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from datetime import datetime
from PIL import Image, ImageTk
from printing import get_printers, print_pdf
from file_monitor import FileMonitor
from config import save_config, load_config

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Reimpresión de Boletas")
        self.pack(fill="both", expand=True)
        self.file_monitor = None
        self.found_files = {}  # Dictionary to store filename -> full_path
        self.create_widgets()
        self.load_printers()
        self.load_initial_config()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # Logo
        try:
            logo_path = resource_path("assets/logo.png")
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((250, 60), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ttk.Label(self, image=self.logo_photo)
            logo_label.pack(pady=10)
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")

        # Folder selection frame
        control_frame = ttk.Frame(self)
        control_frame.pack(padx=10, pady=5, fill="x")
        self.folder_label = ttk.Label(control_frame, text="Carpeta de Boletas:")
        self.folder_label.pack(side="left")
        self.folder_path = tk.StringVar()
        self.folder_entry = ttk.Entry(control_frame, textvariable=self.folder_path, width=50)
        self.folder_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.browse_button = ttk.Button(control_frame, text="Seleccionar Carpeta", command=self.browse_folder)
        self.browse_button.pack(side="left")

        # Date filter frame
        date_frame = ttk.Frame(self)
        date_frame.pack(padx=10, pady=5, fill="x")

        self.start_date_label = ttk.Label(date_frame, text="Fecha Desde:")
        self.start_date_label.pack(side="left")
        self.start_date = tk.StringVar(value=datetime.now().strftime('%Y%m%d'))
        self.start_date_entry = ttk.Entry(date_frame, textvariable=self.start_date, width=12)
        self.start_date_entry.pack(side="left", padx=5)

        self.end_date_label = ttk.Label(date_frame, text="Fecha Hasta:")
        self.end_date_label.pack(side="left", padx=10)
        self.end_date = tk.StringVar(value=datetime.now().strftime('%Y%m%d'))
        self.end_date_entry = ttk.Entry(date_frame, textvariable=self.end_date, width=12)
        self.end_date_entry.pack(side="left", padx=5)

        self.filter_button = ttk.Button(date_frame, text="Buscar", command=self.update_pdf_list)
        self.filter_button.pack(side="left", padx=10)

        # PDF list
        self.pdf_list_frame = ttk.Frame(self)
        self.pdf_list_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.pdf_list_label = ttk.Label(self.pdf_list_frame, text="Boletas Encontradas:")
        self.pdf_list_label.pack(anchor="w")
        self.pdf_listbox = tk.Listbox(self.pdf_list_frame, width=80, height=15)
        self.pdf_listbox.pack(fill="both", expand=True)

        # Printer selection
        self.printer_frame = ttk.Frame(self)
        self.printer_frame.pack(padx=10, pady=10, fill="x")
        self.printer_label = ttk.Label(self.printer_frame, text="Seleccionar Impresora:")
        self.printer_label.pack(side="left")
        self.printer_combo = ttk.Combobox(self.printer_frame, width=50, state="readonly")
        self.printer_combo.pack(side="left", padx=5, expand=True, fill="x")
        self.printer_combo.bind("<<ComboboxSelected>>", self.on_printer_select)

        # Reprint button
        self.reprint_button = ttk.Button(self, text="Reimprimir", command=self.reprint_selected_pdf)
        self.reprint_button.pack(pady=10)

    def load_printers(self):
        """Loads available printers into the combobox."""
        try:
            printers = get_printers()
            self.printer_combo['values'] = printers
        except Exception as e:
            messagebox.showerror("Error de Impresoras", f"No se pudieron cargar las impresoras: {e}")

    def load_initial_config(self):
        """Loads the last used folder and printer from the config file."""
        folder, printer = load_config()
        if folder and os.path.isdir(folder):
            self.folder_path.set(folder)
            self.update_pdf_list()
            self.start_monitoring(folder)

        if printer and printer in self.printer_combo['values']:
            self.printer_combo.set(printer)

    def browse_folder(self):
        """Opens a dialog to select a folder and triggers a PDF list update."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.update_pdf_list()
            self.start_monitoring(folder_selected)
            self.save_current_config()

    def start_monitoring(self, folder_path):
        """Starts the file monitor for the given folder."""
        if self.file_monitor:
            self.file_monitor.stop()

        self.file_monitor = FileMonitor(folder_path, self.update_pdf_list)
        self.file_monitor.start()

    def update_pdf_list(self):
        """Schedules the listbox update from the main thread."""
        self.master.after(0, self._update_listbox)

    def _update_listbox(self):
        """Finds PDFs recursively, filters them by date, and updates the listbox."""
        self.pdf_listbox.delete(0, tk.END)
        self.found_files.clear()

        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            return

        try:
            start_date_str = self.start_date.get()
            end_date_str = self.end_date.get()
            start_date = datetime.strptime(start_date_str, '%Y%m%d').date()
            end_date = datetime.strptime(end_date_str, '%Y%m%d').date()
        except ValueError:
            messagebox.showerror("Fecha Inválida", "El formato de fecha debe ser YYYYMMDD.")
            return

        for root, _, files in os.walk(folder):
            for file in files:
                if file.lower().endswith('.pdf'):
                    try:
                        # Assuming date is at the start of the filename, e.g., "20251021..."
                        file_date_str = file[:8]
                        file_date = datetime.strptime(file_date_str, '%Y%m%d').date()
                        if start_date <= file_date <= end_date:
                            full_path = os.path.join(root, file)
                            self.found_files[file] = full_path
                            self.pdf_listbox.insert(tk.END, file)
                    except (ValueError, IndexError):
                        # Filename does not match the expected date format, skip it
                        continue

    def reprint_selected_pdf(self):
        """Prints the selected PDF to the selected printer."""
        selected_indices = self.pdf_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Selección Requerida", "Por favor, seleccione una boleta para reimprimir.")
            return

        selected_file = self.pdf_listbox.get(selected_indices[0])
        printer_name = self.printer_combo.get()

        if not printer_name:
            messagebox.showwarning("Selección Requerida", "Por favor, seleccione una impresora.")
            return

        file_path = self.found_files.get(selected_file)
        if not file_path:
            messagebox.showerror("Error", "No se encontró la ruta completa del archivo.")
            return

        try:
            print_pdf(file_path, printer_name)
            messagebox.showinfo("Impresión Exitosa", f"Se ha enviado a imprimir '{selected_file}' a '{printer_name}'.")
        except FileNotFoundError:
            messagebox.showerror("Archivo no Encontrado", f"El archivo '{selected_file}' no se encontró en la ruta especificada.")
        except Exception as e:
            messagebox.showerror("Error de Impresión", f"Ocurrió un error al intentar imprimir: {e}")

    def on_printer_select(self, event):
        """Saves the config when a new printer is selected."""
        self.save_current_config()

    def save_current_config(self):
        """Saves the current folder and printer selection."""
        folder = self.folder_path.get()
        printer = self.printer_combo.get()
        save_config(folder, printer)

    def on_closing(self):
        """Handles the window closing event."""
        self.save_current_config()
        if self.file_monitor:
            self.file_monitor.stop()
        self.master.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
