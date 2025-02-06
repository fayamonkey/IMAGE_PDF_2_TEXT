import streamlit as st
import PyPDF2
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
import json
import io
import base64

def extract_text_from_pdf(pdf_file):
    # PDF-Datei einmal in den Speicher laden
    pdf_bytes = pdf_file.read()
    pdf_file.seek(0)  # Datei-Pointer zurücksetzen
    
    # Text extrahieren
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    images = []
    
    # Text aus PDF extrahieren
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    
    # Bilder aus PDF extrahieren
    pdf_images = convert_from_bytes(pdf_bytes)
    for i, image in enumerate(pdf_images):
        # OCR auf Bildern durchführen
        image_text = pytesseract.image_to_string(image)
        images.append({
            "page": i+1,
            "image_text": image_text
        })
    
    return text, images

def create_markdown(text, images):
    markdown = "# PDF Analyse\n\n"
    markdown += "## Extrahierter Text\n\n"
    markdown += text + "\n\n"
    markdown += "## Extrahierter Text aus Bildern\n\n"
    
    for img in images:
        markdown += f"### Seite {img['page']}\n"
        markdown += img['image_text'] + "\n\n"
    
    return markdown

def main():
    st.title("PDF Analyse Tool")
    
    uploaded_files = st.file_uploader("PDF Dateien hochladen", 
                                    type="pdf", 
                                    accept_multiple_files=True)
    
    if uploaded_files:
        all_results = []
        
        for pdf_file in uploaded_files:
            st.write(f"Verarbeite: {pdf_file.name}")
            
            text, images = extract_text_from_pdf(pdf_file)
            
            result = {
                "filename": pdf_file.name,
                "text": text,
                "images": images
            }
            all_results.append(result)
        
        # JSON erstellen
        json_str = json.dumps(all_results, ensure_ascii=False, indent=2)
        
        # Markdown erstellen
        markdown = ""
        for result in all_results:
            markdown += f"# {result['filename']}\n\n"
            markdown += create_markdown(result['text'], result['images'])
        
        # Download Buttons
        st.download_button(
            label="JSON herunterladen",
            data=json_str,
            file_name="pdf_analysis.json",
            mime="application/json"
        )
        
        st.download_button(
            label="Markdown herunterladen",
            data=markdown,
            file_name="pdf_analysis.md",
            mime="text/markdown"
        )

if __name__ == "__main__":
    main() 