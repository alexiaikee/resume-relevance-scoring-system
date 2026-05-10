def weighted_score(scores):

    skill_weight = 0.5
    exp_weight = 0.3
    edu_weight = 0.2

    final_score = (
        scores["skills"] * skill_weight +
        scores["experience"] * exp_weight +
        scores["education"] * edu_weight
    )

    breakdown = {
        "skills": scores["skills"],
        "experience": scores["experience"],
        "education": scores["education"]
    }

    return round(final_score, 2), breakdown