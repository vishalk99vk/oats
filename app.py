import streamlit as st
import easyocr
import requests
from io import BytesIO
import gc

st.title("Lightweight Bulk Image OCR")

# Initialize OCR reader once
reader = easyocr.Reader(['en'], gpu=False)

# Input links
image_links_text = st.text_area("Paste image URLs (one per line)", height=200)

if st.button("Run OCR"):
    links = [line.strip() for line in image_links_text.split("\n") if line.strip()]
    if not links:
        st.error("Please enter image URLs")
    else:
        results = []
        for idx, url in enumerate(links, 1):
            with st.spinner(f"Processing image {idx}/{len(links)}"):
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    img_bytes = BytesIO(response.content)
                    ocr_result = reader.readtext(img_bytes)
                    text = " ".join([r[1] for r in ocr_result]) if ocr_result else ""
                    results.append({"url": url, "text": text})
                except Exception as e:
                    results.append({"url": url, "text": f"Error: {str(e)}"})
                finally:
                    del img_bytes
                    gc.collect()

        st.success("OCR Completed!")

        # Show results
        for res in results:
            st.write(f"**URL:** {res['url']}")
            st.write(f"**Text:** {res['text']}")
            st.markdown("---")
