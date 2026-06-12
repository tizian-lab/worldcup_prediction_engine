import subprocess
import sys
from pathlib import Path

from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import ContextTypes

from data.api_client import (
    test_api_connection,
    get_todays_matches,
    get_world_cup_matches,
    debug_world_cup_fixtures,
    get_world_cup_all_matches,
    get_world_cup_match_by_number,
)
from prediction.engine import generate_prediction

from evaluation.evaluator import (
    evaluate_match,
    update_evaluation_stats,
    get_evaluation_stats,
)

def format_kickoff_time(date_string):
    if not date_string:
        return "Datum/Uhrzeit offen"

    utc_time = datetime.fromisoformat(
        date_string.replace("Z", "+00:00")
    )

    berlin_time = utc_time.astimezone(
        ZoneInfo("Europe/Berlin")
    )

    return berlin_time.strftime("%d.%m.%Y | %H:%M Uhr")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Willkommen beim WM-Kicktipp-Bot ⚽\n\n"
        "Verfügbare Befehle:\n"
        "/spiele - zeigt heutige WM-Spiele\n"
        "/wmalle - zeigt WM-Spiele\n"
        "/wmspiel 1 - zeigt ein einzelnes WM-Spiel\n"
        "/wmtipp 1 - zeigt eine Prognose für ein Spiel\n"
        "/wmtipps - zeigt mehrere Prognosen\n"
        "/api - testet die API-Verbindung\n"
        "/help - zeigt Hilfe"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Aktuell verfügbare Befehle:\n\n"
        "/start\n"
        "/spiele\n"
        "/wmalle\n"
        "/wmspiel 1\n"
        "/wmtipp 1\n"
        "/wmtipps\n"
        "/api\n"
        "/debugwm\n"
        "/help"
    )


async def tipps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Nutze ab jetzt am besten:\n\n"
        "/wmtipp 1 - einzelner Tipp\n"
        "/wmtipps - mehrere Tipps"
    )


async def api_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    success, result = test_api_connection()

    if success:
        await update.message.reply_text(
            "✅ API-Football ist erreichbar.\n"
            "Der API-Key funktioniert."
        )
    else:
        await update.message.reply_text(
            "❌ API-Football ist nicht erreichbar.\n\n"
            f"{result}"
        )


async def spiele(update: Update, context: ContextTypes.DEFAULT_TYPE):
    success, result = get_todays_matches()

    if not success:
        await update.message.reply_text(
            "❌ Spiele konnten nicht geladen werden.\n\n"
            f"{result}"
        )
        return

    if not result:
        await update.message.reply_text(
            "Heute wurden keine WM-Spiele gefunden."
        )
        return

    text = "⚽ Heutige WM-Spiele:\n\n"

    for match in result[:10]:
        fixture = match.get("fixture", {})
        teams = match.get("teams", {})
        league = match.get("league", {})

        home = teams.get("home", {}).get("name", "Heimteam")
        away = teams.get("away", {}).get("name", "Auswärtsteam")
        league_name = league.get("name", "Unbekannter Wettbewerb")
        kickoff = format_kickoff_time(fixture.get("date", ""))

        text += (
            f"{home} – {away}\n"
            f"{league_name} | {kickoff}\n\n"
        )

    await update.message.reply_text(text)


async def wmspiele(update: Update, context: ContextTypes.DEFAULT_TYPE):
    success, result = get_world_cup_matches()

    if not success:
        await update.message.reply_text(
            "❌ WM-Spiele konnten nicht geladen werden.\n\n"
            f"{result}"
        )
        return

    if not result:
        await update.message.reply_text(
            "Es wurden keine kommenden WM-Spiele gefunden."
        )
        return

    text = "🏆 Kommende WM-Spiele:\n\n"

    for match in result:
        fixture = match.get("fixture", {})
        teams = match.get("teams", {})
        league = match.get("league", {})

        home = teams.get("home", {}).get("name", "Heimteam")
        away = teams.get("away", {}).get("name", "Auswärtsteam")
        league_name = league.get("name", "World Cup")
        kickoff = format_kickoff_time(fixture.get("date", ""))

        text += (
            f"{home} – {away}\n"
            f"{league_name} | {kickoff}\n\n"
        )

    await update.message.reply_text(text)


async def debugwm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = debug_world_cup_fixtures()

    text = (
        "🔎 WM-Debug:\n\n"
        f"Statuscode: {result['status_code']}\n"
        f"Errors: {result['errors']}\n"
        f"Results: {result['results']}\n"
        f"Parameters: {result['parameters']}\n"
        f"Response Count: {result['response_count']}"
    )

    await update.message.reply_text(text)


