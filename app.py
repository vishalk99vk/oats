import streamlit as st
import requests
from PIL import Image

st.title("Image Viewer with OCR (No Heavy Libraries)")

# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Display uploaded image
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    # OCR.space API key (use 'helloworld' for free testing)
    api_key = "helloworld"
    ocr_url = "https://api.ocr.space/parse/image"

    with st.spinner("Extracting text from image..."):
        try:
            # Send image to OCR API
            response = requests.post(
                ocr_url,
                files={"file": uploaded_file.getvalue()},
                data={"apikey": api_key, "language": "eng"}
            )
            result = response.json()

            # Extract text
            text = result["ParsedResults"][0]["ParsedText"]
            st.subheader("Extracted Text")
            st.text_area("", text, height=200)

        except Exception as e:
            st.error(f"Error during OCR: {e}")
