import fitz  # PyMuPDF
import re
from datetime import datetime

def extract_data_from_pdf(file_path):
    """
    Opens a PDF and extracts data with a highly flexible line-by-line analysis.
    It looks for keywords and then finds the relevant data on the same line,
    making it robust against formatting variations.
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
            line_upper = line.upper()

            # --- Find Boleta ---
            if 'BOLETA' in line_upper:
                # Find the last sequence of digits on the same line
                numbers = re.findall(r'\d+', line)
                if numbers:
                    data['boleta'] = numbers[-1]

            # --- Find Fecha ---
            if 'FECHA' in line_upper:
                # Find a date pattern on the same line
                match = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})', line)
                if match:
                    try:
                        date_str = match.group(1).replace('/', '-')
                        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
                        data['fecha'] = date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        pass # Ignore invalid date formats

            # --- Find Monto Total ---
            # Check for multiple variations of the "total" keyword
            total_keywords = ['MONTO TOTAL', 'TOTAL A PAGAR', 'TOTAL']
            if any(keyword in line_upper for keyword in total_keywords):
                 # Find what looks like a currency value on the same line
                match = re.search(r'[\d.,]+', line)
                if match:
                    amount_str = match.group(0).strip()
                    # Clean the string for conversion
                    cleaned_amount = amount_str.replace('.', '').replace(',', '')
                    if cleaned_amount.isdigit():
                         # Format with dots for thousands, e.g., $60.450
                        data['total'] = f"${int(cleaned_amount):,}".replace(",", ".")
        return data

    except Exception as e:
        print(f"Could not parse PDF {file_path}: {e}")
        data['error'] = str(e)
        return data