async def wmalle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    success, result = get_world_cup_all_matches()

    if not success:
        await update.message.reply_text(
            "❌ WM-Spiele konnten nicht geladen werden.\n\n"
            f"{result}"
        )
        return

    if not result:
        await update.message.reply_text(
            "Es wurden keine WM-Spiele gefunden."
        )
        return

    text = "🏆 WM-Spiele:\n\n"

    for index, match in enumerate(result[:10], start=1):
        fixture = match.get("fixture", {})
        teams = match.get("teams", {})

        home = teams.get("home", {}).get("name", "Heimteam")
        away = teams.get("away", {}).get("name", "Auswärtsteam")
        kickoff = format_kickoff_time(fixture.get("date", ""))

        text += (
            f"{index}. {home} – {away}\n"
            f"{kickoff}\n\n"
        )

    await update.message.reply_text(text)


async def wmspiel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Bitte gib eine Spielnummer an.\n\n"
            "Beispiel:\n"
            "/wmspiel 1"
        )
        return

    try:
        match_number = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "Bitte gib eine gültige Zahl ein.\n\n"
            "Beispiel:\n"
            "/wmspiel 1"
        )
        return

    success, result = get_world_cup_match_by_number(match_number)

    if not success:
        await update.message.reply_text(f"❌ {result}")
        return

    fixture = result.get("fixture", {})
    league = result.get("league", {})
    teams = result.get("teams", {})
    goals = result.get("goals", {})
    score = result.get("score", {})

    home = teams.get("home", {}).get("name", "Heimteam")
    away = teams.get("away", {}).get("name", "Auswärtsteam")

    league_name = league.get("name", "World Cup")
    round_name = league.get("round", "Runde unbekannt")
    kickoff = format_kickoff_time(fixture.get("date", ""))
    status = fixture.get("status", {}).get("long", "Status unbekannt")

    home_goals = goals.get("home")
    away_goals = goals.get("away")

    penalty = score.get("penalty", {})
    home_penalty = penalty.get("home")
    away_penalty = penalty.get("away")

    text = (
        f"🏆 {league_name}\n"
        f"{round_name}\n\n"
        f"{home} – {away}\n"
        f"{kickoff}\n\n"
        f"Status: {status}\n"
    )

    if home_goals is not None and away_goals is not None:
        text += f"\nErgebnis: {home_goals}:{away_goals}"

    if home_penalty is not None and away_penalty is not None:
        text += f"\nElfmeterschießen: {home_penalty}:{away_penalty}"

    await update.message.reply_text(text)


async def wmtipp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Bitte gib eine Spielnummer an.\n\n"
            "Beispiel:\n"
            "/wmtipp 1"
        )
        return

    try:
        match_number = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "Bitte eine gültige Zahl eingeben."
        )
        return

    success, match = get_world_cup_match_by_number(match_number)

    if not success:
        await update.message.reply_text(f"❌ {match}")
        return

    prediction = generate_prediction(match)

    fixture = match.get("fixture", {})
    teams = match.get("teams", {})

    home = teams.get("home", {}).get("name", "Heimteam")
    away = teams.get("away", {}).get("name", "Auswärtsteam")
    kickoff = format_kickoff_time(fixture.get("date", ""))
    market_data = prediction.get("market_data")

    market_text = "Keine Marktdaten verfügbar"

    if market_data:
        market_text = (
            f"Bookmaker: {market_data['bookmaker']}\n"
            f"{home}: {market_data['market_home_probability']} % "
            f"(Quote {market_data['home_odd']})\n"
            f"Remis: {market_data['market_draw_probability']} % "
            f"(Quote {market_data['draw_odd']})\n"
            f"{away}: {market_data['market_away_probability']} % "
            f"(Quote {market_data['away_odd']})"
        )

    text = (
        f"🤖 WM-Prognose\n\n"
        f"{home} – {away}\n"
        f"{kickoff}\n\n"
        f"Tipp: {prediction['prediction']}\n"
        f"Vertrauen: {prediction['confidence']}\n\n"
        f"Elo-Rating:\n"
        f"{home}: {prediction['home_rating']}\n"
        f"{away}: {prediction['away_rating']}\n"
        f"Differenz: {prediction['rating_difference']}\n\n"
        f"Modell-Wahrscheinlichkeit:\n"
        f"{home}: {prediction['model_home_probability']} %\n"
        f"Remis: {prediction['model_draw_probability']} %\n"
        f"{away}: {prediction['model_away_probability']} %\n\n"
        f"Markt-Wahrscheinlichkeit:\n"
        f"{market_text}\n\n"
        f"Hybrid-Wahrscheinlichkeit:\n"
        f"{home}: {prediction['home_win_probability']} %\n"
        f"Remis: {prediction['draw_probability']} %\n"
        f"{away}: {prediction['away_win_probability']} %\n\n"
        f"Erwartete Tore:\n"
        f"{home}: {prediction['expected_home_goals']}\n"
        f"{away}: {prediction['expected_away_goals']}\n\n"
        f"Wahrscheinlichstes Ergebnis:\n"
        f"{prediction['most_likely_score']}\n"
        f"Trefferwahrscheinlichkeit: {prediction['score_probability']} %\n\n"
        f"Turnierkontext:\n"
        f"{prediction['tournament_context']['description']}\n\n"
        f"Begründung:\n"
        f"{prediction['explanation']}"
    )

    await update.message.reply_text(text)


