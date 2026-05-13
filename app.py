import streamlit as st
import pandas as pd
import os

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

# ================= UI STYLE =================
st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }

.stApp {
    background-color: #F8FAFC;
    font-family: 'Segoe UI', sans-serif;
}

[data-testid="stSidebar"] {
    background-color: #EEF2FF;
}

.header {
    background: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    margin-bottom: 25px;
}

.card {
    background: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

.stButton > button {
    background: linear-gradient(90deg, #4F46E5, #6366F1);
    color: white;
    border-radius: 10px;
    padding: 12px;
    font-weight: 600;
    border: none;
}

.score-good { color:#16A34A; font-size:42px; font-weight:700; }
.score-mid { color:#F59E0B; font-size:42px; font-weight:700; }
.score-bad { color:#DC2626; font-size:42px; font-weight:700; }

.tag {
    display:inline-block;
    padding:6px 10px;
    margin:4px;
    border-radius:8px;
    font-size:13px;
}

.tag-good { background:#DCFCE7; color:#166534; }
.tag-miss { background:#FEE2E2; color:#991B1B; }
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("<div class='header'>", unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 5])

with col1:
    if os.path.exists(logo_path):
        st.image(logo_path, width=160)

with col2:
    st.markdown("""
    <div style="padding-top:15px;">
        <div style="font-size:34px; font-weight:700; color:#1E3A8A;">
            Resume Relevance Scoring System
        </div>
        <div style="color:#64748B; font-size:16px;">
            NLP-based evaluation using TF-IDF and cosine similarity
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ================= SESSION =================
MAX_RESUMES = 3

if "results" not in st.session_state:
    st.session_state.results = []

# ================= NAV =================
page = st.sidebar.radio("Navigation", ["Upload & Analyze", "Dashboard"])

# ================= UPLOAD =================
if page == "Upload & Analyze":

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.subheader("Upload Resumes and Job Description")
    st.info("Upload up to 3 resumes for comparison.")

    job_desc = st.text_area("Job Description", height=220)

    uploaded_files = st.file_uploader(
        "Upload Resume Files",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if uploaded_files and len(uploaded_files) > MAX_RESUMES:
        st.error("Maximum 3 resumes allowed.")
        st.stop()

    if st.button("Run Analysis"):

        if not uploaded_files or not job_desc.strip():
            st.warning("Please provide resumes and job description.")
        else:
            results = []

            with st.spinner("Analyzing..."):

                for file in uploaded_files:

                    resume_text = extract_text_from_file(file)
                    scores = compute_similarity(job_desc, resume_text)

                    final_score, breakdown = weighted_score(scores)
                    feedback = generate_feedback(scores)

                    # ✅ USE REAL ATS OUTPUT
                    ats = ats_feedback(resume_text, job_desc)

                    results.append({
                        "Candidate": file.name,
                        "Total Score": final_score,
                        "Skills": round(breakdown["skills"], 2),
                        "Experience": round(breakdown["experience"], 2),
                        "Education": round(breakdown["education"], 2),
                        "Feedback": feedback,
                        "ATS Score": ats["score"],
                        "ATS Message": ats["message"],
                        "Matched": ats["matched"],
                        "Missing": ats["missing"]
                    })

            st.session_state.results = results
            st.success("Analysis completed.")

    st.markdown("</div>", unsafe_allow_html=True)

# ================= DASHBOARD =================
elif page == "Dashboard":

    if not st.session_state.results:
        st.info("No results yet.")
    else:

        df = pd.DataFrame(st.session_state.results)
        best = df.sort_values(by="Total Score", ascending=False).iloc[0]

        st.success(f"Best Resume: {best['Candidate']} ({best['Total Score']}%)")

        selected = st.selectbox("Select Resume", df["Candidate"])

        data = df[df["Candidate"] == selected].iloc[0]

        score = data["Total Score"]
        cls = "score-good" if score >= 75 else "score-mid" if score >= 50 else "score-bad"

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        st.markdown("### Overall Score")
        st.markdown(f"<div class='{cls}'>{score}%</div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        col1.metric("Skills", f"{data['Skills']}%")
        col2.metric("Experience", f"{data['Experience']}%")
        col3.metric("Education", f"{data['Education']}%")

        st.markdown("### Feedback")
        st.info(data["Feedback"])

        # ✅ CLEAN ATS DISPLAY
        st.markdown("### ATS Analysis")
        st.metric("ATS Score", f"{data['ATS Score']}%")
        st.caption(data["ATS Message"])

        # ✅ SKILLS TAGS (REAL)
        st.markdown("### Matched Skills")
        for skill in data["Matched"]:
            st.markdown(f"<span class='tag tag-good'>{skill}</span>", unsafe_allow_html=True)

        st.markdown("### Missing Skills")
        for skill in data["Missing"]:
            st.markdown(f"<span class='tag tag-miss'>{skill}</span>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # TABLE
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Comparison Table")

        st.dataframe(
            df.drop(columns=["Feedback", "Matched", "Missing", "ATS Message"])
            .sort_values(by="Total Score", ascending=False),
            use_container_width=True
        )

        st.markdown("</div>", unsafe_allow_html=True)