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
# Assumi che banned_words_file sia il percorso del tuo file di parole vietate
banned_words_file = config['DEFAULT']['BannedWords']

pdf_dir = config['DEFAULT']['PDFDirectory']
png_dir = config['DEFAULT']['OutputDirectory']
os.makedirs(png_dir, exist_ok=True)  # Assicurati che la directory di output esista

import re

def filter_text(input_text, banned_words_file):
    """
    Sostituisce con uno spazio tutte le parole presenti nel file esterno,
    elimina tutte le doppie spaziature e alla fine rimuove tutte le linee
    con lunghezza inferiore ai 4 caratteri.

    :param input_text: Il testo da filtrare.
    :param banned_words_file: Il percorso del file che contiene le parole vietate.
    :return: Il testo filtrato.
    """
    # Leggi le parole vietate dal file
    with open(banned_words_file, 'r') as file:
        banned_words = [line.strip() for line in file.readlines()]

    # Sostituisce ciascuna parola vietata con uno spazio
    for word in banned_words:
        input_text = re.sub(r'\b{}\b'.format(re.escape(word)), ' ', input_text)

    # Elimina tutte le doppie spaziature
    input_text = re.sub(r'  ', ' ', input_text)
    
    #input_text = re.sub(r'\s+', ' ', input_text)


    # Rimuove le righe con meno di 4 caratteri
    filtered_lines = []
    for line in input_text.split('\n'):
        if len(line.strip()) >= 4:
            filtered_lines.append(line)

    result_text = re.sub(r'\n\n', '\n', '\n'.join(filtered_lines))

    return result_text

# ... Il resto del codice rimane invariato ...

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
                # Filtra il testo
                filtered_text = filter_text(text,banned_words_file)


                full_txt_path = os.path.join(output_dir, f"{filename}.txt")
                save_text_to_file(filtered_text, full_txt_path)

                new_pdf = create_text_pdf_page(pdf, filtered_text, page.number)
                new_pdf_path = os.path.join(output_dir, f"{filename}.pdf")
                new_pdf.save(new_pdf_path)
                new_pdf.close()

            pdf.close()
            #rename the pdf file to .old
            os.rename(full_pdf_path, full_pdf_path + '.old')
            
process_pdfs(pdf_dir, png_dir)
print("Done")
