def decimal_odd_to_probability(odd):
    return 1 / float(odd)


def normalize_probabilities(home, draw, away):
    total = home + draw + away

    return {
        "home": home / total,
        "draw": draw / total,
        "away": away / total,
    }


def extract_match_winner_odds(odds_response):
    if not odds_response:
        return None

    first_item = odds_response[0]
    bookmakers = first_item.get("bookmakers", [])

    for bookmaker in bookmakers:
        bets = bookmaker.get("bets", [])

        for bet in bets:
            if bet.get("name") != "Match Winner":
                continue

            values = bet.get("values", [])

            odds = {}

            for value in values:
                label = value.get("value")
                odd = value.get("odd")

                if label == "Home":
                    odds["home"] = float(odd)
                elif label == "Draw":
                    odds["draw"] = float(odd)
                elif label == "Away":
                    odds["away"] = float(odd)

            if all(key in odds for key in ["home", "draw", "away"]):
                raw_home = decimal_odd_to_probability(odds["home"])
                raw_draw = decimal_odd_to_probability(odds["draw"])
                raw_away = decimal_odd_to_probability(odds["away"])

                normalized = normalize_probabilities(
                    raw_home,
                    raw_draw,
                    raw_away,
                )

                return {
                    "bookmaker": bookmaker.get("name", "Unbekannt"),
                    "home_odd": odds["home"],
                    "draw_odd": odds["draw"],
                    "away_odd": odds["away"],
                    "market_home_probability": round(normalized["home"] * 100, 1),
                    "market_draw_probability": round(normalized["draw"] * 100, 1),
                    "market_away_probability": round(normalized["away"] * 100, 1),
                }

    return None

def blend_probabilities(
    model_home,
    model_draw,
    model_away,
    market_home,
    market_draw,
    market_away,
    model_weight=0.7,
):
    market_weight = 1 - model_weight

    return {
        "home": (
            model_home * model_weight
            + market_home * market_weight
        ),
        "draw": (
            model_draw * model_weight
            + market_draw * market_weight
        ),
        "away": (
            model_away * model_weight
            + market_away * market_weight
        ),
    }