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

# ================= CUSTOM CSS (The AI Studio Aesthetic) =================
st.markdown("""
<style>
    /* Main Background & Font */
    .stApp { background-color: #FFFFFF; font-family: 'Inter', 'Segoe UI', sans-serif; }
    
    /* Sidebar Styling - Dark Theme per image_23c124.png */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Input Box Styling */
    .stTextArea textarea, .stFileUploader section {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
    }

    /* System Status Badges */
    .status-item {
        display: flex;
        justify-content: space-between;
        padding: 5px 0;
        font-size: 13px;
        color: #64748B;
        border-bottom: 1px solid #F1F5F9;
    }
    .status-value { color: #4F46E5; font-weight: 600; font-family: monospace; }
    
    /* Run Analysis Button - Ghost Style */
    .stButton > button {
        background-color: #F1F5F9 !important;
        color: #475569 !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #E2E8F0 !important;
        border-color: #CBD5E1 !important;
    }

    /* Card Containers */
    .card {
        border: 1px solid #E2E8F0;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR (System State) =================
with st.sidebar:
    st.markdown("<h2 style='color:#1E293B; font-size:20px;'>UNIMAS FYP</h2>", unsafe_allow_html=True)
    st.caption("NLP RESUME SCORING")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    page = st.radio("NAVIGATION", ["Dashboard", "Resume Pool", "Documentation"])
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:12px; color:#94A3B8; font-weight:700;'>SYSTEM STATE</p>", unsafe_allow_html=True)
    
    # Matching your image_23c124.png sidebar exactly
    stats = {
        "CORE ENGINE": "Python 3.14",
        "VECTORIZATION": "TF-IDF Active",
        "SIMILARITY": "Cosine-Dist",
        "NLP LIB": "NLTK v3.8"
    }
    for label, val in stats.items():
        st.markdown(f"<div class='status-item'>{label} <span class='status-value'>{val}</span></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.success("SYSTEM READY")

# ================= MAIN CONTENT =================
if page == "Dashboard":
    # Header per image_1706c1.png
    st.title("Resume Relevance Scoring System")
    st.caption("NLP-Based Recruitment Evaluation Prototype")
    
    # 2-Column Layout matching image_16ff3f.png
    col_jd, col_res = st.columns(2, gap="large")
    
    with col_jd:
        st.markdown("<p style='font-weight:700; color:#64748B; font-size:12px;'>JOB DESCRIPTION</p>", unsafe_allow_html=True)
        job_desc = st.text_area("JD_Input", height=300, label_visibility="collapsed", placeholder="Paste the official Job Description requirements here...")
        
    with col_res:
        st.markdown("<p style='font-weight:700; color:#64748B; font-size:12px;'>RESUME DOCUMENT</p>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Resume_Upload", type=["pdf", "docx"], accept_multiple_files=True, label_visibility="collapsed")
        st.info("Upload PDF or DOCX (Max 3 resumes for comparison)")

    # Centered Run Analysis Button
    _, center_col, _ = st.columns([1, 1, 1])
    with center_col:
        run_analysis = st.button("RUN ANALYSIS")

    # ================= ANALYSIS LOGIC =================
    if run_analysis:
        if not uploaded_files or not job_desc.strip():
            st.error("Please provide both Job Description and Resumes.")
        else:
            with st.spinner("Processing NLP Pipeline..."):
                results = []
                for file in uploaded_files:
                    text = extract_text_from_file(file)
                    scores = compute_similarity(job_desc, text)
                    final, breakdown = weighted_score(scores)
                    results.append({
                        "Candidate": file.name, "Total Score": final,
                        "Skills": breakdown["skills"], "Experience": breakdown["experience"],
                        "Education": breakdown["education"], "Feedback": generate_feedback(scores),
                        "Matched": scores["skills_matched"], "Missing": scores["skills_missing"]
                    })
                st.session_state.results = results

    # ================= RESULTS DISPLAY =================
    if "results" in st.session_state and st.session_state.results:
        df = pd.DataFrame(st.session_state.results)
        selected = st.selectbox("Select Candidate to Review", df["Candidate"])
        data = df[df["Candidate"] == selected].iloc[0]

        # Score Visualization
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=data["Total Score"],
                title={'text': "Relevance Score", 'font': {'size': 18}},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#4F46E5"}}
            ))
            fig.update_layout(height=250, margin=dict(t=30, b=0, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            categories = ['Skills', 'Experience', 'Education']
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatterpolar(r=[data['Skills'], data['Experience'], data['Education']], theta=categories, fill='toself'))
            fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=250, margin=dict(t=30, b=30))
            st.plotly_chart(fig_r, use_container_width=True)

        # Skill Gap Analysis
        st.markdown("### Skill Gap Analysis")
        cm, cmiss = st.columns(2)
        with cm:
            st.markdown("**Matched**")
            for s in data["Matched"]: st.success(s)
        with cmiss:
            st.markdown("**Missing**")
            for s in data["Missing"]: st.error(s)
            
        st.table(df[["Candidate", "Total Score", "Skills", "Experience", "Education"]])