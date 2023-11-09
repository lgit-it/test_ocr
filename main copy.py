import fitz 
import pytesseract
from PIL import Image
import os



pytesseract.pytesseract.tesseract_cmd =  'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

print(pytesseract)

pdf_dir = "C:\\Users\\gregori02\\OneDrive - Finanziaria internazionale\\Documenti\\Progetti\\Power\\Scanner"
png_dir = ".\\Text"

# Assicurati che la directory di output esista
os.makedirs(png_dir, exist_ok=True)

# Itera attraverso tutti i file PDF nella directory
for pdf_file in os.listdir(pdf_dir):
    if pdf_file.endswith('.pdf'):
        # Costruisci il percorso completo del file PDF
        full_pdf_path = os.path.join(pdf_dir, pdf_file)
        
      
        
        # Open the PDF file
        pdf = fitz.open(full_pdf_path)
        file_date = pdf.metadata['creationDate'][2:14]
        # for every page in pdf
        for page in pdf:
            filename = file_date + '_' + str(page.number)
            full_png_path = os.path.join(png_dir, filename  + '.png')
            full_txt_path = os.path.join(png_dir, filename  + '.txt')
            new_pdf_path = os.path.join(png_dir, filename  + '.pdf')
                        
            print (full_png_path)


            # Render page to an image
            pix = page.get_pixmap(dpi=300)


            # Convert the PyMuPDF Pixmap object into a PIL Image object
            pil_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            #pil_image.save(full_png_path)

            # Use pytesseract to do OCR on the PIL image
            text = pytesseract.image_to_string(pil_image)

            # Print the extracted text
            print(text)
            # Write the extracted text to a file
            with open(full_txt_path, 'w') as f:
                f.write(text)
            
            new_pdf = fitz.open()
            new_pdf.insert_pdf(pdf, from_page=page.number, to_page=page.number)
            # Aggiungi una pagina di testo
            
            new_pdf.new_page(width=595, height=842)  # Dimensioni di una pagina A4
            page = new_pdf[1]
            # Imposta il contenuto della pagina di testo
            page.insert_text((72, 72), text, fontsize=8)  # Inserisci il testo nella pagina
        
            
            new_pdf.save(new_pdf_path)
            
print("Done")
