import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import pytesseract

st.title("Image Viewer with OCR")

# Upload the text file
uploaded_file = st.file_uploader("Upload a text file with image URLs", type=["txt"])

if uploaded_file is not None:
    # Read the file content
    content = uploaded_file.read().decode("utf-8")
    
    # Split lines to get image URLs
    image_urls = content.strip().split("\n")
    
    st.write(f"Found {len(image_urls)} image URLs.")
    
    # Display each image and detected text
    for url in image_urls:
        url = url.strip()
        if url:
            try:
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                
                st.image(img, caption=f"Image: {url}", use_column_width=True)
                
                # Run OCR
                text = pytesseract.image_to_string(img)
                
                st.subheader("Detected Text:")
                st.text(text if text.strip() else "No text detected")
                
            except Exception as e:
                st.error(f"Could not load image from URL: {url}\nError: {e}")
