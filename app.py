import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

from fileparser import extract_text_from_file
from nlpengine import compute_similarity
from scoringengine import weighted_score
from feedbackengine import generate_feedback, ats_feedback

# ================= PAGE CONFIG =================
st.set_page_config(page_title="UNIMAS FYP - NLP Scoring", layout="wide")

# ================= UI STYLE (The "AI Studio" Look) =================
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    
    /* Sidebar Styling - Dark Professional */
    [data-testid="stSidebar"] {
        background-color: #111827;
        color: #FFFFFF;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }

    /* Custom Card Design */
    .card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        margin-bottom: 15px;
    }
    
    /* System State Sidebar items */
    .system-status {
        padding: 10px;
        border-radius: 8px;
        background: #1F2937;
        border-left: 4px solid #4F46E5;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.image("assets/logo.png", width=120) if os.path.exists("assets/logo.png") else st.title("UNIMAS FYP")
    st.markdown("### SYSTEM STATE")
    st.markdown("<div class='system-status'>🟢 CORE ENGINE: Python 3.14</div>", unsafe_allow_html=True)
    st.markdown("<div class='system-status'>🔵 VECTORIZER: TF-IDF ACTIVE</div>", unsafe_allow_html=True)
    st.markdown("<div class='system-status'>🟣 METRIC: COSINE SIMILARITY</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    page = st.radio("NAVIGATION", ["Upload & Analyze", "Dashboard"])
    st.markdown("---")
    st.caption("Developed by Alexia Ijau Kee")
    st.success("SYSTEM READY")

# ================= MAIN CONTENT =================
if page == "Upload & Analyze":
    st.title("Resume Relevance Scoring System")
    st.caption("NLP-Based Recruitment Evaluation Prototype")

    # TWO-COLUMN INPUT (Removes the "Ugly Gaps")
    col_jd, col_file = st.columns([1, 1], gap="medium")

    with col_jd:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📝 Job Description")
        job_desc = st.text_area("Paste Requirements Here", height=250, placeholder="Enter the JD text...")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_file:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📂 Resume Dropzone")
        uploaded_files = st.file_uploader("Upload PDF or DOCX (Max 3)", type=["pdf", "docx"], accept_multiple_files=True)
        st.info("Supported formats: .pdf, .docx")
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("RUN AI ANALYSIS", use_container_width=True):
        if not uploaded_files or not job_desc.strip():
            st.error("Missing Input: Please provide both JD and Resumes.")
        else:
            with st.spinner("Applying NLP Pipeline..."):
                results = []
                for file in uploaded_files:
                    text = extract_text_from_file(file)
                    scores = compute_similarity(job_desc, text)
                    final, breakdown = weighted_score(scores)
                    ats = ats_feedback(text, job_desc)
                    results.append({
                        "Candidate": file.name, "Total Score": final,
                        "Skills": breakdown["skills"], "Experience": breakdown["experience"],
                        "Education": breakdown["education"], "Feedback": generate_feedback(scores),
                        "ATS Score": ats["score"], "ATS Message": ats["message"],
                        "Matched": scores["skills_matched"], "Missing": scores["skills_missing"]
                    })
                st.session_state.results = results
                st.balloons()
                st.success("Analysis Complete! Switch to Dashboard.")

# ================= DASHBOARD =================
elif page == "Dashboard":
    if not st.session_state.get("results"):
        st.warning("No data found. Please run the analysis first.")
    else:
        df = pd.DataFrame(st.session_state.results)
        selected = st.selectbox("REVIEW CANDIDATE", df["Candidate"])
        data = df[df["Candidate"] == selected].iloc[0]

        # TOP ROW: Visual Insights
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            # GAUGE CHART
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=data["Total Score"],
                title={'text': "Relevance Score", 'font': {'size': 20}},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#4F46E5"}}
            ))
            fig.update_layout(height=280, margin=dict(t=30, b=0, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            # RADAR CHART
            categories = ['Skills', 'Experience', 'Education']
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatterpolar(r=[data['Skills'], data['Experience'], data['Education']], theta=categories, fill='toself'))
            fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=280, margin=dict(t=30, b=30))
            st.plotly_chart(fig_r, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # BOTTOM ROW: Skill Gaps
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Skill Gap Analysis")
        col_m, col_ms = st.columns(2)
        with col_m:
            st.write("✅ **MATCHED**")
            for s in data["Matched"]: st.info(s) if s else st.write("None")
        with col_ms:
            st.write("❌ **MISSING**")
            for s in data["Missing"]: st.error(s) if s else st.write("None")
        st.markdown("</div>", unsafe_allow_html=True)