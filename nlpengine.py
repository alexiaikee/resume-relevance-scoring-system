from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from preprocessing import preprocess_text
from skills import SKILL_KEYWORDS

# Add this back in case app.py or feedbackengine.py calls it separately
def extract_skills(text):
    if not text:
        return set()
    text = text.lower()
    return set([skill for skill in SKILL_KEYWORDS if skill in text])

def compute_similarity(job_desc, resume_text):
    # 1. Preprocess both texts
    clean_jd = preprocess_text(job_desc)
    clean_resume = preprocess_text(resume_text)
    
    # 2. TF-IDF & Cosine Similarity
    # Safety check: if either text is empty after preprocessing, similarity is 0
    if not clean_jd.strip() or not clean_resume.strip():
        overall_similarity = 0
    else:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([clean_jd, clean_resume])
        overall_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    # 3. Skill-Specific Matching
    jd_skills = extract_skills(clean_jd)
    res_skills = extract_skills(clean_resume)
    
    matched = jd_skills & res_skills
    missing = jd_skills - res_skills
    
    skill_score = (len(matched) / len(jd_skills)) * 100 if jd_skills else 0
    
    # 4. Experience & Education (Keyword detection)
    # Using lowercase check for better reliability
    res_lower = clean_resume.lower()
    exp_score = 100 if "experience" in res_lower or "work" in res_lower else 40
    edu_score = 100 if any(x in res_lower for x in ["degree", "bachelor", "university", "unimas"]) else 50

    return {
        "overall_cosine": round(overall_similarity * 100, 2),
        "skills": round(skill_score, 2),
        "experience": exp_score,
        "education": edu_score,
        "skills_matched": list(matched),
        "skills_missing": list(missing)
    }