import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

from fileparser import extract_text_from_file
from nlpengine import compute_similarity
from scoringengine import weighted_score
from feedbackengine import generate_feedback, ats_feedback

# ================= PAGE CONFIG =================
st.set_page_config(page_title="UNIMAS Resume Relevance Scorer", layout="wide")

# ================= CUSTOM CSS (Shading & Depth) =================
st.markdown("""
<style>
    /* Main Background */
    .stApp { background-color: #F8FAFC; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; }

    /* TITLE SHADING: This creates the shaded block behind your title */
    .title-container {
        background-color: #1E293B; /* Deep Slate Shading */
        padding: 40px 50px;
        border-radius: 12px;
        margin-bottom: 30px;
        border-left: 6px solid #6366F1; /* Indigo accent line */
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    /* CARD SHADING: Subtly shades the input areas */
    .input-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* LABEL SHADING: Small shaded boxes for headers */
    .label-shade {
        background-color: #F1F5F9;
        color: #475569;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-bottom: 12px;
    }

    /* System Status Items */
    .status-item {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        font-size: 13px;
        color: #64748B;
        border-bottom: 1px solid #F1F5F9;
    }
    .status-value { color: #6366F1; font-weight: 600; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR (System State) =================
with st.sidebar:
    st.markdown("<h2 style='color:#1E293B; font-size:22px; font-weight:800;'>UNIMAS FYP</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6366F1; font-size:12px; font-weight:600; margin-top:-15px;'>NLP RELEVANCE ENGINE</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    page = st.radio("NAVIGATION", ["Dashboard", "Pool", "Documentation"])
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:10px; color:#94A3B8; font-weight:800; letter-spacing:0.1em;'>SYSTEM STATE</p>", unsafe_allow_html=True)
    
    stats = {"CORE": "Python 3.14", "ENGINE": "TF-IDF", "METRIC": "Cosine", "LIB": "NLTK v3.8"}
    for label, val in stats.items():
        st.markdown(f"<div class='status-item'>{label} <span class='status-value'>{val}</span></div>", unsafe_allow_html=True)
    st.success("SYSTEM READY")

# ================= MAIN CONTENT =================
if page == "Dashboard":
    # THE SHADED TITLE SECTION
    st.markdown("""
        <div class="title-container">
            <h1 style="color:#FFFFFF; font-size:30px; font-weight:800; margin:0;">Resume Relevance Scoring System</h1>
            <p style="color:#94A3B8; font-size:15px; margin-top:5px; font-weight:500;">
                Advanced NLP Prototype for Recruitment Evaluation
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Inputs with Shaded Cards
    col_jd, col_res = st.columns(2, gap="large")
    
    with col_jd:
        st.markdown("<div class='input-card'>", unsafe_allow_html=True)
        st.markdown("<div class='label-shade'>JOB DESCRIPTION INPUT</div>", unsafe_allow_html=True)
        job_desc = st.text_area("JD_Input", height=300, label_visibility="collapsed", placeholder="Paste official job description requirements here...")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_res:
        st.markdown("<div class='input-card'>", unsafe_allow_html=True)
        st.markdown("<div class='label-shade'>CANDIDATE DOCUMENT</div>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Upload", type=["pdf", "docx"], accept_multiple_files=True, label_visibility="collapsed")
        st.info("System optimized for PDF and DOCX formats.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Run Button
    st.markdown("<br>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1.5, 1, 1.5])
    with center_col:
        if st.button("RUN AI ANALYSIS", use_container_width=True):
            if not uploaded_files or not job_desc.strip():
                st.error("Protocol Error: Provide input data.")
            else:
                with st.spinner("Analyzing..."):
                    # (Your Analysis Logic Here)
                    pass