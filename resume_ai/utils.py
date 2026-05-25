import fitz


def extract_pdf_text(pdf_file):
    doc = fitz.open(
        stream=pdf_file.read(),
        filetype="pdf"
    )

    text = []

    for page in doc:
        page_text = page.get_text("text")

        if page_text and page_text.strip():
            text.append(page_text)

    final_text = "\n".join(text)

    return final_text