import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai

# 1. Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Page Configuration
st.set_page_config(
    page_title="DevAudit AI | Enterprise Code Reviewer",
    page_icon="🛡️",
    layout="wide"
)

# 3. Advanced UI / UX Styling (Glassmorphism & High Contrast)
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 50% 10%, #1e1b4b 0%, #090d16 70%);
        color: #f8fafc;
    }
    [data-testid="stSidebar"] {
        background-color: #050811 !important;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown p {
        color: #f1f5f9 !important;
        font-weight: 500 !important;
    }
    /* Style selectboxes and multiselects */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    /* Code input text area */
    textarea, .stTextArea textarea {
        background-color: #050811 !important;
        color: #38bdf8 !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 0.95rem !important;
    }
    /* Hero header styling */
    .hero-container {
        padding: 1.5rem 2rem;
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 16px;
        backdrop-filter: blur(12px);
        margin-bottom: 1.5rem;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
    }
    /* Custom buttons */
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6, #6366f1) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
    }
</style>
""", unsafe_allow_html=True)

if not api_key:
    st.error("⚠️ GEMINI_API_KEY not found in your .env file! Please configure it to proceed.")
    st.stop()

client = genai.Client(api_key=api_key)

# Initialize session state for code input
if "code_text" not in st.session_state:
    st.session_state.code_text = ""

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🛡️ DevAudit Control")
    st.markdown("Configure your automated code security analyzer parameters below.")
    
    language = st.selectbox(
        "Programming Language", 
        ["Python", "JavaScript / TypeScript", "C++ / C", "Java", "SQL", "Go", "Other"]
    )
    
    audit_focus = st.multiselect(
        "Audit Focus Areas",
        ["Security Vulnerabilities", "Bug Detection", "Performance Optimization", "Clean Code & Best Practices"],
        default=["Security Vulnerabilities", "Bug Detection"]
    )
    
    st.divider()
    st.markdown("### 📊 Engine Status")
    st.markdown("🟢 **Model:** `gemini-flash-lite-latest`")
    st.markdown("🔒 **Security Scanner:** Active")
    st.divider()
    st.caption("Labmentix Internship Portfolio Project • Built with Streamlit & Google Gemini SDK")

# --- MAIN HERO HEADER ---
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🛡️ DevAudit AI</div>
    <div class="hero-subtitle">Enterprise-grade automated code review, vulnerability scanner, and refactoring assistant powered by Google Gemini.</div>
</div>
""", unsafe_allow_html=True)

# --- QUICK PRESET SAMPLES ---
st.markdown("💡 **Quick Test Presets:** Click a button below to load a sample buggy snippet instantly!")
col_p1, col_p2, col_p3 = st.columns(3)

if col_p1.button("🧪 SQL Injection Bug"):
    st.session_state.code_text = "def get_user(user_id):\n    query = 'SELECT * FROM users WHERE id = ' + user_id\n    return db.execute(query)"
if col_p2.button("🧪 Hardcoded Secret"):
    st.session_state.code_text = "API_KEY = 'sk-live-998877665544332211'\ndef connect_stripe():\n    stripe.api_key = API_KEY"
if col_p3.button("🧪 Infinite Loop / Memory"):
    st.session_state.code_text = "def process_items(items):\n    while len(items) > 0:\n        item = items.pop()\n        # missing break condition or error check"

# Code Input Area linked to session state
code_input = st.text_area("Paste your code snippet here:", value=st.session_state.code_text, height=220, key="code_input_box")

# --- RUN AUDIT ACTION ---
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    run_audit = st.button("🚀 Run Code Audit", type="primary")

if run_audit:
    # Use code_input from the text area widget
    if not code_input.strip():
        st.warning("⚠️ Please paste some code or select a preset to audit first!")
    else:
        prompt = (
            f"You are an elite Principal Software Engineer and Cybersecurity Auditor. "
            f"Review the following {language} code snippet focusing on: {', '.join(audit_focus)}.\n\n"
            f"Provide your response in structured, beautifully formatted Markdown:\n"
            f"1. **Executive Summary of Code Quality & Risk Score** (e.g. Low, Medium, Critical Risk)\n"
            f"2. **Detailed Bugs & Vulnerabilities Found** (categorized by severity)\n"
            f"3. **Production-Ready / Refactored Code** (secure, clean, well-commented code block)\n"
            f"4. **Key Recommendations & Best Practices**\n\n"
            f"--- CODE SNIPPET ---\n{code_input}\n--- END CODE ---"
        )

        with st.spinner("🔍 Running deep static analysis & security threat modeling..."):
            try:
                response = client.models.generate_content(
                    model="gemini-flash-lite-latest",
                    contents=prompt
                )
                st.markdown("---")
                st.subheader("📋 Comprehensive Audit Report")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Audit generation failed: {e}")