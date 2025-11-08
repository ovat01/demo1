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
from pdf_parser import extract_data_from_pdf
from cache_manager import load_cache, save_cache, is_file_modified

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Reimpresión de Boletas")
        self.master.minsize(700, 500)

        self.pack(fill="both", expand=True)

        self.file_monitor = None
        self.found_files = {}
        self.create_widgets()
        self.load_printers()
        self.load_initial_config()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        try:
            logo_path = resource_path(os.path.join("assets", "logo.png"))
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((250, 60), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ttk.Label(main_frame, image=self.logo_photo)
            logo_label.pack(pady=10)
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(padx=10, pady=5, fill="x")

        try:
            folder_icon_path = resource_path(os.path.join("assets", "folder.png"))
            folder_icon_image = Image.open(folder_icon_path).resize((24, 24), Image.Resampling.LANCZOS)
            self.folder_icon = ImageTk.PhotoImage(folder_icon_image)
            self.browse_button = ttk.Button(control_frame, image=self.folder_icon, command=self.browse_folder)
        except Exception as e:
            self.browse_button = ttk.Button(control_frame, text="Seleccionar Carpeta", command=self.browse_folder)
        self.browse_button.pack(side="left", padx=(0, 10))
        self.folder_path = tk.StringVar()
        self.folder_label = ttk.Label(control_frame, text="No se ha seleccionado ninguna carpeta", style="TLabel")
        self.folder_label.pack(side="left", fill="x", expand=True)

        date_frame = ttk.Frame(main_frame)
        date_frame.pack(padx=10, pady=5, fill="x")

        self.start_date_label = ttk.Label(date_frame, text="Desde:")
        self.start_date_label.pack(side="left")
        self.start_date = tk.StringVar(value=datetime.now().strftime('%d-%m-%Y'))
        self.start_date_entry = ttk.Entry(date_frame, textvariable=self.start_date, width=12)
        self.start_date_entry.pack(side="left", padx=5)
        self.start_cal_button = ttk.Button(date_frame, text="📅", width=3, command=lambda: self.pick_date(self.start_date))
        self.start_cal_button.pack(side="left")

        self.end_date_label = ttk.Label(date_frame, text="Hasta:")
        self.end_date_label.pack(side="left", padx=10)
        self.end_date = tk.StringVar(value=datetime.now().strftime('%d-%m-%Y'))
        self.end_date_entry = ttk.Entry(date_frame, textvariable=self.end_date, width=12)
        self.end_date_entry.pack(side="left", padx=5)
        self.end_cal_button = ttk.Button(date_frame, text="📅", width=3, command=lambda: self.pick_date(self.end_date))
        self.end_cal_button.pack(side="left")

        self.filter_button = ttk.Button(date_frame, text="Buscar", command=self.update_pdf_list)
        self.filter_button.pack(side="left", padx=10)

        pdf_list_frame = ttk.Frame(main_frame)
        pdf_list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        columns = ("fecha", "boleta", "total")
        self.pdf_tree = ttk.Treeview(pdf_list_frame, columns=columns, show="headings")
        self.pdf_tree.heading("fecha", text="Fecha")
        self.pdf_tree.heading("boleta", text="Boleta")
        self.pdf_tree.heading("total", text="Monto Total")
        self.pdf_tree.column("fecha", width=120, anchor="center")
        self.pdf_tree.column("boleta", width=200, anchor="center")
        self.pdf_tree.column("total", width=150, anchor="e")
        self.pdf_tree.pack(fill="both", expand=True)

        # --- Progress Bar ---
        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.pack_forget() # Hidden by default

        printer_frame = ttk.Frame(main_frame)
        printer_frame.pack(padx=10, pady=10, fill="x")
        self.printer_label = ttk.Label(printer_frame, text="Seleccionar Impresora:")
        self.printer_label.pack(side="left")
        self.printer_combo = ttk.Combobox(printer_frame, width=50, state="readonly")
        self.printer_combo.pack(side="left", padx=5, expand=True, fill="x")
        self.printer_combo.bind("<<ComboboxSelected>>", self.on_printer_select)

        self.reprint_button = ttk.Button(main_frame, text="Reimprimir", command=self.reprint_selected_pdf)
        self.reprint_button.pack(pady=10)

    def pick_date(self, date_var):
        top = tk.Toplevel(self.master)
        try:
            current_date = datetime.strptime(date_var.get(), '%d-%m-%Y')
        except ValueError:
            current_date = datetime.now()

        cal = Calendar(top, selectmode='day', date_pattern='dd-mm-y', year=current_date.year, month=current_date.month, day=current_date.day)
        cal.pack(pady=20)

        def set_date_and_close():
            date_var.set(cal.selection_get().strftime('%d-%m-%Y'))
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
            self.folder_label.config(text=folder)
            self.update_pdf_list()
            self.start_monitoring(folder)
        if printer and printer in self.printer_combo['values']:
            self.printer_combo.set(printer)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.folder_label.config(text=folder_selected)
            self.update_pdf_list()
            self.start_monitoring(folder_selected)
            self.save_current_config()

    def start_monitoring(self, folder_path):
        if self.file_monitor:
            self.file_monitor.stop()
        self.file_monitor = FileMonitor(folder_path, self.update_pdf_list)
        self.file_monitor.start()

    def update_pdf_list(self):
        for i in self.pdf_tree.get_children():
            self.pdf_tree.delete(i)
        self.found_files.clear()
        self.filter_button.config(state="disabled")

        self.progress_bar.pack(fill="x", padx=10, pady=5) # Show progress bar
        self.progress_bar["value"] = 0

        threading.Thread(target=self._background_pdf_search, daemon=True).start()

    def _background_pdf_search(self):
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            self.master.after(0, self.on_search_complete)
            return

        try:
            start_date_str = self.start_date.get()
            end_date_str = self.end_date.get()
            start_date = datetime.strptime(start_date_str, '%d-%m-%Y').date()
            end_date = datetime.strptime(end_date_str, '%d-%m-%Y').date()
        except ValueError:
            messagebox.showerror("Fecha Inválida", "El formato de fecha debe ser DD-MM-YYYY.")
            self.master.after(0, self.on_search_complete)
            return

        cache = load_cache(folder)
        updated_cache = False

        all_pdfs = [os.path.join(r, f) for r, _, fs in os.walk(folder) for f in fs if f.lower().endswith('.pdf')]
        total_files = len(all_pdfs)
        self.master.after(0, self.progress_bar.config, {"maximum": total_files})

        temp_file_list = []
        for i, full_path in enumerate(all_pdfs):
            cached_file = cache.get(full_path)

            if not cached_file or is_file_modified(full_path, cached_file.get("mtime", "0")):
                pdf_data = extract_data_from_pdf(full_path)
                if 'error' not in pdf_data:
                    cache[full_path] = {"mtime": str(os.path.getmtime(full_path)), "data": pdf_data}
                    updated_cache = True
            else:
                pdf_data = cached_file["data"]

            if pdf_data and pdf_data.get('fecha') not in ['No encontrado', 'Fecha inválida']:
                try:
                    file_date = datetime.strptime(pdf_data['fecha'], '%Y-%m-%d').date()
                    if start_date <= file_date <= end_date:
                        temp_file_list.append({'path': full_path, 'data': pdf_data})
                except (ValueError, TypeError):
                    continue

            # Update progress bar in the main thread
            self.master.after(0, self.progress_bar.config, {"value": i + 1})

        if updated_cache:
            save_cache(folder, cache)

        temp_file_list.sort(key=lambda item: item['data']['fecha'], reverse=True)
        self.master.after(0, self.populate_tree, temp_file_list)
        self.master.after(100, self.on_search_complete) # Delay hiding to ensure UI updates

    def populate_tree(self, file_list):
        for i in self.pdf_tree.get_children():
            self.pdf_tree.delete(i)
        self.found_files.clear()

        for item in file_list:
            pdf_data = item['data']
            display_date = datetime.strptime(pdf_data['fecha'], '%Y-%m-%d').strftime('%d-%m-%Y')
            item_id = self.pdf_tree.insert("", "end", values=(display_date, pdf_data['boleta'], pdf_data['total']))
            self.found_files[item_id] = {'path': item['path'], 'data': pdf_data}

    def on_search_complete(self):
        self.progress_bar.pack_forget() # Hide progress bar
        self.filter_button.config(state="normal")

    def reprint_selected_pdf(self):
        selected_item = self.pdf_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selección Requerida", "Por favor, seleccione una boleta para reimprimir.")
            return

        full_path = self.found_files[selected_item]['path']
        printer_name = self.printer_combo.get()

        if not printer_name:
            messagebox.showwarning("Selección Requerida", "Por favor, seleccione una impresora.")
            return

        try:
            print_pdf(full_path, printer_name)
            messagebox.showinfo("Impresión Exitosa", f"Se ha enviado a imprimir la boleta a '{printer_name}'.")
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
