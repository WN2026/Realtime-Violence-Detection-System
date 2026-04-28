def classify_violence(score, weapon_type):

    if score <= 0.5:
        return "NON VIOLENCE"

    if weapon_type in ["gun", "knife"]:
        return "HIGH"

    if score <= 0.65:
        return "LOW"
    elif score <= 0.85:
        return "MEDIUM"
    else:
        return "HIGH"
        