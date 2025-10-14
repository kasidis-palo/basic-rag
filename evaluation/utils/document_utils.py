from PyPDF2 import PdfReader


def load_pdf_as_text_pages(pdf_path: str):
    reader = PdfReader(pdf_path)
    pages = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text.strip():
            pages.append(text)
    return pages