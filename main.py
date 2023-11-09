import configparser
import os
import fitz
from PIL import Image
import pytesseract

# Leggi il file di configurazione
config = configparser.ConfigParser()
config.read('config.ini')

# Configurazione di Tesseract
pytesseract.pytesseract.tesseract_cmd = config['DEFAULT']['TesseractCmd']

# Percorsi
pdf_dir = config['DEFAULT']['PDFDirectory']
png_dir = config['DEFAULT']['OutputDirectory']
os.makedirs(png_dir, exist_ok=True)  # Assicurati che la directory di output esista

def convert_pdf_page_to_image(pdf_page):
    pix = pdf_page.get_pixmap(dpi=300)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

def ocr_image_to_text(image):
    return pytesseract.image_to_string(image)

def save_text_to_file(text, filepath):
    with open(filepath, 'w') as file:
        file.write(text)

def create_text_pdf_page(pdf, text, page_number):
    new_pdf = fitz.open()
    new_pdf.insert_pdf(pdf, from_page=page_number, to_page=page_number)
    new_pdf.new_page(width=595, height=842)  # Dimensioni di una pagina A4
    page = new_pdf[1]
    page.insert_text((72, 72), text, fontsize=8)
    return new_pdf

def process_pdfs(directory, output_dir):
    for pdf_file in os.listdir(directory):
        if pdf_file.endswith('.pdf'):
            full_pdf_path = os.path.join(directory, pdf_file)
            pdf = fitz.open(full_pdf_path)
            file_date = pdf.metadata['creationDate'][2:14]

            for page in pdf:
                filename = f"{file_date}_{page.number}"
                image = convert_pdf_page_to_image(page)
                text = ocr_image_to_text(image)

                full_txt_path = os.path.join(output_dir, f"{filename}.txt")
                save_text_to_file(text, full_txt_path)

                new_pdf = create_text_pdf_page(pdf, text, page.number)
                new_pdf_path = os.path.join(output_dir, f"{filename}.pdf")
                new_pdf.save(new_pdf_path)
                new_pdf.close()

            pdf.close()

process_pdfs(pdf_dir, png_dir)
print("Done")
