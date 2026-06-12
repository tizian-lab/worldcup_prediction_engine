from prediction.engine import generate_prediction

import json
from pathlib import Path

RESULTS_FILE = (
    Path(__file__).resolve().parent
    / "results.json"
)


def parse_score(score_text):
    home, away = score_text.split(":")
    return int(home), int(away)


def get_result_type(home_goals, away_goals):
    if home_goals > away_goals:
        return "home"
    if away_goals > home_goals:
        return "away"
    return "draw"


def evaluate_match(match):
    goals = match.get("goals", {})
    home_goals = goals.get("home")
    away_goals = goals.get("away")

    if home_goals is None or away_goals is None:
        return None

    prediction = generate_prediction(match)

    predicted_home, predicted_away = parse_score(
        prediction["prediction"]
    )

    predicted_result = get_result_type(
        predicted_home,
        predicted_away
    )

    actual_result = get_result_type(
        home_goals,
        away_goals
    )

    exact_score = (
        predicted_home == home_goals
        and predicted_away == away_goals
    )

    correct_tendency = predicted_result == actual_result

    goal_difference_error = abs(
        (predicted_home - predicted_away)
        - (home_goals - away_goals)
    )

    total_goal_error = abs(
        (predicted_home + predicted_away)
        - (home_goals + away_goals)
    )

    fixture = match.get("fixture", {})
    fixture_id = fixture.get("id")

    return {
        "fixture_id": fixture_id,
        "prediction": prediction["prediction"],
        "actual_score": f"{home_goals}:{away_goals}",
        "exact_score": exact_score,
        "correct_tendency": correct_tendency,
        "goal_difference_error": goal_difference_error,
        "total_goal_error": total_goal_error,
    }

def update_evaluation_stats(evaluation_result):
    if evaluation_result is None:
        return False

    fixture_id = evaluation_result.get("fixture_id")

    with open(RESULTS_FILE, "r", encoding="utf-8") as file:
        stats = json.load(file)

    if fixture_id in stats["evaluated_fixture_ids"]:
        return False

    stats["evaluated_fixture_ids"].append(fixture_id)
    stats["matches_evaluated"] += 1

    if evaluation_result["exact_score"]:
        stats["exact_hits"] += 1

    if evaluation_result["correct_tendency"]:
        stats["tendency_hits"] += 1

    stats["total_goal_error"] += evaluation_result["total_goal_error"]
    stats["goal_difference_error"] += evaluation_result["goal_difference_error"]

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(stats, file, indent=4, ensure_ascii=False)

    return True

def get_evaluation_stats():
    with open(RESULTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)