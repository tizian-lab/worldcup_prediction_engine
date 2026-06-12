import math

from data.api_client import get_fixture_odds
from prediction.odds import (
    extract_match_winner_odds,
    blend_probabilities,
)
from prediction.team_ratings import TEAM_ELO_RATINGS, DEFAULT_ELO
from prediction.team_stats import TEAM_STATS
from prediction.tournament_context import get_tournament_context


DEFAULT_ATTACK = 1.0
DEFAULT_DEFENSE = 1.0

HOST_TEAMS = {
    "Mexico": 40,
    "USA": 40,
    "Canada": 40,
}


def get_team_elo(team_name):
    return TEAM_ELO_RATINGS.get(team_name, DEFAULT_ELO)


def get_team_stats(team_name):
    return TEAM_STATS.get(
        team_name,
        {
            "attack": DEFAULT_ATTACK,
            "defense": DEFAULT_DEFENSE,
        },
    )


def get_host_bonus(team_name):
    return HOST_TEAMS.get(team_name, 0)


def calculate_expected_score(home_elo, away_elo):
    elo_difference = home_elo - away_elo
    return 1 / (1 + 10 ** (-elo_difference / 400))


def poisson_probability(goals, expected_goals):
    return (
        math.exp(-expected_goals)
        * (expected_goals ** goals)
        / math.factorial(goals)
    )


def calculate_expected_goals(home_elo, away_elo, home_team, away_team):
    elo_difference = home_elo - away_elo

    home_stats = get_team_stats(home_team)
    away_stats = get_team_stats(away_team)

    home_attack = home_stats["attack"]
    home_defense = home_stats["defense"]

    away_attack = away_stats["attack"]
    away_defense = away_stats["defense"]

    base_goals = 1.35

    home_team_factor = (
        0.55 * home_attack
        + 0.45 * away_defense
    )

    away_team_factor = (
        0.55 * away_attack
        + 0.45 * home_defense
    )

    home_elo_factor = 1 + elo_difference / 800
    away_elo_factor = 1 - elo_difference / 800

    home_expected_goals = (
        base_goals
        * home_team_factor
        * home_elo_factor
    )

    away_expected_goals = (
        base_goals
        * away_team_factor
        * away_elo_factor
    )

    home_expected_goals = max(0.95, min(home_expected_goals, 4.0))
    away_expected_goals = max(0.95, min(away_expected_goals, 4.0))

    return home_expected_goals, away_expected_goals


def find_most_likely_score(
    home_expected_goals,
    away_expected_goals,
    preferred_outcome=None,
):
    best_probability = 0
    best_score = "1:1"

    for home_goals in range(6):
        for away_goals in range(6):
            if preferred_outcome == "home" and home_goals <= away_goals:
                continue

            if preferred_outcome == "draw" and home_goals != away_goals:
                continue

            if preferred_outcome == "away" and away_goals <= home_goals:
                continue

            probability = (
                poisson_probability(home_goals, home_expected_goals)
                * poisson_probability(away_goals, away_expected_goals)
            )

            if home_goals == 0 and away_goals == 0:
                probability *= 0.75

            if probability > best_probability:
                best_probability = probability
                best_score = f"{home_goals}:{away_goals}"

    return best_score, round(best_probability * 100, 2)


