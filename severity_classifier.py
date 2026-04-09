def classify_violence(score, weapon_type):

    if weapon_type in ["gun", "knife"]:
        return "HIGH"

    if score <= 0.25:
        return "NON VIOLENCE"
    elif score <= 0.5:
        return "LOW"
    elif score <= 0.75:
        return "MEDIUM"
    else:
        return "HIGH"