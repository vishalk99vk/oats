import streamlit as st
from PIL import Image
import requests
from io import BytesIO

st.title("Image Viewer from URL File")

# Upload the text file
uploaded_file = st.file_uploader("Upload a text file with image URLs", type=["txt"])

if uploaded_file is not None:
    # Read the file content
    content = uploaded_file.read().decode("utf-8")
    
    # Split lines to get image URLs
    image_urls = content.strip().split("\n")
    
    st.write(f"Found {len(image_urls)} image URLs.")
    
    # Display each image
    for url in image_urls:
        url = url.strip()
        if url:
            try:
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                st.image(img, caption=url, use_column_width=True)
            except Exception as e:
                st.error(f"Could not load image from URL: {url}\nError: {e}")