async def wmtipps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    success, matches = get_world_cup_all_matches()

    if not success:
        await update.message.reply_text(
            "❌ WM-Tipps konnten nicht geladen werden.\n\n"
            f"{matches}"
        )
        return

    if not matches:
        await update.message.reply_text(
            "Es wurden keine WM-Spiele gefunden."
        )
        return

    text = "🏆 WM-Tipps\n\n"

    for index, match in enumerate(matches[:10], start=1):
        fixture = match.get("fixture", {})
        teams = match.get("teams", {})

        home = teams.get("home", {}).get("name", "Heimteam")
        away = teams.get("away", {}).get("name", "Auswärtsteam")
        kickoff = format_kickoff_time(fixture.get("date", ""))

        prediction = generate_prediction(match)

        text += (
            f"{index}. {home} – {away}\n"
            f"{kickoff}\n"
            f"Tipp: {prediction['prediction']}\n"
            f"Wahrscheinlichkeit: {prediction['score_probability']} %\n\n"
        )

    await update.message.reply_text(text)

async def update_stats(update, context):
    await update.message.reply_text(
        "🔄 Aktualisiere Team-Statistiken..."
    )

    try:
        project_root = Path(__file__).resolve().parent.parent

        script_path = (
            project_root
            / "scripts"
            / "update_team_stats.py"
        )

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            await update.message.reply_text(
                "✅ Team-Statistiken erfolgreich aktualisiert."
            )
        else:
            await update.message.reply_text(
                f"❌ Fehler:\n\n{result.stderr}"
            )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Fehler:\n\n{e}"
        )

async def refresh(update, context):
    await update.message.reply_text(
        "🔄 Starte vollständige Aktualisierung..."
    )

    try:
        project_root = Path(__file__).resolve().parent.parent

        scripts = [
            "update_team_stats.py",
            "update_team_ratings.py",
        ]

        output_messages = []

        for script in scripts:
            script_path = project_root / "scripts" / script

            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                output_messages.append(f"✅ {script} erfolgreich ausgeführt.")
            else:
                output_messages.append(
                    f"❌ Fehler in {script}:\n{result.stderr}"
                )

        await update.message.reply_text(
            "\n\n".join(output_messages)
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Fehler beim Refresh:\n\n{e}"
        )

async def evaluate(update, context):
    success, matches = get_world_cup_all_matches()

    if not success:
        await update.message.reply_text(
            "❌ Evaluation konnte nicht geladen werden.\n\n"
            f"{matches}"
        )
        return

    evaluated = []

    for index, match in enumerate(matches, start=1):
        result = evaluate_match(match)

        if result is None:
            continue

        update_evaluation_stats(result)

        teams = match.get("teams", {})

        home = teams.get("home", {}).get(
            "name",
            "Heimteam"
        )

        away = teams.get("away", {}).get(
            "name",
            "Auswärtsteam"
        )

        evaluated.append(
            {
                "index": index,
                "home": home,
                "away": away,
                **result,
            }
        )

    if not evaluated:
        await update.message.reply_text(
            "Es gibt noch keine fertigen Spiele zur Evaluation."
        )
        return

    exact_hits = sum(
        1
        for item in evaluated
        if item["exact_score"]
    )

    tendency_hits = sum(
        1
        for item in evaluated
        if item["correct_tendency"]
    )

    total = len(evaluated)

    stats = get_evaluation_stats()

    text = (
        f"📊 Modell-Evaluation\n\n"

        f"Aktuelle Auswertung:\n"
        f"Ausgewertete Spiele: {total}\n"
        f"Exakte Treffer: {exact_hits}/{total}\n"
        f"Tendenz richtig: {tendency_hits}/{total}\n\n"

        f"Gesamtstatistik:\n"
        f"Ausgewertete Spiele: {stats['matches_evaluated']}\n"
        f"Exakte Treffer: {stats['exact_hits']}\n"
        f"Tendenztreffer: {stats['tendency_hits']}\n\n"

        f"Letzte ausgewertete Spiele:\n"
    )

    for item in evaluated[:10]:
        exact_icon = (
            "🎯"
            if item["exact_score"]
            else "—"
        )

        tendency_icon = (
            "✅"
            if item["correct_tendency"]
            else "❌"
        )

        text += (
            f"\n{item['index']}. "
            f"{item['home']} – {item['away']}\n"
            f"Tipp: {item['prediction']} | "
            f"Ergebnis: {item['actual_score']}\n"
            f"Tendenz: {tendency_icon} | "
            f"Exakt: {exact_icon}\n"
        )

    await update.message.reply_text(text)