def generate_prediction(match):
    teams = match.get("teams", {})

    home_team = teams.get("home", {}).get("name", "Heimteam")
    away_team = teams.get("away", {}).get("name", "Auswärtsteam")

    home_host_bonus = get_host_bonus(home_team)
    away_host_bonus = get_host_bonus(away_team)

    home_elo = get_team_elo(home_team) + home_host_bonus
    away_elo = get_team_elo(away_team) + away_host_bonus
    elo_difference = home_elo - away_elo

    tournament_context = get_tournament_context(match)

    home_expected_goals, away_expected_goals = calculate_expected_goals(
        home_elo,
        away_elo,
        home_team,
        away_team,
    )

    home_expected_goals *= tournament_context["goal_multiplier"]
    away_expected_goals *= tournament_context["goal_multiplier"]

    home_win_probability_raw = calculate_expected_score(home_elo, away_elo)

    draw_probability = max(
        0.15,
        0.28
        - abs(elo_difference) / 1000
        + tournament_context["draw_boost"],
    )

    remaining_probability = 1 - draw_probability

    home_win_probability = home_win_probability_raw * remaining_probability
    away_win_probability = (1 - home_win_probability_raw) * remaining_probability

    model_home_probability = home_win_probability
    model_draw_probability = draw_probability
    model_away_probability = away_win_probability

    fixture = match.get("fixture", {})
    fixture_id = fixture.get("id")

    market_data = None

    success, odds_response = get_fixture_odds(fixture_id)

    if success:
        market_data = extract_match_winner_odds(odds_response)

    if market_data:
        blended = blend_probabilities(
            model_home=model_home_probability,
            model_draw=model_draw_probability,
            model_away=model_away_probability,
            market_home=market_data["market_home_probability"] / 100,
            market_draw=market_data["market_draw_probability"] / 100,
            market_away=market_data["market_away_probability"] / 100,
            model_weight=0.6,
        )

        home_win_probability = blended["home"]
        draw_probability = blended["draw"]
        away_win_probability = blended["away"]

    if (
        home_win_probability > draw_probability
        and home_win_probability > away_win_probability
    ):
        preferred_outcome = "home"

    elif (
        away_win_probability > draw_probability
        and away_win_probability > home_win_probability
    ):
        preferred_outcome = "away"

    else:
        preferred_outcome = "draw"

    most_likely_score, score_probability = find_most_likely_score(
        home_expected_goals,
        away_expected_goals,
        preferred_outcome=preferred_outcome,
    )

    home_stats = get_team_stats(home_team)
    away_stats = get_team_stats(away_team)

    if abs(elo_difference) <= 50:
        confidence = "Mittel"
        explanation = "Beide Teams liegen laut Elo nah beieinander."
    elif elo_difference > 200:
        confidence = "Hoch"
        explanation = f"{home_team} ist laut Elo deutlich stärker."
    elif elo_difference > 100:
        confidence = "Mittel"
        explanation = f"{home_team} hat laut Elo klare Vorteile."
    elif elo_difference > 50:
        confidence = "Mittel"
        explanation = f"{home_team} ist laut Elo leicht stärker."
    elif elo_difference < -200:
        confidence = "Hoch"
        explanation = f"{away_team} ist laut Elo deutlich stärker."
    elif elo_difference < -100:
        confidence = "Mittel"
        explanation = f"{away_team} hat laut Elo klare Vorteile."
    else:
        confidence = "Mittel"
        explanation = f"{away_team} ist laut Elo leicht stärker."

    return {
        "prediction": most_likely_score,
        "confidence": confidence,
        "home_rating": home_elo,
        "away_rating": away_elo,
        "rating_difference": elo_difference,
        "home_host_bonus": home_host_bonus,
        "away_host_bonus": away_host_bonus,

        "model_home_probability": round(model_home_probability * 100, 1),
        "model_draw_probability": round(model_draw_probability * 100, 1),
        "model_away_probability": round(model_away_probability * 100, 1),

        "home_win_probability": round(home_win_probability * 100, 1),
        "draw_probability": round(draw_probability * 100, 1),
        "away_win_probability": round(away_win_probability * 100, 1),

        "expected_home_goals": round(home_expected_goals, 2),
        "expected_away_goals": round(away_expected_goals, 2),
        "most_likely_score": most_likely_score,
        "score_probability": score_probability,
        "preferred_outcome": preferred_outcome,

        "home_attack": home_stats["attack"],
        "home_defense": home_stats["defense"],
        "away_attack": away_stats["attack"],
        "away_defense": away_stats["defense"],

        "tournament_context": tournament_context,
        "market_data": market_data,
        "explanation": explanation,
    }