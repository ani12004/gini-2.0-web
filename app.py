# Save as app.py
import streamlit as st
from dotenv import load_dotenv
import os
import json
import re
from PIL import Image

# ----------------- CONFIG & SETUP -----------------
st.set_page_config(layout="wide", page_title="TechGini - Misinformation Detector")

# --- LOAD API KEY (FROM .ENV OR STREAMLIT SECRETS) ---
load_dotenv()
GEMINI_API_key = os.environ.get("GEMINI_API_KEY")

# ----------------- CUSTOM CSS STYLING -----------------
page_style = """
    <style>
    /* --- GENERAL & TEXT FIXES --- */
    h1, h2, h3, p, li, label { color: #111827 !important; }
    .stApp { background-color: #FFFFFF; }
    .st-emotion-cache-1y4p8pa { padding: 0 5rem; }

    /* --- HEADER (Simplified) --- */
    .header {
        background-color: #2563EB; padding: 1rem; color: white; border-radius: 10px;
        margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;
    }
    .header-title { font-size: 24px; font-weight: bold; color: white !important; }
    .header-subtitle { font-size: 14px; opacity: 0.9; color: white !important; }

    /* --- INPUTS & BUTTONS (FIXED) --- */
    [data-testid="stTextArea"] textarea {
        background-color: #FFFFFF !important; 
        color: #111827 !important; 
        border: 1px solid #D1D5DB !important;
    }

    /* PRIMARY BUTTONS - Blue styling */
    .stButton > button[kind="primary"] {
        background-color: #2563EB !important;
        color: white !important;
        border: none !important;
        border-radius: 0.5rem !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #1D4ED8 !important;
        color: white !important;
    }

    /* SECONDARY BUTTONS - White with border */
    .stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 0.5rem !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #F9FAFB !important;
        color: #111827 !important;
        border-color: #9CA3AF !important;
    }

    /* DEFAULT BUTTONS - White with border */
    .stButton > button {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 0.5rem !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
    }
    .stButton > button:hover {
        background-color: #F9FAFB !important;
        color: #111827 !important;
        border-color: #9CA3AF !important;
    }

    /* LINK BUTTONS */
    .stLinkButton > a {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 0.5rem !important;
        padding: 0.5rem 1rem !important;
        text-decoration: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: 500 !important;
    }
    .stLinkButton > a:hover {
        background-color: #F9FAFB !important;
        color: #111827 !important;
        border-color: #9CA3AF !important;
    }

    /* --- RESULT UI STYLES --- */
    .result-container,
    .info-section {
        border: 1px solid #E5E7EB; 
        border-radius: 10px;
        background-color: #FFFFFF;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .result-container { padding: 2rem; }
    .result-header {
        display: flex; 
        justify-content: space-between; 
        align-items: flex-start; 
        margin-bottom: 1rem;
    }
    .result-title-section .dot {
        height: 15px; 
        width: 15px; 
        border-radius: 50%; 
        display: inline-block;
        margin-right: 10px; 
        vertical-align: middle;
    }
    .result-title { 
        font-size: 20px; 
        font-weight: bold; 
        display: inline-block; 
    }
    .result-subtitle { 
        color: #6B7280 !important; 
        font-size: 14px; 
        margin-top: 5px; 
    }
    .result-confidence-section { text-align: right; }
    .result-confidence-value { 
        font-size: 24px; 
        font-weight: bold; 
    }
    .result-confidence-label { 
        color: #6B7280 !important; 
        font-size: 14px; 
    }
    .confidence-gauge-container {
        margin-top: 2rem; 
        position: relative; 
        padding-bottom: 20px;
        border: none; 
        box-shadow: none; 
        background-color: transparent; 
        padding: 0;
    }
    .gauge-indicator {
        position: absolute; 
        top: -5px; 
        height: 20px; 
        width: 4px; 
        background-color: #111827;
        border-radius: 2px; 
        transform: translateX(-50%); 
        z-index: 10;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .confidence-gauge { 
        display: flex; 
        width: 100%; 
        height: 10px; 
        border-radius: 5px; 
        overflow: hidden; 
    }
    .gauge-fake { background-color: #EF4444; }
    .gauge-unsure { background-color: #FBBF24; }
    .gauge-real { background-color: #22C55E; }
    .gauge-labels { 
        display: flex; 
        justify-content: space-between; 
        font-size: 12px; 
        color: #6B7280; 
        margin-top: 5px; 
    }

    .info-section h3 {
        font-size: 16px; 
        font-weight: bold; 
        margin-bottom: 1rem; 
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #E5E7EB;
    }
    .summary-box { 
        border: none; 
        box-shadow: none; 
        padding: 0; 
    }
    .flag-item {
        border: 1px solid #E5E7EB; 
        padding: 0.75rem 1rem;
        background-color: #F9FAFB; 
        border-radius: 8px; 
        margin-bottom: 0.5rem;
    }
    .flag-item:last-child { margin-bottom: 0; }

    .footer {
        margin-top: 3rem; 
        padding: 2rem 5rem; 
        border-top: 1px solid #E5E7EB; 
        color: #6B7280;
    }
    .footer-container { 
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
        gap: 20px; 
    }
    .footer h4, .footer p, .footer a { color: inherit !important; }
    .footer-copyright {
        text-align: center; 
        margin-top: 2rem; 
        padding-top: 1rem; 
        border-top: 1px solid #E5E7EB;
    }

    /* --- TAB FIXES --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF !important;
        color: #6B7280 !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 0.5rem !important;
        padding: 0.5rem 1rem !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #2563EB !important;
        color: white !important;
        border-color: #2563EB !important;
    }

    /* --- FILE UPLOADER FIXES --- */
    .stFileUploader label {
        color: #111827 !important;
        font-weight: 500 !important;
    }
    .stFileUploader [data-testid="stFileUploaderDropzone"] {
        background-color: #FFFFFF !important;
        border: 2px dashed #D1D5DB !important;
        border-radius: 0.5rem !important;
    }
    .stFileUploader [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #2563EB !important;
    }
    </style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# --- SAFE IMPORT & CONFIGURE GENERATIVEAI ---
try:
    import google.generativeai as genai

    if not GEMINI_API_key:
        st.error("**Error:** `GEMINI_API_KEY` not found. Please add it to your `.env` file or Streamlit secrets.")
        st.stop()
    genai.configure(api_key=GEMINI_API_key)
except ImportError:
    st.error("The `google-generativeai` package is not installed. Please run `pip install google-generativeai`.")
    st.stop()
except Exception as e:
    st.error(f"""
    **API Configuration Error:** Could not configure the Gemini API.
    Please check that your `GEMINI_API_KEY` is correct and active.

    *Technical Detail: {e}*
    """)
    st.stop()

# ----------------- PROMPTS -----------------
UNIVERSAL_ANALYSIS_PROMPT = """
You are an expert AI misinformation and scam detector, with a focus on content relevant to India.
Your task is to analyze content (text and/or image) for signs of scams, fake news, or manipulation.
Classify the content as REAL, FAKE, or UNSURE.
You MUST respond ONLY with a valid JSON object matching this structure:
{{
  "result": "FAKE" | "REAL" | "UNSURE",
  "confidence": 0-100,
  "reason": "A concise, one-sentence technical explanation for your conclusion.",
  "why_card_en": ["A bullet point explanation in simple English.", "A second bullet point if necessary."],
  "why_card_hi": ["सरल हिंदी में एक बुलेट पॉइंट स्पष्टीकरण।", "यदि आवश्यक हो तो दूसरा बुलेट पॉइंट।"],
  "red_flags": ["List of identified risk indicators, e.g., 'Premature Claim', 'Urgent Action Required'."],
  "recommended_actions": ["A short, actionable recommendation, e.g., 'Verify from official sources before sharing.'"]
}}
User's query text: "{query}"
"""


# ----------------- HELPER FUNCTIONS -----------------
def parse_json_from_response(text: str) -> dict | None:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"```json\s*({.*?})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None
    return None


def call_gemini_for_analysis(query: str, img: Image.Image = None) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    prompt_parts = [UNIVERSAL_ANALYSIS_PROMPT.format(query=query if query else "N/A")]
    if img:
        prompt_parts.append(img)
    try:
        resp = model.generate_content(
            prompt_parts, generation_config={"response_mime_type": "application/json"}
        )
        return resp.text
    except Exception as e:
        error_json = {
            "result": "UNSURE", "confidence": 0, "reason": f"AI analysis failed: {str(e)}",
            "why_card_en": ["Could not analyze due to a critical AI error."],
            "why_card_hi": ["एक गंभीर एआई त्रुटि के कारण सामग्री का विश्लेषण नहीं किया जा सका।"],
            "red_flags": ["API Error"], "recommended_actions": ["Review the error and try again."]
        }
        return json.dumps(error_json)


# ----------------- UI RENDER FUNCTION -----------------
def render_result_ui(data: dict):
    result = data.get("result", "UNSURE")
    confidence = data.get("confidence", 0)

    color_map = {"FAKE": "#EF4444", "REAL": "#22C55E", "UNSURE": "#FBBF24"}
    status_map = {"FAKE": "Red Flag", "REAL": "Green Flag", "UNSURE": "Yellow Flag"}
    subtitle_map = {"FAKE": "High risk of misinformation detected", "REAL": "Content appears to be credible",
                    "UNSURE": "Could not determine with high confidence"}

    result_color = color_map.get(result, "#6B7280")

    with st.container(border=True):
        st.markdown(f"""
            <div class="result-header">
                <div class="result-title-section">
                    <span class="dot" style="background-color:{result_color};"></span>
                    <h2 class="result-title" style="color:{result_color};">{result.title()} - {status_map.get(result)}</h2>
                    <p class="result-subtitle">{subtitle_map.get(result)}</p>
                </div>
                <div class="result-confidence-section">
                    <div class="result-confidence-value" style="color:{result_color};">{confidence}%</div>
                    <div class="result-confidence-label">Confidence</div>
                </div>
            </div>
            <div class="confidence-gauge-container">
                <div class="gauge-indicator" style="left: {confidence}%;"></div>
                <div class="confidence-gauge">
                    <div class="gauge-fake" style="width:65%;"></div>
                    <div class="gauge-unsure" style="width:30%;"></div>
                    <div class="gauge-real" style="width:5%;"></div>
                </div>
                <div class="gauge-labels">
                    <span>Fake (0%+)</span>
                    <span>Uncertain (65%+)</span>
                    <span>Real (95%+)</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<h3>Technical Analysis</h3>", unsafe_allow_html=True)
        st.write(data.get('reason', 'N/A'))

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("<h3>GB English Summary</h3>", unsafe_allow_html=True)
            for line in data.get("why_card_en", ["No summary available."]):
                st.markdown(f"- {line}")
    with col2:
        with st.container(border=True):
            st.markdown("<h3>IN Hindi Summary</h3>", unsafe_allow_html=True)
            for line in data.get("why_card_hi", ["कोई सारांश उपलब्ध नहीं है।"]):
                st.markdown(f"- {line}")

    col_flags, col_actions = st.columns(2)

    # Conditionally render the Red Flags section
    flags = data.get("red_flags", [])
    if flags:
        with col_flags:
            with st.container(border=True):
                st.markdown("<h3>Detected Red Flags</h3>", unsafe_allow_html=True)
                for flag in flags:
                    st.markdown(f"<div class='flag-item'>{flag}</div>", unsafe_allow_html=True)

    with col_actions:
        with st.container(border=True):
            st.markdown("<h3>Recommended Actions</h3>", unsafe_allow_html=True)
            st.button("Generate Report for Authorities", type="primary", use_container_width=True)
            c1, c2 = st.columns(2)
            with c1:
                st.button("Share Analysis", type="secondary", use_container_width=True)
            with c2:
                st.button("Download Report", type="secondary", use_container_width=True)


