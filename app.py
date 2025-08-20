import streamlit as st
import easyocr
import pandas as pd
import requests
from io import BytesIO

# Initialize OCR reader
reader = easyocr.Reader(['en'], gpu=False)  # CPU mode

st.title("Bulk Image OCR from URLs")

# Upload text file with image URLs
uploaded_file = st.file_uploader("Upload a text file containing image URLs (one per line)", type=["txt"])

if uploaded_file:
    # Read image URLs
    image_links = uploaded_file.read().decode("utf-8").splitlines()
    st.success(f"Found {len(image_links)} image URLs!")

    batch_size = st.number_input("Batch size", min_value=10, max_value=200, value=50, step=10)

    @st.cache_data
    def ocr_image(url):
        try:
            response = requests.get(url, timeout=10)
            img = BytesIO(response.content)
            result = reader.readtext(img, detail=0)
            return " | ".join(result)
        except Exception as e:
            return f"Error: {e}"

    results = []
    progress_bar = st.progress(0)
    
    for i in range(0, len(image_links), batch_size):
        batch = image_links[i:i+batch_size]
        for link in batch:
            text = ocr_image(link)
            results.append({"URL": link, "Extracted Text": text})
        progress_bar.progress((i + batch_size)/len(image_links))

    st.success("OCR Processing Completed!")

    # Convert to DataFrame
    df = pd.DataFrame(results)
    st.dataframe(df)

    # Download as CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download OCR results as CSV",
        data=csv,
        file_name='ocr_results.csv',
        mime='text/csv'
    )
