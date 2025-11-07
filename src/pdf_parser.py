import fitz  # PyMuPDF
import re
from datetime import datetime

def extract_data_from_pdf(file_path):
    """
    Opens a PDF, extracts its text, and searches for boleta number, date, and total amount.
    """
    data = {
        'boleta': 'No encontrado',
        'fecha': 'No encontrado',
        'total': 'No encontrado'
    }
    try:
        doc = fitz.open(file_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text("text")
        doc.close()

        # Regex to find the required data based on the provided image
        # Example: BOLETA : 4525086
        boleta_match = re.search(r'BOLETA\s*:\s*(\d+)', full_text, re.IGNORECASE)
        if boleta_match:
            data['boleta'] = boleta_match.group(1).strip()

        # Example: FECHA : 05-11-2025
        fecha_match = re.search(r'FECHA\s*:\s*(\d{2}-\d{2}-\d{4})', full_text, re.IGNORECASE)
        if fecha_match:
            try:
                # Parse the date from DD-MM-YYYY format
                date_obj = datetime.strptime(fecha_match.group(1).strip(), '%d-%m-%Y')
                # Store it in a standard, sortable format (YYYY-MM-DD)
                data['fecha'] = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                data['fecha'] = 'Fecha inválida'

        # Example: Monto Total $ : 60.450
        total_match = re.search(r'Monto Total\s*\$?\s*:\s*([\d.,]+)', full_text, re.IGNORECASE)
        if total_match:
            amount_str = total_match.group(1).strip()
            # Clean the amount string by removing thousand separators (dots)
            # This is based on the format "60.450" representing 60450
            cleaned_amount = amount_str.replace('.', '').replace(',', '')
            data['total'] = cleaned_amount

        return data

    except Exception as e:
        print(f"Could not parse PDF {file_path}: {e}")
        data['error'] = str(e) # Add an error key if something goes wrong
        return data
