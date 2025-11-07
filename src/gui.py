import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from datetime import datetime
from PIL import Image, ImageTk
from tkcalendar import Calendar
import threading

from printing import get_printers, print_pdf, resource_path
from file_monitor import FileMonitor
from config import save_config, load_config
from pdf_parser import extract_total_from_pdf

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Reimpresión de Boletas")
        self.pack(fill="both", expand=True)
        self.file_monitor = None
        self.found_files = {}  # filename -> full_path
        self.create_widgets()
        self.load_printers()
        self.load_initial_config()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # Logo and main frames setup...
        try:
            logo_path = resource_path(os.path.join("assets", "logo.png"))
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((250, 60), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ttk.Label(self, image=self.logo_photo)
            logo_label.pack(pady=10)
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")

        control_frame = ttk.Frame(self)
        control_frame.pack(padx=10, pady=5, fill="x")
        self.folder_label = ttk.Label(control_frame, text="Carpeta de Boletas:")
        self.folder_label.pack(side="left")
        self.folder_path = tk.StringVar()
        self.folder_entry = ttk.Entry(control_frame, textvariable=self.folder_path, width=50)
        self.folder_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.browse_button = ttk.Button(control_frame, text="Seleccionar Carpeta", command=self.browse_folder)
        self.browse_button.pack(side="left")

        date_frame = ttk.Frame(self)
        date_frame.pack(padx=10, pady=5, fill="x")
        self.start_date_label = ttk.Label(date_frame, text="Fecha Desde:")
        self.start_date_label.pack(side="left")
        self.start_date = tk.StringVar(value=datetime.now().strftime('%Y%m%d'))
        self.start_date_entry = ttk.Entry(date_frame, textvariable=self.start_date, width=12)
        self.start_date_entry.pack(side="left", padx=5)
        self.start_cal_button = ttk.Button(date_frame, text="📅", width=3, command=lambda: self.pick_date(self.start_date))
        self.start_cal_button.pack(side="left")
        self.end_date_label = ttk.Label(date_frame, text="Fecha Hasta:")
        self.end_date_label.pack(side="left", padx=10)
        self.end_date = tk.StringVar(value=datetime.now().strftime('%Y%m%d'))
        self.end_date_entry = ttk.Entry(date_frame, textvariable=self.end_date, width=12)
        self.end_date_entry.pack(side="left", padx=5)
        self.end_cal_button = ttk.Button(date_frame, text="📅", width=3, command=lambda: self.pick_date(self.end_date))
        self.end_cal_button.pack(side="left")
        self.filter_button = ttk.Button(date_frame, text="Buscar", command=self.update_pdf_list)
        self.filter_button.pack(side="left", padx=10)

        pdf_list_frame = ttk.Frame(self)
        pdf_list_frame.pack(padx=10, pady=10, fill="both", expand=True)
        columns = ("filename", "total")
        self.pdf_tree = ttk.Treeview(pdf_list_frame, columns=columns, show="headings")
        self.pdf_tree.heading("filename", text="Nombre del Archivo")
        self.pdf_tree.heading("total", text="Monto Total")
        self.pdf_tree.column("filename", width=400)
        self.pdf_tree.column("total", width=100, anchor="e")
        self.pdf_tree.pack(fill="both", expand=True)

        self.printer_frame = ttk.Frame(self)
        self.printer_frame.pack(padx=10, pady=10, fill="x")
        self.printer_label = ttk.Label(self.printer_frame, text="Seleccionar Impresora:")
        self.printer_label.pack(side="left")
        self.printer_combo = ttk.Combobox(self.printer_frame, width=50, state="readonly")
        self.printer_combo.pack(side="left", padx=5, expand=True, fill="x")
        self.printer_combo.bind("<<ComboboxSelected>>", self.on_printer_select)
        self.reprint_button = ttk.Button(self, text="Reimprimir", command=self.reprint_selected_pdf)
        self.reprint_button.pack(pady=10)

    def pick_date(self, date_var):
        top = tk.Toplevel(self.master)
        try:
            current_date = datetime.strptime(date_var.get(), '%Y%m%d')
        except ValueError:
            current_date = datetime.now()
        cal = Calendar(top, selectmode='day', year=current_date.year, month=current_date.month, day=current_date.day)
        cal.pack(pady=20)
        def set_date_and_close():
            date_var.set(cal.selection_get().strftime('%Y%m%d'))
            top.destroy()
        ok_button = ttk.Button(top, text="Aceptar", command=set_date_and_close)
        ok_button.pack(pady=10)

    def load_printers(self):
        try:
            printers = get_printers()
            self.printer_combo['values'] = printers
        except Exception as e:
            messagebox.showerror("Error de Impresoras", f"No se pudieron cargar las impresoras: {e}")

    def load_initial_config(self):
        folder, printer = load_config()
        if folder and os.path.isdir(folder):
            self.folder_path.set(folder)
            self.update_pdf_list()
            self.start_monitoring(folder)
        if printer and printer in self.printer_combo['values']:
            self.printer_combo.set(printer)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.update_pdf_list()
            self.start_monitoring(folder_selected)
            self.save_current_config()

    def start_monitoring(self, folder_path):
        if self.file_monitor:
            self.file_monitor.stop()
        self.file_monitor = FileMonitor(folder_path, self.update_pdf_list)
        self.file_monitor.start()

    def update_pdf_list(self):
        # Clear previous results and disable search button
        for i in self.pdf_tree.get_children():
            self.pdf_tree.delete(i)
        self.found_files.clear()
        self.filter_button.config(state="disabled")

        # Start the search and parsing in a background thread
        threading.Thread(target=self._background_pdf_search, daemon=True).start()

    def _background_pdf_search(self):
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            self.master.after(0, lambda: self.filter_button.config(state="normal"))
            return

        try:
            start_date_str = self.start_date.get()
            end_date_str = self.end_date.get()
            start_date = datetime.strptime(start_date_str, '%Y%m%d').date()
            end_date = datetime.strptime(end_date_str, '%Y%m%d').date()
        except ValueError:
            self.master.after(0, lambda: messagebox.showerror("Fecha Inválida", "El formato de fecha debe ser YYYYMMDD."))
            self.master.after(0, lambda: self.filter_button.config(state="normal"))
            return

        # Find files first
        pdf_files_to_process = []
        for root, _, files in os.walk(folder):
            for file in files:
                if file.lower().endswith('.pdf'):
                    try:
                        file_date_str = file[:8]
                        file_date = datetime.strptime(file_date_str, '%Y%m%d').date()
                        if start_date <= file_date <= end_date:
                            full_path = os.path.join(root, file)
                            pdf_files_to_process.append((file, full_path))
                    except (ValueError, IndexError):
                        continue

        # Populate the table with "Loading..." message
        for file, full_path in pdf_files_to_process:
            item_id = self.pdf_tree.insert("", "end", values=(file, "Cargando..."))
            self.found_files[item_id] = (file, full_path)

        # Now, parse each PDF and update the table
        for item_id in self.pdf_tree.get_children():
            file, full_path = self.found_files[item_id]
            total = extract_total_from_pdf(full_path)
            # Schedule the update in the main thread
            self.master.after(0, self.pdf_tree.set, item_id, "total", total)

        # Re-enable the search button
        self.master.after(0, lambda: self.filter_button.config(state="normal"))

    def reprint_selected_pdf(self):
        selected_item = self.pdf_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selección Requerida", "Por favor, seleccione una boleta para reimprimir.")
            return

        _, full_path = self.found_files[selected_item]
        printer_name = self.printer_combo.get()

        if not printer_name:
            messagebox.showwarning("Selección Requerida", "Por favor, seleccione una impresora.")
            return

        try:
            print_pdf(full_path, printer_name)
            messagebox.showinfo("Impresión Exitosa", f"Se ha enviado a imprimir '{os.path.basename(full_path)}' a '{printer_name}'.")
        except Exception as e:
            messagebox.showerror("Error de Impresión", f"Ocurrió un error al intentar imprimir: {e}")

    def on_printer_select(self, event):
        self.save_current_config()

    def save_current_config(self):
        folder = self.folder_path.get()
        printer = self.printer_combo.get()
        save_config(folder, printer)

    def on_closing(self):
        self.save_current_config()
        if self.file_monitor:
            self.file_monitor.stop()
        self.master.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
