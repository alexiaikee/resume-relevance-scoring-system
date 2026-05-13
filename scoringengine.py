def weighted_score(scores):
    # Weights based on your scoring logic
    skill_weight = 0.50
    exp_weight = 0.30
    edu_weight = 0.20

    # We use the Skill score (which is more specific) for the main weight
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