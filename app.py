import streamlit as st
import easyocr
import pandas as pd
import requests
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Initialize OCR reader
reader = easyocr.Reader(['en'], gpu=False)

st.title("Bulk OCR from Image URLs (Chunked & Async)")

uploaded_file = st.file_uploader("Upload a text file containing image URLs (one per line)", type=["txt"])

if uploaded_file:
    image_links = uploaded_file.read().decode("utf-8").splitlines()
    st.success(f"Found {len(image_links)} image URLs!")

    max_threads = st.slider("Number of threads per chunk", min_value=2, max_value=20, value=8)
    chunk_size = st.number_input("Number of images per chunk", min_value=10, max_value=200, value=50, step=10)

    results = []
    progress_text = st.empty()
    progress_bar = st.progress(0)

    def ocr_image(url):
        try:
            response = requests.get(url, timeout=10)
            img = BytesIO(response.content)
            text = reader.readtext(img, detail=0)
            return {"URL": url, "Extracted Text": " | ".join(text)}
        except Exception as e:
            return {"URL": url, "Extracted Text": f"Error: {e}"}

    # Process in chunks
    total_chunks = (len(image_links) + chunk_size - 1) // chunk_size
    for idx in range(total_chunks):
        chunk = image_links[idx*chunk_size : (idx+1)*chunk_size]
        futures = []
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            for url in chunk:
                futures.append(executor.submit(ocr_image, url))
            for i, future in enumerate(as_completed(futures)):
                results.append(future.result())
                overall_idx = idx*chunk_size + i + 1
                progress_text.text(f"Processing {overall_idx}/{len(image_links)}")
                progress_bar.progress(overall_idx / len(image_links))
        # Optional: small pause to free memory
        time.sleep(0.5)

    st.success("OCR Processing Completed!")

    # Show and download results
    df = pd.DataFrame(results)
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download OCR results as CSV", data=csv, file_name='ocr_results.csv', mime='text/csv')
