import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import easyocr  # pure Python OCR library

# Initialize OCR reader
reader = easyocr.Reader(['en'])  # English language

st.title("OCR from Image URLs")

uploaded_file = st.file_uploader("Upload a text file with image URLs", type="txt")

if uploaded_file:
    urls = uploaded_file.read().decode("utf-8").splitlines()
    for url in urls:
        st.write(f"Processing: {url}")
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))

            # Run OCR
            result = reader.readtext(response.content)
            extracted_text = " ".join([text[1] for text in result])

            st.image(img, caption="Image")
            st.text_area("Extracted Text", extracted_text, height=150)
        except Exception as e:
            st.error(f"Failed to process {url}: {e}")
