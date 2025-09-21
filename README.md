# 🌐 Gini Web 2.0 - AI Misinformation Detector Web App  
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) ![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg) ![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red)  

Gini Web 2.0 is a **web-based application** powered by the **Google Gemini API**, designed to analyze text and detect potential misinformation, scams, or fake news with a focus on the Indian context.  

---

## ✨ Key Features  
- 💬 **Conversational AI** – Chat with the assistant directly in your browser.  
- 🔎 **Misinformation Detector** – Enter text or URLs to analyze for red flags.  
- 📝 **Complaint Generation** – Generate a ready-to-use complaint template for high-risk content.  
- 🌍 **Bilingual Summaries** – Get results in both **English and Hindi**.  
- 📊 **Logs & Error Tracking** – All analyses and errors are logged for reference.  

---

## 🚀 Getting Started  

### Prerequisites  
- Python **3.9 or higher**  
- A **Google Gemini API Key**  

### Installation  

1. Clone the repository  
   ```bash
   git clone https://github.com/ani12004/gini-web-2.0.git
   cd gini-web-2.0
    ```
2.Create and activate a virtual environment
 ```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
Install dependencies
 ```

 ```bash
pip install -r requirements.txt
 ```
# Set up environment variables

Create a .env file in the project root.

Add your Gemini API Key:

 ```bash
.env
GEMINI_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY_HERE"
 ```
Run the web app
 ```bash
streamlit run main.py
 ```
