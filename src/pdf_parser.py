import fitz  # PyMuPDF
import re
from datetime import datetime

def find_value_near_keyword(lines, keywords, regex, search_window=2):
    """
    Generic function to find a value using regex near a keyword in a list of lines.
    It searches in a window of lines and returns the last match found, which is
    often the correct one for receipt data.
    """
    for i, line in enumerate(lines):
        if any(keyword.upper() in line.upper() for keyword in keywords):
            # Define the search area (current line + next lines in window)
            search_area = " ".join(lines[i : i + search_window])

            # Find all matches in the search area
            matches = re.findall(regex, search_area)

            if matches:
                # The last match in the vicinity of the keyword is usually the correct value.
                return matches[-1]
    return None

def extract_data_from_pdf(file_path):
    """
    Opens a PDF and extracts key data by searching for keywords and then
    applying regular expressions in the vicinity of those keywords. This approach
    is robust to variations in PDF layout.
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

        # Split text into clean lines (no leading/trailing whitespace)
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]

        # --- Extract Boleta ---
        # Looks for a number, which can include a hyphen (e.g., 001-12345)
        boleta_num = find_value_near_keyword(lines, ['BOLETA'], r'\d+(?:-\d+)?')
        if boleta_num:
            data['boleta'] = boleta_num

        # --- Extract Fecha ---
        # Looks for a date in dd-mm-yyyy or dd/mm/yyyy format
        fecha_str = find_value_near_keyword(lines, ['FECHA'], r'\d{2}[-/]\d{2}[-/]\d{4}')
        if fecha_str:
            try:
                # Normalize date separator and parse
                date_obj = datetime.strptime(fecha_str.replace('/', '-'), '%d-%m-%Y')
                data['fecha'] = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                data['fecha'] = 'Fecha inválida'

        # --- Extract Monto Total ---
        # Looks for a monetary value (digits, dots, commas)
        total_keywords = ['MONTO TOTAL', 'TOTAL A PAGAR', 'TOTAL']
        total_str = find_value_near_keyword(lines, total_keywords, r'[\d.,]+')
        if total_str:
            # Clean the string by removing formatting for conversion
            cleaned_amount = total_str.replace('.', '').replace(',', '')
            if cleaned_amount.isdigit():
                # Re-format as currency with a dot for the thousands separator
                data['total'] = f"${int(cleaned_amount):,}".replace(",", ".")

        return data

    except Exception as e:
        print(f"Could not parse PDF {file_path}: {e}")
        data['error'] = str(e)
        return data
