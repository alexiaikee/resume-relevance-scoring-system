from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from preprocessing import preprocess_text
from skills import SKILL_KEYWORDS

def compute_similarity(job_desc, resume_text):
    # 1. Preprocess both texts
    clean_jd = preprocess_text(job_desc)
    clean_resume = preprocess_text(resume_text)
    
    # 2. TF-IDF & Cosine Similarity (General Content Match)
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([clean_jd, clean_resume])
    overall_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    # 3. Skill-Specific Matching
    jd_skills = set([s for s in SKILL_KEYWORDS if s in clean_jd])
    res_skills = set([s for s in SKILL_KEYWORDS if s in clean_resume])
    
    matched = jd_skills & res_skills
    missing = jd_skills - res_skills
    
    skill_score = (len(matched) / len(jd_skills)) * 100 if jd_skills else 0
    
    # 4. Experience & Education (Keyword detection)
    exp_score = 100 if "experience" in clean_resume or "work" in clean_resume else 40
    edu_score = 100 if any(x in clean_resume for x in ["degree", "bachelor", "university", "unimas"]) else 50

    return {
        "overall_cosine": round(overall_similarity * 100, 2),
        "skills": round(skill_score, 2),
        "experience": exp_score,
        "education": edu_score,
        "skills_matched": list(matched),
        "skills_missing": list(missing)
    }