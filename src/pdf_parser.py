import fitz  # PyMuPDF
import re
from datetime import datetime

def extract_data_from_pdf(file_path):
    """
    Opens a PDF, extracts its text, and searches for boleta number, date, and total amount
    with more flexible regular expressions.
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
            # Using page.get_text("text", flags=fitz.TEXT_INHIBIT_SPACES) might help with layout
            full_text += page.get_text("text")
        doc.close()

        # Regex for Boleta: Looks for "BOLETA", allows optional colon, and captures the number.
        # The [\s:]* part allows for any combination of whitespace and colons.
        boleta_match = re.search(r'BOLETA[\s:]*(\d+)', full_text, re.IGNORECASE)
        if boleta_match:
            data['boleta'] = boleta_match.group(1).strip()

        # Regex for Fecha: More flexible, allows for different separators.
        fecha_match = re.search(r'FECHA[\s:]*(\d{2}[-/]\d{2}[-/]\d{4})', full_text, re.IGNORECASE)
        if fecha_match:
            try:
                # Normalize date string by replacing separators
                date_str = fecha_match.group(1).strip().replace('/', '-')
                date_obj = datetime.strptime(date_str, '%d-%m-%Y')
                data['fecha'] = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                data['fecha'] = 'Fecha inválida'

        # Regex for Total: Allows for more variations in spacing and symbols.
        total_match = re.search(r'Monto Total\s*\$?\s*:?\s*([\d.,]+)', full_text, re.IGNORECASE)
        if total_match:
            amount_str = total_match.group(1).strip()
            # Clean the amount string by removing thousand separators (dots or commas)
            # and handling potential decimal commas.
            cleaned_amount = amount_str.replace('.', '').replace(',', '')
            if cleaned_amount.isdigit():
                data['total'] = f"${int(cleaned_amount):,}".replace(",",".") # Format with dots
            else:
                data['total'] = amount_str # Fallback to original string if not a simple integer

        return data

    except Exception as e:
        print(f"Could not parse PDF {file_path}: {e}")
        data['error'] = str(e)
        return data
