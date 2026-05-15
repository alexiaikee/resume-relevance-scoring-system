import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

from fileparser import extract_text_from_file
from nlpengine import compute_similarity
from scoringengine import weighted_score
from feedbackengine import generate_feedback, ats_feedback

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Resume Relevance Scoring System",
    layout="wide"
)

# ================= PATH =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(BASE_DIR, "assets", "logo.png")

# ================= UI STYLE (AI Studio Inspired) =================
st.markdown("""
<style>
.block-container { padding-top: 1rem; }
.stApp { background-color: #FBFBFE; font-family: 'Inter', sans-serif; }

/* Sidebar Styling */
[data-testid="stSidebar"] { background-color: #111827; color: white; }
[data-testid="stSidebar"] * { color: white !important; }

/* AI Studio Card Style */
.card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin-bottom: 15px; /* Tightened margin to remove ugly gaps */
}

.stButton > button {
    background: #4F46E5;
    color: white;
    border-radius: 6px;
    padding: 10px;
    border: none;
    transition: 0.3s;
}
.stButton > button:hover { background: #4338CA; }

.tag {
    display:inline-block;
    padding:4px 10px;
    margin:4px;
    border-radius:6px;
    font-size:13px;
    font-weight: 500;
}
.tag-good { background:#DCFCE7; color:#166534; border: 1px solid #BBF7D0; }
.tag-miss { background:#FEE2E2; color:#991B1B; border: 1px solid #FECACA; }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR (Technical Methodology) =================
st.sidebar.title("⚙️ System Control")
page = st.sidebar.radio("Navigation", ["Upload & Analyze", "Dashboard"])

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Technical Methodology")
st.sidebar.caption("FYP Phase: Evaluation Prototype")
st.sidebar.write("**AI Model:** TF-IDF Vectorizer")
st.sidebar.write("**Metric:** Cosine Similarity")
st.sidebar.write("**Language:** Python 3.14")
st.sidebar.write("**NLP Library:** NLTK (Lemmatization)")
st.sidebar.markdown("---")
st.sidebar.info("Developed by Alexia Ijau Kee")

# ================= HEADER =================
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)
with col2:
    st.title("Resume Relevance Scoring System")
    st.caption("Advanced NLP-based Recruitment Evaluation")

# ================= SESSION =================
if "results" not in st.session_state:
    st.session_state.results = []

# ================= UPLOAD PAGE =================
if page == "Upload & Analyze":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Input Data")
    job_desc = st.text_area("Target Job Description", height=200)
    uploaded_files = st.file_uploader("Upload Resumes", type=["pdf", "docx"], accept_multiple_files=True)

    if st.button("Generate AI Insights"):
        if uploaded_files and job_desc.strip():
            with st.spinner("Processing NLP Pipeline..."):
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
                st.success("Analysis complete!")
        else:
            st.warning("Please provide all inputs.")
    st.markdown("</div>", unsafe_allow_html=True)

# ================= DASHBOARD PAGE =================
elif page == "Dashboard":
    if not st.session_state.results:
        st.info("Please upload data first.")
    else:
        df = pd.DataFrame(st.session_state.results)
        selected = st.selectbox("Select Candidate", df["Candidate"])
        data = df[df["Candidate"] == selected].iloc[0]

        # --- ROW 1: Gauge and Radar ---
        col_gauge, col_radar = st.columns([1, 1])

        with col_gauge:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=data["Total Score"],
                title={'text': "Relevance Score"},
                gauge={'axis': {'range': [0, 100]},
                       'bar': {'color': "#4F46E5"},
                       'steps': [{'range': [0, 50], 'color': "#FEE2E2"},
                                 {'range': [50, 75], 'color': "#FEF3C7"},
                                 {'range': [75, 100], 'color': "#DCFCE7"}]}))
            fig_gauge.update_layout(height=300, margin=dict(t=50, b=0, l=20, r=20))
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.caption("Weightage: 50% Skills, 30% Experience, 20% Education")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_radar:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            categories = ['Skills Alignment', 'Experience Relevance', 'Education Fit']
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=[data['Skills'], data['Experience'], data['Education']],
                theta=categories, fill='toself', line_color='#4F46E5'
            ))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                                    showlegend=False, height=300, margin=dict(t=40, b=40, l=40, r=40))
            st.plotly_chart(fig_radar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # --- ROW 2: Skill Gap Analysis ---
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Skill Gap Analysis")
        c1, c2 = st.columns(2)
        with c1:
            st.write("✅ **Matched**")
            if data["Matched"]:
                for s in data["Matched"]: st.markdown(f"<span class='tag tag-good'>{s}</span>", unsafe_allow_html=True)
            else: st.caption("None found")
        with c2:
            st.write("❌ **Missing**")
            if data["Missing"]:
                for s in data["Missing"]: st.markdown(f"<span class='tag tag-miss'>{s}</span>", unsafe_allow_html=True)
            else: st.caption("No gaps detected")
        st.markdown("</div>", unsafe_allow_html=True)

        # --- ROW 3: Feedback ---
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Improvement Suggestions")
        st.info(data["Feedback"])
        st.markdown(f"**ATS Optimization Check:** {data['ATS Score']}% - {data['ATS Message']}")
        st.markdown("</div>", unsafe_allow_html=True)

        # --- ROW 4: Comparison Table ---
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.dataframe(df.drop(columns=["Feedback", "Matched", "Missing", "ATS Message"]), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)