import fitz  # PyMuPDF
import re
from datetime import datetime

def extract_data_from_pdf(file_path):
    """
    Opens a PDF, extracts text line by line, and precisely extracts data
    by looking for specific keywords followed by a colon.
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

        lines = full_text.split('\n')

        for line in lines:
            # --- Precise Key-Value Extraction ---
            # Try to split the line at the colon to separate key from value
            if ':' in line:
                parts = line.split(':', 1)
                key = parts[0].strip().upper()
                value = parts[1].strip()

                if key == 'BOLETA':
                    data['boleta'] = value

                elif key == 'FECHA':
                    try:
                        # Normalize date string (e.g., from DD/MM/YYYY to DD-MM-YYYY)
                        date_str = value.replace('/', '-')
                        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
                        data['fecha'] = date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        data['fecha'] = 'Fecha inválida'

                elif key == 'MONTO TOTAL $':
                    # Clean and format the total amount
                    cleaned_amount = value.replace('.', '').replace(',', '')
                    if cleaned_amount.isdigit():
                        data['total'] = f"${int(cleaned_amount):,}".replace(",", ".")
                    else:
                        data['total'] = value # Fallback

        # Fallback for "Monto Total" if it's on a line without a colon
        if data['total'] == 'No encontrado':
             for line in lines:
                if 'Monto Total' in line and '$' in line:
                    # Extract the number part of the line
                    match = re.search(r'([\d.,]+)', line)
                    if match:
                        value = match.group(1)
                        cleaned_amount = value.replace('.', '').replace(',', '')
                        if cleaned_amount.isdigit():
                            data['total'] = f"${int(cleaned_amount):,}".replace(",", ".")
                        else:
                            data['total'] = value
                        break # Stop after finding it

        return data

    except Exception as e:
        print(f"Could not parse PDF {file_path}: {e}")
        data['error'] = str(e)
        return data
