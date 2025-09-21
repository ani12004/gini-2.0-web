# Save as app.py
import streamlit as st
from dotenv import load_dotenv
import os
import json
from PIL import Image
import io

# ----------------- SAFE IMPORT & CONFIG -----------------
try:
    import google.generativeai as genai
except ImportError:
    st.error(
        "The `google-generativeai` package is not installed.\n\n"
        "Please run this command in your terminal:\n\n"
        "`pip install google-generativeai`"
    )
    st.stop()

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    try:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    except (FileNotFoundError, KeyError):
        st.error("GEMINI_API_KEY not found. Please add it to your .env file or Streamlit secrets.")
        st.stop()

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"Error configuring the Gemini API: {e}")
    st.stop()

# ----------------- PROMPTS -----------------
UNIVERSAL_ANALYSIS_PROMPT = """
You are an expert AI misinformation and scam detector, with a focus on content relevant to India.
Your task is to analyze content, which may include text and/or an image, for any signs of scams, fake news, or malicious manipulation.
Based on your analysis, classify the content as REAL, FAKE, or UNSURE.
You MUST respond ONLY with a valid JSON object matching this structure:
{{
  "result": "FAKE" | "REAL" | "UNSURE",
  "confidence": 0-100,
  "reason": "A short, technical reason for your conclusion based on all provided content.",
  "why_card_en": ["A bullet point explanation in simple English.", "A second bullet point if necessary."],
  "why_card_hi": ["सरल हिंदी में एक बुलेट पॉइंट स्पष्टीकरण।", "यदि आवश्यक हो तो दूसरा बुलेट पॉइंट।"],
  "red_flags": ["List of identified risk indicators, e.g., 'Suspicious QR Code', 'Urgent Action Required', 'Unverified Source'."]
}}
User's query text: "{query}"
"""

# ----------------- GEMINI API CALLS -----------------
def call_gemini_for_analysis(query: str, img: Image.Image = None) -> str:
    """Calls Gemini for structured analysis and returns a JSON string."""
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    prompt_parts = [UNIVERSAL_ANALYSIS_PROMPT.format(query=query if query else "N/A")]
    if img:
        prompt_parts.append(img)

    try:
        resp = model.generate_content(
            prompt_parts,
            generation_config={"response_mime_type": "application/json"}
        )
        return resp.text
    except Exception as e:
        return json.dumps({
            "result": "UNSURE",
            "confidence": 0,
            "reason": f"AI analysis failed: {str(e)}",
            "why_card_en": ["Could not analyze the content due to a critical AI error."],
            "why_card_hi": ["एक गंभीर एआई त्रुटि के कारण सामग्री का विश्लेषण नहीं किया जा सका।"],
            "red_flags": ["API Error"]
        })

# ----------------- UI HELPER FUNCTIONS -----------------
def get_result_color(result: str) -> str:
    """Returns a hex color code based on the analysis result."""
    return {"FAKE": "#D32F2F", "REAL": "#388E3C", "UNSURE": "#FBC02D"}.get(result, "#616161")

def render_result_ui(data: dict):
    """Renders the formatted result from the analysis data in a clean UI."""
    result = data.get("result", "UNSURE")
    color = get_result_color(result)

    with st.container(border=True):
        st.markdown(
            f"<h3 style='color:{color};'>Analysis Result: {result.title()}</h3>",
            unsafe_allow_html=True
        )
        st.divider()

        confidence = data.get("confidence", 0)
        st.progress(confidence, text=f"Confidence Score: {confidence}%")
        st.markdown(f"**Conclusion:** {data.get('reason', 'Not available.')}")

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("English Summary")
            for line in data.get("why_card_en", ["No summary available."]):
                st.markdown(f"- {line}")
        with col2:
            st.subheader("Hindi Summary")
            for line in data.get("why_card_hi", ["कोई सारांश उपलब्ध नहीं है।"]):
                st.markdown(f"- {line}")

        red_flags = data.get("red_flags", [])
        if red_flags:
            st.divider()
            st.subheader("Identified Red Flags")
            for flag in red_flags:
                st.markdown(f"- _{flag}_")

# ----------------- STREAMLIT UI -----------------
st.set_page_config(layout="centered", page_title="Content Analysis AI")
st.title("Content Analysis AI")
st.write("Analyze text or images for misinformation, scams, or manipulation.")

tab1, tab2 = st.tabs(["Text Analysis", "Image Analysis"])

with tab1:
    st.header("Analyze Text Content")
    text_input = st.text_area("Enter the text you want to analyze below:", height=150, key="text_analyzer")

    if st.button("Analyze Text", type="primary", use_container_width=True, key="text_button"):
        if not text_input.strip():
            st.warning("Please enter some text to analyze.")
        else:
            with st.spinner("Analyzing text... Please wait."):
                raw_json_result = call_gemini_for_analysis(text_input.strip(), img=None)
                try:
                    result_data = json.loads(raw_json_result)
                    render_result_ui(result_data)
                except json.JSONDecodeError:
                    st.error("Error: Could not parse the AI's response.")
                    st.code(raw_json_result, language="text")

with tab2:
    st.header("Analyze an Image")
    uploaded_file = st.file_uploader("Choose an image file to analyze:", type=['jpg', 'png', 'jpeg'], key="image_uploader")
    image_caption = st.text_input("Optional: Add a caption or context for the image:", key="image_caption")

    if uploaded_file:
        st.image(uploaded_file, caption="Image to be analyzed", use_column_width=True)

    if st.button("Analyze Image", type="primary", use_container_width=True, key="image_button"):
        if not uploaded_file:
            st.warning("Please upload an image to analyze.")
        else:
            with st.spinner("Analyzing image... Please wait."):
                img_obj = Image.open(uploaded_file)
                raw_json_result = call_gemini_for_analysis(image_caption.strip(), img=img_obj)
                try:
                    result_data = json.loads(raw_json_result)
                    render_result_ui(result_data)
                except json.JSONDecodeError:
                    st.error("Error: Could not parse the AI's response.")
                    st.code(raw_json_result, language="text")

st.markdown("---")
st.caption("Powered by Google Gemini 1.5 Flash. This tool is for educational purposes.")
