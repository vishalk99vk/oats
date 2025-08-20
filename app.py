import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from io import BytesIO
import easyocr
import asyncio
import httpx
import time

# Initialize OCR reader
reader = easyocr.Reader(['en'], gpu=False)

st.title("Fast Batch OCR from Image URLs")

uploaded_file = st.file_uploader("Upload text file with image URLs", type=["txt"])

if uploaded_file:
    urls = [line.strip() for line in uploaded_file.read().decode("utf-8").splitlines() if line.strip()]
    
    if not urls:
        st.warning("No URLs found!")
    else:
        st.info(f"Processing {len(urls)} images in batches of 20 asynchronously...")
        results = []
        batch_size = 20
        
        progress_bar = st.progress(0)
        status_text = st.empty()

        async def fetch_image(client, url):
            try:
                response = await client.get(url, timeout=15)
                img = Image.open(BytesIO(response.content)).convert('RGB')
                return np.array(img)
            except Exception as e:
                return f"Error: {e}"

        async def process_batch(batch):
            async with httpx.AsyncClient() as client:
                images = await asyncio.gather(*[fetch_image(client, url) for url in batch])
                batch_results = []
                for idx, img_np in enumerate(images):
                    url = batch[idx]
                    if isinstance(img_np, str):
                        batch_results.append({"URL": url, "Text": img_np})
                    else:
                        text = reader.readtext(img_np, detail=0)
                        batch_results.append({"URL": url, "Text": " | ".join(text)})
                        del img_np  # free memory
                return batch_results

        async def main():
            for start in range(0, len(urls), batch_size):
                batch = urls[start:start+batch_size]
                status_text.text(f"Processing images {start+1} to {min(start+batch_size, len(urls))}")
                batch_results = await process_batch(batch)
                results.extend(batch_results)
                pd.DataFrame(results).to_csv("temp_ocr_results.csv", index=False)
                progress_bar.progress(min(start+batch_size, len(urls)) / len(urls))
                await asyncio.sleep(0.05)

        asyncio.run(main())

        st.success("OCR Completed!")
        st.download_button("Download final CSV", 
                           data=pd.DataFrame(results).to_csv(index=False).encode('utf-8'), 
                           file_name="ocr_results.csv")
