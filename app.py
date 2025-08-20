import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import easyocr

st.title("Image Viewer with OCR (Pure Python)")

# Upload a text file
uploaded_file = st.file_uploader("Upload a text file with image URLs", type="txt")

if uploaded_file is not None:
    # Read URLs from the file
    urls = uploaded_file.read().decode("utf-8").splitlines()

    # Initialize EasyOCR Reader
    reader = easyocr.Reader(['en'])  # Use English

    for i, url in enumerate(urls):
        st.subheader(f"Image {i+1}")
        try:
            response = requests.get(url)
            image = Image.open(BytesIO(response.content))
            st.image(image, caption=f"Image {i+1}", use_column_width=True)

            # Run OCR
            results = reader.readtext(response.content if isinstance(response.content, bytes) else image)
            detected_text = "\n".join([res[1] for res in results])
            
            if detected_text.strip() == "":
                st.info("No text detected in this image.")
            else:
                st.text_area("Detected Text", detected_text, height=150)

        except Exception as e:
            st.error(f"Error loading image {i+1}: {e}")