# ----------------- SESSION STATE & MAIN LAYOUT -----------------
if 'text_input' not in st.session_state:
    st.session_state.text_input = ""


def clear_text():
    st.session_state.text_input = ""


# --- HEADER ---
st.markdown("""
<div class="header">
    <div>
        <div class="header-title">TechGini</div>
        <div class="header-subtitle">AI-Powered Misinformation Detection</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.title("Detect Misinformation Instantly")
st.write(
    "Analyze text, URLs, and images to identify potential misinformation, scams, or fake news with our advanced AI.")
tab1, tab2 = st.tabs(["Text & URL Analysis", "Image Analysis"])


def run_analysis(raw_text_result: str):
    result_data = parse_json_from_response(raw_text_result)
    if result_data:
        render_result_ui(result_data)
    else:
        st.error("The AI returned a response that could not be understood. Please try your request again.")
        with st.expander("See technical details"):
            st.code(raw_text_result, language="text")


with tab1:
    with st.container(border=True):
        st.subheader("Enter Text or URL to Analyze")
        text_input = st.text_area(
            "Paste the content you want to verify here...", height=150, key="text_input_widget",
            value=st.session_state.text_input
        )
        st.caption("Minimum 10 characters required for analysis.")
        st.session_state.text_input = text_input
        col1, col2, _ = st.columns([0.2, 0.2, 0.6])
        with col1:
            analyze_button = st.button("Analyze Content", type="primary", use_container_width=True)
        with col2:
            st.button("Clear", use_container_width=True, on_click=clear_text)

    if analyze_button:
        if len(st.session_state.text_input.strip()) < 10:
            st.warning("Please enter at least 10 characters to analyze.")
        else:
            with st.spinner("Analyzing text... Please wait."):
                raw_json_result = call_gemini_for_analysis(st.session_state.text_input.strip(), img=None)
                run_analysis(raw_json_result)

with tab2:
    with st.container(border=True):
        st.subheader("Upload an Image to Analyze")
        uploaded_file = st.file_uploader(
            "Choose an image file...", type=['jpg', 'png', 'jpeg'], key="file_uploader_widget"
        )
        image_caption = st.text_input("Optional: Add a caption or context for the image.")
        col1, col2, _ = st.columns([0.2, 0.2, 0.6])
        with col1:
            analyze_img_button = st.button("Analyze Image", type="primary", use_container_width=True)
        with col2:
            # Using a simple refresh approach for clearing
            if st.button("Clear Image", use_container_width=True):
                st.rerun()

    if uploaded_file:
        st.image(uploaded_file, caption="Image to be analyzed", width=300)

    if analyze_img_button:
        if uploaded_file is None:
            st.warning("Please upload an image to analyze.")
        else:
            with st.spinner("Analyzing image... Please wait."):
                img_obj = Image.open(uploaded_file)
                raw_json_result = call_gemini_for_analysis(image_caption.strip(), img=img_obj)
                run_analysis(raw_json_result)

# --- Footer ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <div class="footer-container">
        <div>
            <h4>TechGini</h4>
            <p>Protecting communities from misinformation through advanced AI technology.</p>
        </div>
        <div>
            <h4>Features</h4>
            <a href="#">Real-time Analysis</a>
            <a href="#">Multi-language Support</a>
            <a href="#">Image Detection</a>
        </div>
        <div>
            <h4>Resources</h4>
            <a href="#">API Documentation</a>
            <a href="#">Telegram Bot</a>
            <a href="#">Community</a>
        </div>
        <div>
            <h4>Contact</h4>
            <p>support@techgini.ai</p>
            <p>@TechGiniBot</p>
            <a href="#">GitHub</a>
        </div>
    </div>
    <div class="footer-copyright">
        © 2025 TechGini. Built with AI for truth and transparency.
    </div>
</div>
""", unsafe_allow_html=True)
