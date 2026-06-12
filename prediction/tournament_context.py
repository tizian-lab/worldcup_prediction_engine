def get_tournament_context(match):
    league = match.get("league", {})
    round_name = league.get("round", "")

    round_lower = round_name.lower()

    context = {
        "round_name": round_name,
        "goal_multiplier": 1.0,
        "draw_boost": 0.0,
        "description": "Normale Turnierbedingungen.",
    }

    if "group stage - 1" in round_lower:
        context["description"] = "Gruppenspiel 1: Auftaktspiel, normales Risikoprofil."

    elif "group stage - 2" in round_lower:
        context["goal_multiplier"] = 1.02
        context["description"] = "Gruppenspiel 2: erste Tabellenlage beeinflusst das Risiko leicht."

    elif "group stage - 3" in round_lower:
        context["goal_multiplier"] = 0.96
        context["draw_boost"] = 0.025
        context["description"] = "Gruppenspiel 3: oft vorsichtiger, Remis kann wertvoller sein."

    elif "group" in round_lower:
        context["description"] = "Gruppenphase: normales Risikoprofil."

    elif "round of 32" in round_lower:
        context["goal_multiplier"] = 0.94
        context["draw_boost"] = 0.03
        context["description"] = "K.o.-Phase: etwas vorsichtigeres Spiel."

    elif "round of 16" in round_lower:
        context["goal_multiplier"] = 0.92
        context["draw_boost"] = 0.035
        context["description"] = "Achtelfinale: tendenziell vorsichtiger."

    elif "quarter" in round_lower:
        context["goal_multiplier"] = 0.90
        context["draw_boost"] = 0.04
        context["description"] = "Viertelfinale: weniger Risiko, knappere Spiele."

    elif "semi" in round_lower:
        context["goal_multiplier"] = 0.88
        context["draw_boost"] = 0.045
        context["description"] = "Halbfinale: sehr vorsichtiges Risikoprofil."

    elif "final" in round_lower:
        context["goal_multiplier"] = 0.86
        context["draw_boost"] = 0.05
        context["description"] = "Finale: häufig enger und torärmer."

    return context