from pathlib import Path

from data.api_client import get_world_cup_all_matches


DEFAULT_ELO = 1700

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "prediction" / "team_ratings.py"


ELO_RATINGS_SOURCE = {
    "Spain": 2157,
    "Argentina": 2114,
    "France": 2063,
    "England": 2021,
    "Brazil": 1991,
    "Portugal": 1986,
    "Colombia": 1982,
    "Netherlands": 1948,
    "Ecuador": 1938,
    "Germany": 1932,
    "Norway": 1914,
    "Croatia": 1912,
    "Belgium": 1908,
    "Uruguay": 1888,
    "Morocco": 1880,
    "Switzerland": 1855,
    "Japan": 1850,
    "Mexico": 1845,
    "Denmark": 1840,
    "Austria": 1830,
    "Senegal": 1815,
    "Sweden": 1810,
    "Türkiye": 1805,
    "South Korea": 1795,
    "Iran": 1790,
    "Australia": 1777,
    "Czech Republic": 1770,
    "Scotland": 1765,
    "Paraguay": 1760,
    "USA": 1755,
    "Ivory Coast": 1745,
    "Algeria": 1740,
    "Egypt": 1735,
    "Ghana": 1715,
    "Canada": 1710,
    "Poland": 1705,
    "Tunisia": 1695,
    "Saudi Arabia": 1680,
    "Bosnia & Herzegovina": 1675,
    "South Africa": 1665,
    "Congo DR": 1660,
    "Uzbekistan": 1645,
    "Iraq": 1635,
    "Panama": 1625,
    "Cape Verde Islands": 1615,
    "Jordan": 1605,
    "New Zealand": 1585,
    "Curaçao": 1575,
    "Qatar": 1565,
    "Haiti": 1505,
}


def collect_world_cup_teams(matches):
    teams = set()

    for match in matches:
        match_teams = match.get("teams", {})

        for side in ["home", "away"]:
            team = match_teams.get(side, {})
            team_name = team.get("name")

            if team_name:
                teams.add(team_name)

    return sorted(teams)


def build_team_ratings(team_names):
    ratings = {}
    missing_teams = []

    for team_name in team_names:
        elo = ELO_RATINGS_SOURCE.get(team_name)

        if elo is None:
            elo = DEFAULT_ELO
            missing_teams.append(team_name)

        ratings[team_name] = elo

    return ratings, missing_teams


def write_team_ratings_file(team_ratings):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write("# Auto-generiert durch scripts/update_team_ratings.py\n\n")
        file.write(f"DEFAULT_ELO = {DEFAULT_ELO}\n\n")
        file.write("TEAM_ELO_RATINGS = {\n")

        for team_name in sorted(team_ratings):
            file.write(
                f'    "{team_name}": {team_ratings[team_name]},\n'
            )

        file.write("}\n")


def main():
    success, matches = get_world_cup_all_matches()

    if not success:
        print("❌ WM-Spiele konnten nicht geladen werden:")
        print(matches)
        return

    team_names = collect_world_cup_teams(matches)

    print(f"Gefundene WM-Teams: {len(team_names)}")

    team_ratings, missing_teams = build_team_ratings(team_names)

    write_team_ratings_file(team_ratings)

    print("\n✅ team_ratings.py wurde aktualisiert.")
    print(f"Datei: {OUTPUT_FILE}")

    if missing_teams:
        print("\n⚠️ Für diese Teams wurde DEFAULT_ELO verwendet:")
        for team in missing_teams:
            print(f"- {team}")


if __name__ == "__main__":
    main()