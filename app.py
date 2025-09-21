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
        "⚠️ The `google-generativeai` package is not installed.\n\n"
        "Please run this command in your terminal:\n\n"
        "`pip install google-generativeai`"
    )
    st.stop()

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    # Attempt to get the key from Streamlit secrets if not in .env
    try:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    except (FileNotFoundError, KeyError):
        st.error("⚠️ No GEMINI_API_KEY found. Please add it to your `.env` file or Streamlit secrets.")
        st.stop()

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"⚠️ Error configuring Gemini API: {e}")
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
  "why_card_hi": ["सरल हिंदी में एक बुलेट पॉइंट स्पष्टीकरण।", "यदि आवश्यक हो तो दूसरा बुlet पॉइंट।"],
  "red_flags": ["List of identified risk indicators, e.g., 'Suspicious QR Code', 'Urgent Action Required', 'Unverified Source'."]
}}
User's query text: "{query}"
"""

IMAGE_DESCRIPTION_PROMPT = """
You are an AI image analyst. Your task is to analyze the provided image and its accompanying caption.
1.  **Describe the Image:** Briefly describe the key visual elements and the overall scene.
2.  **Check for Manipulation:** Assess if the image shows obvious signs of being digitally altered, photoshopped, or AI-generated. Mention specific artifacts if you see any.
3.  **Contextual Analysis:** Based on the image and the user's caption, provide a brief conclusion about its likely authenticity, purpose, or context.
Respond in clear and concise Markdown format.
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
        # Create a JSON error response if the API call fails
        return json.dumps({
            "result": "UNSURE",
            "confidence": 0,
            "reason": f"AI analysis failed: {str(e)}",
            "why_card_en": ["Could not analyze the content due to a critical AI error."],
            "why_card_hi": ["एक गंभीर एआई त्रुटि के कारण सामग्री का विश्लेषण नहीं किया जा सका।"],
            "red_flags": ["API Error"]
        })


def call_gemini_for_description(img: Image.Image, caption: str) -> str:
    """Calls Gemini for a descriptive analysis of an image."""
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    prompt_parts = [
        IMAGE_DESCRIPTION_PROMPT,
        f"**User's Caption:** *{caption if caption else 'No caption provided.'}*\n\n---",
        img
    ]
    try:
        resp = model.generate_content(prompt_parts)
        return resp.text
    except Exception as e:
        return f"### ⚠️ An Error Occurred\n\nCould not describe the image. Reason: {e}"


# ----------------- UI HELPER FUNCTIONS -----------------
def get_result_color(result: str) -> str:
    """Returns a hex color code based on the analysis result."""
    return {"FAKE": "#ef4444", "REAL": "#22c55e", "UNSURE": "#eab308"}.get(result, "#9ca3af")


def render_result_ui(data: dict):
    """Renders the formatted result from the analysis data."""
    result = data.get("result", "UNSURE")
    color = get_result_color(result)
    flag_map = {"FAKE": "Red Flag", "REAL": "Green Flag", "UNSURE": "Yellow Flag"}

    with st.container(border=True):
        st.markdown(
            f"<h3 style='color:{color}; border-left: 5px solid {color}; padding-left: 10px;'>"
            f"Result: {result.title()} ({flag_map.get(result)})</h3>",
            unsafe_allow_html=True
        )

        confidence = data.get("confidence", 0)
        st.progress(confidence, text=f"**Confidence: {confidence}%**")
        st.markdown(f"**Reason:** {data.get('reason', 'N/A')}")

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("🇬🇧 **English Summary**")
            for line in data.get("why_card_en", []):
                st.info(line)
        with col2:
            st.markdown("🇮🇳 **Hindi Summary**")
            for line in data.get("why_card_hi", []):
                st.info(line)

        red_flags = data.get("red_flags", [])
        if red_flags:
            st.divider()
            st.markdown("🚨 **Identified Red Flags**")
            for flag in red_flags:
                st.warning(flag)


# ----------------- STREAMLIT UI -----------------
st.set_page_config(layout="wide")
st.title("🕵️ Misinformation Analysis & Image AI")
st.write("Enter text and/or upload an image to analyze for scams, fake news, or manipulation.")

mode = st.radio("Choose mode:", ("Analyze Content", "Describe Image"), horizontal=True)

if mode == "Analyze Content":
    st.subheader("Analyze Text and/or Image")
    text_input = st.text_area("Enter text to analyze (optional):", height=100)
    uploaded_file = st.file_uploader("Upload an image to analyze (optional):", type=['jpg', 'png', 'jpeg'])

    img_obj = None
    if uploaded_file:
        img_obj = Image.open(uploaded_file)
        st.image(uploaded_file, caption="Image to be analyzed", width=300)

    if st.button("Analyze Now", type="primary"):
        if not text_input and not uploaded_file:
            st.warning("Please provide text or upload an image to analyze.")
        else:
            with st.spinner("🧠 Running Gemini Analysis... Please wait."):
                raw_json_result = call_gemini_for_analysis(text_input.strip(), img=img_obj)
            try:
                # Attempt to parse the JSON response
                result_data = json.loads(raw_json_result)
                render_result_ui(result_data)
            except json.JSONDecodeError:
                st.error("Error: Failed to parse the AI's response. The raw output is shown below.")
                st.code(raw_json_result, language="text")

elif mode == "Describe Image":
    st.subheader("Describe an Image")
    uploaded_file = st.file_uploader("Upload an image to describe:", type=['jpg', 'png', 'jpeg'])
    caption = st.text_input("Add a caption for more context (optional):")

    if uploaded_file:
        st.image(uploaded_file, caption="Image to be described", width=300)
        if st.button("Describe Image", type="primary"):
            img_obj = Image.open(uploaded_file)
            with st.spinner("🖼️ Describing image with Gemini..."):
                description = call_gemini_for_description(img_obj, caption)
            st.markdown(description)

st.caption("Powered by Google Gemini 1.5 Flash | Built for educational purposes. [2025]")