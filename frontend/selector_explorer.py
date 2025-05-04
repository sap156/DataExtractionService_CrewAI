import streamlit as st
import requests
import json

st.set_page_config(page_title="CrewAI Data Tools", layout="wide")
st.title("🧠 CrewAI-Powered Data Extraction Suite")

tab1, tab2, tab3 = st.tabs(["🌐 Web Scraper", "🖼️ Image Text Extractor", "📄 File Text Extractor"])

# ------------------- TAB 1: WEB SCRAPER -------------------
with tab1:
    st.subheader("Extract content from any webpage and query it using OpenAI")

    url = st.text_input("🌍 Enter the webpage URL", "https://en.wikipedia.org/wiki/Main_Page")

    if url and st.button("🚀 Scrape & Structure"):
        with st.spinner("Scraping content..."):
            try:
                res = requests.get("http://localhost:8000/api/scrape-all", params={"url": url})
                data = res.json()

                if "result" in data:
                    formatted = data["result"]
                    st.session_state.structured_data = formatted
                    st.success("✅ Structured content:")
                    st.code(formatted, language="json")

                    # ✅ Download button for structured data
                    st.download_button(
                        label="📥 Download JSON",
                        data=formatted,
                        file_name="scraped_data.json",
                        mime="application/json"
                    )
                else:
                    st.error(data.get("error", "No data returned."))

            except Exception as e:
                st.error(f"Scraping failed: {e}")

    # Ask questions about the structured data
    if "structured_data" in st.session_state:
        st.markdown("---")
        st.subheader("🔍 Ask a Question on the Scraped Data")
        user_question = st.text_input("What do you want to know?")
        if user_question and st.button("Ask OpenAI"):
            try:
                payload = {
                    "data": st.session_state.structured_data,
                    "question": user_question
                }
                res = requests.post("http://localhost:8000/api/ask", json=payload)
                data = res.json()
                if "answer" in data:
                    st.success("OpenAI's Answer:")
                    st.write(data["answer"])
                else:
                    st.error(data.get("error", "No answer returned."))
            except Exception as e:
                st.error(f"Q&A failed: {e}")


# ------------------- TAB 2: IMAGE TEXT EXTRACTOR -------------------
with tab2:
    st.subheader("Extract content from an image using Vision AI")

    image_file = st.file_uploader("📷 Upload an image", type=["png", "jpg", "jpeg", "webp", "gif"])

    if image_file and st.button("Extract Text from Image"):
        with st.spinner("Analyzing image with Vision Tool..."):
            try:
                files = {"file": (image_file.name, image_file, image_file.type)}
                res = requests.post("http://localhost:8000/api/vision", files=files)
                data = res.json()

                if "result" in data:
                    st.success("✅ Extracted Text:")
                    st.text_area("Result", data["result"], height=300)

                    # ✅ Add download button
                    json_bytes = data["result"].encode("utf-8")
                    st.download_button(
                        label="⬇️ Download JSON",
                        data=json_bytes,
                        file_name="extracted_text.json",
                        mime="application/json"
                    )
                else:
                    st.error(data.get("error", "No text extracted from the image."))
            except Exception as e:
                st.error(f"Vision tool failed: {e}")


# ------------------- TAB 3: FILE TEXT EXTRACTOR -------------------
with tab3:
    st.subheader("Upload a file to read its content")

    file = st.file_uploader("📄 Upload a text file", type=["txt", "csv", "json"])

    if file and st.button("Extract Text from File"):
        with st.spinner("Reading file..."):
            try:
                res = requests.post("http://localhost:8000/api/file-read", files={"file": file})
                data = res.json()
                if "result" in data:
                    st.success("Extracted Text:")
                    st.text_area("Result", data["result"], height=300)
                else:
                    st.error(data.get("error", "No text found."))
            except Exception as e:
                st.error(f"File read failed: {e}")
