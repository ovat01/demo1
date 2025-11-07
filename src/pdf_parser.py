import fitz  # PyMuPDF
import re

def _find_best_total(text_block):
    """
    Finds all numbers that look like currency in a block of text and returns the largest one.
    This is a heuristic to identify the "Total" amount.
    """
    # Regex to find numbers like: 1.234,56 | 1,234.56 | 1234.56 | 1.234
    money_pattern = re.compile(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?|\d+(?:[.,]\d{2})?)')

    numbers_found = money_pattern.findall(text_block)

    if not numbers_found:
        return None

    max_value = -1.0

    for num_str in numbers_found:
        # Normalize the number string for conversion to float
        # Replace comma decimal separator with a dot, and remove thousand separators
        normalized_str = num_str.replace('.', '').replace(',', '.')

        # Handle cases where the last dot was a thousand separator (e.g., "1.234")
        if '.' in num_str and '.' not in normalized_str:
            parts = num_str.split('.')
            if len(parts[-1]) == 3: # Likely a thousand separator
                 normalized_str = "".join(parts)

        try:
            value = float(normalized_str)
            if value > max_value:
                max_value = value
        except ValueError:
            continue

    if max_value == -1.0:
        return None

    # Return the largest number found, formatted as a currency string for display
    return f"${max_value:,.2f}"

def extract_total_from_pdf(file_path):
    """
    Opens a PDF, extracts its text, and searches for a total amount.
    """
    try:
        doc = fitz.open(file_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text("text")
        doc.close()

        # List of keywords to search for, in order of preference
        keywords = ['total a pagar', 'total', 'monto total', 'valor total']

        lines = full_text.lower().split('\n')

        for keyword in keywords:
            for i, line in enumerate(lines):
                if keyword in line:
                    # Search for the total in the current line and the next two lines
                    search_area = " ".join(lines[i:i+3])
                    total = _find_best_total(search_area)
                    if total:
                        return total

        return "No encontrado"

    except Exception as e:
        print(f"Could not parse PDF {file_path}: {e}")
        return "Error"
