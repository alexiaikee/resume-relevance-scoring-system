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

# ================= CUSTOM CSS (Shading, Depth & Alert Button) =================
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; }

    .title-container {
        background-color: #1E293B;
        padding: 40px 50px;
        border-radius: 12px;
        margin-bottom: 30px;
        border-left: 6px solid #6366F1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .input-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 20px;
    }

    /* ALERT BUTTON CSS */
    div.stButton > button:first-child {
        background-color: #4F46E5 !important; /* Premium Indigo */
        color: white !important;
        border: none !important;
        padding: 15px 30px !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.39) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100%;
    }

    div.stButton > button:first-child:hover {
        background-color: #059669 !important; /* Success Green on Hover */
        transform: scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(5, 150, 105, 0.23) !important;
    }

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

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("<h2 style='color:#1E293B; font-size:22px; font-weight:800;'>UNIMAS FYP</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6366F1; font-size:12px; font-weight:600; margin-top:-15px;'>NLP RELEVANCE ENGINE</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    page = st.radio("WORKFLOW", ["Evaluation Workspace", "Analysis Insights"])
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:10px; color:#94A3B8; font-weight:800; letter-spacing:0.1em;'>SYSTEM STATE</p>", unsafe_allow_html=True)
    
    stats = {"CORE": "Python 3.14", "ENGINE": "TF-IDF", "METRIC": "Cosine", "LIB": "NLTK v3.8"}
    for label, val in stats.items():
        st.markdown(f"<div class='status-item'>{label} <span class='status-value'>{val}</span></div>", unsafe_allow_html=True)
    st.success("SYSTEM READY")

# ================= WORKFLOW: EVALUATION WORKSPACE =================
if page == "Evaluation Workspace":
    st.markdown("""
        <div class="title-container">
            <h1 style="color:#FFFFFF; font-size:30px; font-weight:800; margin:0;">Resume Relevance Scoring System</h1>
            <p style="color:#94A3B8; font-size:15px; margin-top:5px; font-weight:500;">
                Advanced NLP Prototype for Recruitment Evaluation
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col_jd, col_res = st.columns(2, gap="large")
    
    with col_jd:
        st.markdown("<div class='input-card'>", unsafe_allow_html=True)
        st.markdown("<div class='label-shade'>JOB DESCRIPTION INPUT</div>", unsafe_allow_html=True)
        job_desc = st.text_area("JD_Input", height=300, label_visibility="collapsed", placeholder="Paste requirements here...")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_res:
        st.markdown("<div class='input-card'>", unsafe_allow_html=True)
        st.markdown("<div class='label-shade'>CANDIDATE DOCUMENT</div>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Upload", type=["pdf", "docx"], accept_multiple_files=True, label_visibility="collapsed")
        st.info("System optimized for PDF and DOCX formats.")
        st.markdown("</div>", unsafe_allow_html=True)

    # RUN ANALYSIS BUTTON SECTION
    st.markdown("<br>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1.5, 1, 1.5])
    with center_col:
        if st.button("RUN AI ANALYSIS"):
            if not uploaded_files or not job_desc.strip():
                st.error("Protocol Error: Provide input data.")
            else:
                with st.spinner("Analyzing..."):
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
                    st.success("Analysis Complete! Head to 'Analysis Insights' in the sidebar.")

# ================= WORKFLOW: ANALYSIS INSIGHTS =================
elif page == "Analysis Insights":
    if "results" not in st.session_state or not st.session_state.results:
        st.warning("⚠️ No data analyzed yet. Please go to 'Evaluation Workspace' and click 'Run AI Analysis' first.")
    else:
        st.markdown("## Analysis Insights")
        df = pd.DataFrame(st.session_state.results)
        selected = st.selectbox("Select Candidate", df["Candidate"])
        data = df[df["Candidate"] == selected].iloc[0]

        # Charts Section
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='input-card'>", unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(mode="gauge+number", value=data["Total Score"], number={'suffix': "%"}, gauge={'bar': {'color': "#6366F1"}}))
            fig.update_layout(height=250, margin=dict(t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='input-card'>", unsafe_allow_html=True)
            fig_r = go.Figure(go.Scatterpolar(r=[data['Skills'], data['Experience'], data['Education']], theta=['Skills', 'Experience', 'Education'], fill='toself'))
            fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=250, margin=dict(t=30, b=30))
            st.plotly_chart(fig_r, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Skill Gaps
        st.markdown("<div class='input-card'>", unsafe_allow_html=True)
        st.markdown("### Skill Gap Analysis")
        cm, cmiss = st.columns(2)
        with cm:
            st.success("**Matched Skills**")
            for s in data["Matched"]: st.write(f"✅ {s}")
        with cmiss:
            st.error("**Missing Skills**")
            for s in data["Missing"]: st.write(f"❌ {s}")
        st.markdown("</div>", unsafe_allow_html=True)