import re
from modules.skills import SKILL_KEYWORDS


# ================= CLEAN TEXT =================
def clean_tokens(tokens):
    stop_words = set([
        "the", "and", "a", "to", "of", "in", "for", "on", "with",
        "at", "by", "an", "be", "is", "are", "as", "from", "or"
    ])

    clean = [
        t.lower() for t in tokens
        if t.lower() not in stop_words and len(t) > 2 and t.isalpha()
    ]

    return list(set(clean))


# ================= SKILL EXTRACTION =================
def extract_skills(text):
    text = text.lower()
    return set([skill for skill in SKILL_KEYWORDS if skill in text])


# ================= GENERATE FEEDBACK =================
def generate_feedback(scores):

    skill_score = scores.get("skills", 0)
    exp_score = scores.get("experience", 0)
    edu_score = scores.get("education", 0)

    feedback = []

    # Skills
    if skill_score >= 70:
        feedback.append("Strong alignment with required skills.")
    elif skill_score >= 40:
        feedback.append("Partial skill match. Consider adding more relevant tools or technologies.")
    else:
        feedback.append("Low skill match. Key skills from the job description are missing.")

    # Experience
    if exp_score >= 70:
        feedback.append("Your experience is highly relevant to the job.")
    elif exp_score >= 40:
        feedback.append("Your experience is somewhat relevant but could be clearer.")
    else:
        feedback.append("Your experience does not strongly match the role.")

    # Education
    if edu_score >= 70:
        feedback.append("Your education aligns well with the job.")
    elif edu_score >= 40:
        feedback.append("Your education is somewhat relevant.")
    else:
        feedback.append("Your education does not clearly support this role.")

    return " ".join(feedback)


# ================= ATS FEEDBACK =================
def ats_feedback(resume_text, job_desc):

    # ===== SKILL-BASED MATCHING (MAIN) =====
    jd_skills = extract_skills(job_desc)
    res_skills = extract_skills(resume_text)

    matched = list(jd_skills & res_skills)
    missing = list(jd_skills - res_skills)

    # ===== FALLBACK (if no skills detected) =====
    if len(jd_skills) == 0:
        resume_tokens = re.findall(r"\b\w+\b", resume_text.lower())
        job_tokens = re.findall(r"\b\w+\b", job_desc.lower())

        resume_clean = clean_tokens(resume_tokens)
        job_clean = clean_tokens(job_tokens)

        resume_set = set(resume_clean)
        job_set = set(job_clean)

        matched = list(resume_set & job_set)[:10]
        missing = list(job_set - resume_set)[:10]

        if len(job_set) == 0:
            score = 0
        else:
            score = (len(matched) / len(job_set)) * 100

    else:
        if len(jd_skills) == 0:
            score = 0
        else:
            score = (len(matched) / len(jd_skills)) * 100

    # ===== MESSAGE =====
    if score >= 70:
        message = "High alignment with job requirements."
    elif score >= 40:
        message = "Moderate alignment. Some improvements needed."
    else:
        message = "Low alignment. Resume needs better tailoring."

    return {
        "score": round(score, 2),
        "message": message,
        "matched": matched[:10],
        "missing": missing[:10]
    }