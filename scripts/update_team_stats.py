from pathlib import Path

from data.api_client import (
    get_team_fixtures,
    get_world_cup_all_matches,
)


NUMBER_OF_RECENT_MATCHES = 10

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "prediction" / "team_stats.py"


def collect_world_cup_teams(matches):
    teams = {}

    for match in matches:
        match_teams = match.get("teams", {})

        for side in ["home", "away"]:
            team = match_teams.get(side, {})
            team_id = team.get("id")
            team_name = team.get("name")

            if team_id and team_name:
                teams[team_name] = team_id

    return teams


def calculate_team_stat(team_name, team_id):
    success, fixtures = get_team_fixtures(
        team_id=team_id,
        last=NUMBER_OF_RECENT_MATCHES,
    )

    if not success:
        print(f"⚠️ Fehler bei {team_name}: {fixtures}")
        return {
            "attack": 1.0,
            "defense": 1.0,
        }

    goals_for = 0
    goals_against = 0
    matches_count = 0

    for fixture in fixtures:
        teams = fixture.get("teams", {})
        goals = fixture.get("goals", {})

        home_team = teams.get("home", {})
        away_team = teams.get("away", {})

        home_id = home_team.get("id")
        away_id = away_team.get("id")

        home_goals = goals.get("home")
        away_goals = goals.get("away")

        if home_goals is None or away_goals is None:
            continue

        if home_id == team_id:
            goals_for += home_goals
            goals_against += away_goals
            matches_count += 1

        elif away_id == team_id:
            goals_for += away_goals
            goals_against += home_goals
            matches_count += 1

    if matches_count == 0:
        return {
            "attack": 1.0,
            "defense": 1.0,
        }

    goals_for_per_game = goals_for / matches_count
    goals_against_per_game = goals_against / matches_count

    average_goals_per_team_game = 1.35

    attack = goals_for_per_game / average_goals_per_team_game
    defense = goals_against_per_game / average_goals_per_team_game

    attack = max(0.6, min(attack, 1.8))
    defense = max(0.5, min(defense, 1.5))

    return {
        "attack": round(attack, 2),
        "defense": round(defense, 2),
    }


def write_team_stats_file(team_stats):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write("# Auto-generiert durch scripts/update_team_stats.py\n\n")
        file.write("TEAM_STATS = {\n")

        for team_name in sorted(team_stats):
            file.write(
                f'    "{team_name}": {team_stats[team_name]},\n'
            )

        file.write("}\n")


def main():
    success, matches = get_world_cup_all_matches()

    if not success:
        print("❌ WM-Spiele konnten nicht geladen werden:")
        print(matches)
        return

    teams = collect_world_cup_teams(matches)

    print(f"Gefundene WM-Teams: {len(teams)}")

    team_stats = {}

    for team_name, team_id in sorted(teams.items()):
        print(f"Berechne Stats für {team_name}...")

        team_stats[team_name] = calculate_team_stat(
            team_name=team_name,
            team_id=team_id,
        )

    write_team_stats_file(team_stats)

    print("\n✅ team_stats.py wurde aktualisiert.")
    print(f"Datei: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()