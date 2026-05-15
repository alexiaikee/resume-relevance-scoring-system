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

# ================= CUSTOM CSS (Enhanced AI Studio Aesthetic) =================
st.markdown("""
<style>
    /* Main Background & Font */
    .stApp { background-color: #F8FAFC; font-family: 'Inter', 'Segoe UI', sans-serif; }
    
    /* Sidebar Styling - Professional Dark/Light contrast */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Shaded Header Section */
    .main-header {
        background-color: #FFFFFF;
        padding: 40px 60px;
        border-bottom: 1px solid #E2E8F0;
        margin: -6rem -5rem 2rem -5rem;
    }

    /* Input Card Styling with soft shading */
    .input-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        min-height: 450px;
    }

    /* Label Shading */
    .label-box {
        background-color: #F1F5F9;
        padding: 8px 16px;
        border-radius: 8px;
        display: inline-block;
        margin-bottom: 15px;
        color: #475569;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.05em;
    }

    /* System Status Badges */
    .status-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        font-size: 13px;
        color: #64748B;
        border-bottom: 1px solid #F1F5F9;
    }
    .status-value { color: #6366F1; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
    
    /* Ghost Button Style */
    .stButton > button {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        padding: 15px 30px !important;
        font-weight: 600 !important;
        width: 100%;
        border: none !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        background-color: #0F172A !important;
    }

</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR (System State) =================
with st.sidebar:
    st.markdown("<h2 style='color:#1E293B; font-size:22px; font-weight:800;'>UNIMAS FYP</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6366F1; font-size:12px; font-weight:600; margin-top:-15px;'>NLP RELEVANCE ENGINE</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    page = st.radio("NAVIGATION", ["DASHBOARD", "RESUME POOL", "DOCUMENTATION"])
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:11px; color:#94A3B8; font-weight:800; letter-spacing:0.1em;'>SYSTEM STATE</p>", unsafe_allow_html=True)
    
    stats = {
        "CORE ENGINE": "Python 3.14",
        "VECTORIZATION": "TF-IDF Active",
        "SIMILARITY": "Cosine-Dist",
        "NLP PIPELINE": "Lemmatization"
    }
    for label, val in stats.items():
        st.markdown(f"<div class='status-item'>{label} <span class='status-value'>{val}</span></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.success("PROTOCOL READY")

# ================= MAIN CONTENT =================
if page == "DASHBOARD":
    # Shaded Header Section
    st.markdown(f"""
        <div class="main-header">
            <h1 style="color:#0F172A; font-size:36px; font-weight:800; margin:0;">Resume Relevance Scoring System</h1>
            <p style="color:#64748B; font-size:16px; margin-top:5px;">AI-driven recruitment evaluation using TF-IDF and Cosine Similarity.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 2-Column Layout with Shaded Cards
    col_jd, col_res = st.columns(2, gap="large")
    
    with col_jd:
        st.markdown("<div class='input-card'>", unsafe_allow_html=True)
        st.markdown("<div class='label-box'>REQUIRED JOB DESCRIPTION</div>", unsafe_allow_html=True)
        job_desc = st.text_area("JD_Input", height=320, label_visibility="collapsed", placeholder="Paste the official Job Description here...")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_res:
        st.markdown("<div class='input-card'>", unsafe_allow_html=True)
        st.markdown("<div class='label-box'>CANDIDATE RESUME DOCUMENT</div>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Resume_Upload", type=["pdf", "docx"], accept_multiple_files=True, label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("System accepts PDF or DOCX formats. Maximum 3 files for batch analysis.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Centered Run Analysis Button
    st.markdown("<br>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1.5, 1, 1.5])
    with center_col:
        run_analysis = st.button("EXECUTE ANALYSIS")

    # ================= ANALYSIS LOGIC =================
    if run_analysis:
        if not uploaded_files or not job_desc.strip():
            st.error("Protocol Error: Please provide both Job Description and Candidate Resumes.")
        else:
            with st.spinner("Initializing NLP Pipeline..."):
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

    # ================= RESULTS DISPLAY (Only shows if results exist) =================
    if "results" in st.session_state and st.session_state.results:
        st.markdown("---")
        df = pd.DataFrame(st.session_state.results)
        selected = st.selectbox("Select Candidate to Review", df["Candidate"])
        data = df[df["Candidate"] == selected].iloc[0]

        # Professional Visualization Row
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='input-card' style='min-height:300px;'>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=data["Total Score"],
                number={'suffix': "%", 'font': {'color': '#1E293B'}},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#6366F1"}}
            ))
            fig.update_layout(height=250, margin=dict(t=30, b=0, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with c2:
            st.markdown("<div class='input-card' style='min-height:300px;'>", unsafe_allow_html=True)
            categories = ['Skills', 'Experience', 'Education']
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatterpolar(r=[data['Skills'], data['Experience'], data['Education']], theta=categories, fill='toself', fillcolor='rgba(99, 102, 241, 0.3)', line=dict(color='#6366F1')))
            fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=250, margin=dict(t=30, b=30))
            st.plotly_chart(fig_r, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Skill Gap Analysis
        st.markdown("<div class='input-card'>", unsafe_allow_html=True)
        st.markdown("### Skill Gap Analysis")
        cm, cmiss = st.columns(2)
        with cm:
            st.markdown("<p style='color:#16A34A; font-weight:700;'>Matched Competencies</p>", unsafe_allow_html=True)
            for s in data["Matched"]: st.success(s)
        with cmiss:
            st.markdown("<p style='color:#DC2626; font-weight:700;'>Missing Requirements</p>", unsafe_allow_html=True)
            for s in data["Missing"]: st.error(s)
        st.markdown("</div>", unsafe_allow_html=True)