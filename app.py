from paddleocr import PaddleOCR
import streamlit as st
from PIL import Image
import requests
from io import BytesIO

st.title("Image OCR Viewer")

uploaded_file = st.file_uploader("Upload a text file with image URLs", type=["txt"])

if uploaded_file:
    urls = uploaded_file.read().decode("utf-8").splitlines()
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    for url in urls:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        st.image(img, caption=url, use_column_width=True)
        result = ocr.ocr(url, cls=True)
        text = "\n".join([line[1][0] for line in result[0]])
        st.text_area(f"OCR Text for {url}", text, height=150)
