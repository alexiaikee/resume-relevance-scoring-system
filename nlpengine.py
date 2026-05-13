from preprocessing import preprocess_text


def extract_skills(text):
    text = text.lower()
    return set([skill for skill in SKILL_KEYWORDS if skill in text])


def compute_similarity(job_desc, resume_text):

    jd_skills = extract_skills(job_desc)
    res_skills = extract_skills(resume_text)

    matched = jd_skills & res_skills
    missing = jd_skills - res_skills

    # Skill score
    if len(jd_skills) == 0:
        skill_score = 0
    else:
        skill_score = (len(matched) / len(jd_skills)) * 100

    # Experience (simple logic)
    if "experience" in resume_text.lower():
        experience_score = 100
    else:
        experience_score = 40

    # Education (simple logic)
    if "degree" in resume_text.lower() or "bachelor" in resume_text.lower():
        education_score = 100
    else:
        education_score = 50

    return {
        "skills": round(skill_score, 2),
        "experience": experience_score,
        "education": education_score,
        "skills_matched": list(matched),
        "skills_missing": list(missing)
    }