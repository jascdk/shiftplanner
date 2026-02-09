from pypdf import PdfReader

def extract_text_from_pdf(file_input):
    """
    Extracts raw text from a PDF file object or file path.
    """
    try:
        # Handle both file paths (str) and file-like objects (Streamlit uploads)
        reader = PdfReader(file_input)
            
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"