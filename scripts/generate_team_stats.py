from collections import defaultdict

from data.api_client import get_world_cup_all_matches


def generate_team_stats():
    success, matches = get_world_cup_all_matches()

    if not success:
        print("Fehler beim Laden der WM-Spiele:")
        print(matches)
        return

    stats = defaultdict(lambda: {
        "matches": 0,
        "goals_for": 0,
        "goals_against": 0,
    })

    total_goals = 0
    total_team_games = 0

    for match in matches:
        teams = match.get("teams", {})
        goals = match.get("goals", {})

        home = teams.get("home", {}).get("name")
        away = teams.get("away", {}).get("name")

        home_goals = goals.get("home")
        away_goals = goals.get("away")

        if home is None or away is None:
            continue

        if home_goals is None or away_goals is None:
            continue

        stats[home]["matches"] += 1
        stats[home]["goals_for"] += home_goals
        stats[home]["goals_against"] += away_goals

        stats[away]["matches"] += 1
        stats[away]["goals_for"] += away_goals
        stats[away]["goals_against"] += home_goals

        total_goals += home_goals + away_goals
        total_team_games += 2

    average_goals_per_team_game = total_goals / total_team_games

    team_stats = {}

    for team, values in stats.items():
        matches_played = values["matches"]

        goals_for_per_game = values["goals_for"] / matches_played
        goals_against_per_game = values["goals_against"] / matches_played

        attack = goals_for_per_game / average_goals_per_team_game
        defense = goals_against_per_game / average_goals_per_team_game

        team_stats[team] = {
            "attack": round(attack, 2),
            "defense": round(defense, 2),
        }

    print("TEAM_STATS = {")
    for team in sorted(team_stats):
        print(f'    "{team}": {team_stats[team]},')
        print("}")


if __name__ == "__main__":
    generate_team_stats()