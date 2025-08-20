import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import numpy as np
import easyocr
import time

# Initialize EasyOCR once
reader = easyocr.Reader(['en'], gpu=False)

st.title("Batch OCR from Image URLs")

st.write("Upload a text file containing image URLs (one per line).")

uploaded_file = st.file_uploader("Upload text file", type=["txt"])

if uploaded_file:
    urls = [line.strip() for line in uploaded_file.read().decode("utf-8").splitlines() if line.strip()]
    
    if len(urls) == 0:
        st.warning("No URLs found in the file!")
    else:
        st.success(f"Found {len(urls)} image URLs. Starting OCR...")
        results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, url in enumerate(urls, start=1):
            status_text.text(f"Processing {idx}/{len(urls)}: {url}")
            try:
                response = requests.get(url, timeout=10)
                img = Image.open(BytesIO(response.content)).convert('RGB')
                img_np = np.array(img)
                text = reader.readtext(img_np, detail=0)
                results.append({"URL": url, "Extracted Text": " | ".join(text)})
            except Exception as e:
                results.append({"URL": url, "Extracted Text": f"Error: {e}"})
            
            progress_bar.progress(idx / len(urls))
            time.sleep(0.05)  # slight delay to keep UI responsive
        
        st.success("OCR Completed!")
        
        # Display results in Streamlit
        for res in results:
            st.write(f"**URL:** {res['URL']}")
            st.write(f"**Text:** {res['Extracted Text']}")
            st.markdown("---")
        
        # Option to download results as CSV
        import pandas as pd
        df = pd.DataFrame(results)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download results as CSV",
            data=csv,
            file_name='ocr_results.csv',
            mime='text/csv',
        )
