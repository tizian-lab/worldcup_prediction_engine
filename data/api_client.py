import requests
from datetime import date

from config import (
    API_FOOTBALL_KEY,
    WORLD_CUP_LEAGUE_ID,
    WORLD_CUP_SEASON,
)


BASE_URL = "https://v3.football.api-sports.io"


def _get_headers():
    return {
        "x-apisports-key": API_FOOTBALL_KEY
    }


def _get(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"

    response = requests.get(
        url,
        headers=_get_headers(),
        params=params,
        timeout=10,
    )

    if response.status_code != 200:
        return False, f"API-Fehler: Statuscode {response.status_code}"

    data = response.json()

    if data.get("errors"):
        return False, f"API-Fehler: {data.get('errors')}"

    return True, data


def test_api_connection():
    success, result = _get("status")

    if not success:
        return False, result

    return True, result


def get_todays_matches():
    today = date.today().isoformat()

    success, data = _get(
        "fixtures",
        {
            "date": today,
            "league": WORLD_CUP_LEAGUE_ID,
            "season": WORLD_CUP_SEASON,
        },
    )

    if not success:
        return False, data

    return True, data.get("response", [])


def get_world_cup_matches():
    success, data = _get(
        "fixtures",
        {
            "league": WORLD_CUP_LEAGUE_ID,
            "season": WORLD_CUP_SEASON,
            "next": 10,
        },
    )

    if not success:
        return False, data

    return True, data.get("response", [])


def get_world_cup_all_matches():
    success, data = _get(
        "fixtures",
        {
            "league": WORLD_CUP_LEAGUE_ID,
            "season": WORLD_CUP_SEASON,
        },
    )

    if not success:
        return False, data

    return True, data.get("response", [])


def get_world_cup_match_by_number(match_number):
    success, matches = get_world_cup_all_matches()

    if not success:
        return False, matches

    if match_number < 1 or match_number > len(matches):
        return False, f"Bitte eine Zahl zwischen 1 und {len(matches)} eingeben."

    return True, matches[match_number - 1]


def debug_world_cup_fixtures():
    url = f"{BASE_URL}/fixtures"

    params = {
        "league": WORLD_CUP_LEAGUE_ID,
        "season": WORLD_CUP_SEASON,
    }

    response = requests.get(
        url,
        headers=_get_headers(),
        params=params,
        timeout=10,
    )

    data = response.json()

    return {
        "status_code": response.status_code,
        "errors": data.get("errors"),
        "results": data.get("results"),
        "parameters": data.get("parameters"),
        "response_count": len(data.get("response", [])),
    }


def test_team_statistics():
    success, data = _get(
        "teams",
        {
            "id": 25,
        },
    )

    if not success:
        return False, data

    return True, data


def test_team_fixtures():
    success, data = _get(
        "fixtures",
        {
            "team": 25,
            "last": 10,
        },
    )

    if not success:
        return False, data

    return True, data


def get_team_fixtures(team_id, last=10):
    success, data = _get(
        "fixtures",
        {
            "team": team_id,
            "last": last,
        },
    )

    if not success:
        return False, data

    return True, data.get("response", [])

def test_odds():
    success, matches = get_world_cup_all_matches()

    if not success or not matches:
        return False, "Keine WM-Spiele gefunden"

    fixture_id = matches[0]["fixture"]["id"]

    return _get(
        "odds",
        {
            "fixture": fixture_id
        }
    )

def get_fixture_odds(fixture_id):
    success, data = _get(
        "odds",
        {
            "fixture": fixture_id,
        },
    )

    if not success:
        return False, data

    return True, data.get("response", [])