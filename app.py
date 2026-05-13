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
    width: 100%;
}

.score-good { color:#16A34A; font-size:48px; font-weight:700; }
.score-mid { color:#F59E0B; font-size:48px; font-weight:700; }
.score-bad { color:#DC2626; font-size:48px; font-weight:700; }

.tag {
    display:inline-block;
    padding:6px 12px;
    margin:4px;
    border-radius:8px;
    font-size:14px;
    font-weight: 500;
}

.tag-good { background:#DCFCE7; color:#166534; border: 1px solid #BBF7D0; }
.tag-miss { background:#FEE2E2; color:#991B1B; border: 1px solid #FECACA; }
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
            AI-based evaluation using TF-IDF and Cosine Similarity
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

# ================= UPLOAD PAGE =================
if page == "Upload & Analyze":

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.subheader("Upload Resumes and Job Description")
    st.info("Upload up to 3 resumes to compare against the target job requirements.")

    job_desc = st.text_area("Target Job Description", height=220, placeholder="Paste the job responsibilities and requirements here...")

    uploaded_files = st.file_uploader(
        "Upload Resume Files (PDF/DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if uploaded_files and len(uploaded_files) > MAX_RESUMES:
        st.error(f"Maximum {MAX_RESUMES} resumes allowed.")
        st.stop()

    if st.button("Run AI Analysis"):
        if not uploaded_files or not job_desc.strip():
            st.warning("Please provide at least one resume and a job description.")
        else:
            results = []

            # ADDED: Improved spinner text for academic professionalism
            with st.spinner("Applying NLP Pipeline: Preprocessing, TF-IDF Vectorization, and Cosine Similarity..."):

                for file in uploaded_files:
                    # 1. Extraction
                    resume_text = extract_text_from_file(file)
                    
                    # 2. NLP Engine (using updated Cosine Similarity)
                    scores = compute_similarity(job_desc, resume_text)

                    # 3. Scoring & Feedback
                    final_score, breakdown = weighted_score(scores)
                    feedback = generate_feedback(scores)
                    ats = ats_feedback(resume_text, job_desc)

                    results.append({
                        "Candidate": file.name,
                        "Total Score": final_score,
                        "Skills": breakdown["skills"],
                        "Experience": breakdown["experience"],
                        "Education": breakdown["education"],
                        "Feedback": feedback,
                        "ATS Score": ats["score"],
                        "ATS Message": ats["message"],
                        "Matched": scores["skills_matched"], # Uses actual matched list from nlpengine
                        "Missing": scores["skills_missing"]  # Uses actual missing list from nlpengine
                    })

            st.session_state.results = results
            st.success("Analysis completed! Head to the Dashboard to see results.")

    st.markdown("</div>", unsafe_allow_html=True)

# ================= DASHBOARD PAGE =================
elif page == "Dashboard":

    if not st.session_state.results:
        st.info("No results yet. Please upload and analyze resumes first.")
    else:
        df = pd.DataFrame(st.session_state.results)
        
        # Highlight best match
        best = df.sort_values(by="Total Score", ascending=False).iloc[0]
        st.success(f"🏆 **Best Match Found:** {best['Candidate']} with a score of {best['Total Score']}%")

        # Select individual resume to view
        selected = st.selectbox("Select Candidate to Review", df["Candidate"])
        data = df[df["Candidate"] == selected].iloc[0]

        # Overall Score Card
        score = data["Total Score"]
        cls = "score-good" if score >= 75 else "score-mid" if score >= 50 else "score-bad"

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Relevance Score")
        st.markdown(f"<div class='{cls}'>{score}%</div>", unsafe_allow_html=True)
        
        # ADDED: Transparency note for FYP requirements
        st.caption("Weightage: 50% Skills Match, 30% Experience Match, 20% Education Match.")

        col1, col2, col3 = st.columns(3)
        col1.metric("Skills Alignment", f"{data['Skills']}%")
        col2.metric("Experience Relevance", f"{data['Experience']}%")
        col3.metric("Education Fit", f"{data['Education']}%")
        st.markdown("</div>", unsafe_allow_html=True)

        # ADDED: Side-by-Side Skill Gap Analysis (UX Improvement)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Skill Gap Analysis")
        
        col_match, col_miss = st.columns(2)
        
        with col_match:
            st.markdown("**✅ Matched Skills**")
            if data["Matched"]:
                for skill in data["Matched"]:
                    st.markdown(f"<span class='tag tag-good'>{skill}</span>", unsafe_allow_html=True)
            else:
                st.write("No direct skill matches found.")

        with col_miss:
            st.markdown("**❌ Missing Skills / Areas for Improvement**")
            if data["Missing"]:
                for skill in data["Missing"]:
                    st.markdown(f"<span class='tag tag-miss'>{skill}</span>", unsafe_allow_html=True)
            else:
                st.write("No missing skills identified.")
        st.markdown("</div>", unsafe_allow_html=True)

        # Professional Feedback
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Improvement Suggestions")
        st.info(data["Feedback"])
        
        # ATS Deep Dive
        st.markdown("#### ATS Optimization Check")
        st.write(f"**Score:** {data['ATS Score']}%")
        st.write(data['ATS Message'])
        st.markdown("</div>", unsafe_allow_html=True)

        # Comparison Table
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("All Candidates Comparison")
        summary_df = df.drop(columns=["Feedback", "Matched", "Missing", "ATS Message"])
        st.dataframe(
            summary_df.sort_values(by="Total Score", ascending=False),
            use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)