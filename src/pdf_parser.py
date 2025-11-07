import fitz  # PyMuPDF
import re
from datetime import datetime

def extract_data_from_pdf(file_path):
    """
    Opens a PDF, extracts its text line by line, and searches for boleta number,
    date, and total amount with high precision.
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

        # Process the text line by line for better accuracy
        lines = full_text.split('\n')

        for line in lines:
            line_upper = line.upper()

            # --- Find Boleta Number ---
            if 'BOLETA' in line_upper:
                # Find all numbers in the line and take the last one.
                # This is robust against other numbers appearing before the actual boleta number.
                numbers = re.findall(r'\d+', line)
                if numbers:
                    data['boleta'] = numbers[-1]

            # --- Find Date ---
            if 'FECHA' in line_upper:
                 # Search for a date pattern DD-MM-YYYY or DD/MM/YYYY
                match = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})', line)
                if match:
                    try:
                        date_str = match.group(1).replace('/', '-')
                        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
                        data['fecha'] = date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        data['fecha'] = 'Fecha inválida'

            # --- Find Total Amount ---
            if 'MONTO TOTAL' in line_upper:
                # Find the number following the keyword in the same line.
                match = re.search(r'[\d.,]+', line)
                if match:
                    amount_str = match.group(0).strip()
                    cleaned_amount = amount_str.replace('.', '').replace(',', '')
                    if cleaned_amount.isdigit():
                         # Format as a currency string with dots for thousands
                        data['total'] = f"${int(cleaned_amount):,}".replace(",", ".")
                    else:
                        data['total'] = amount_str # Fallback

        return data

    except Exception as e:
        print(f"Could not parse PDF {file_path}: {e}")
        data['error'] = str(e)
        return data
