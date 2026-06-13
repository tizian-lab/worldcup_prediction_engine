# worldcup_prediction_engine
World Cup Prediction Engine

# Kicktipp WM 2026 Prediction Engine

A Python-based football prediction engine built for the FIFA World Cup 2026.

The project combines Elo ratings, recent team form, betting market odds, attack/defense metrics, tournament context, and probabilistic score modeling to generate match predictions and Kicktipp-ready score suggestions.

---

## Features

### Match Predictions

* Elo-based team strength ratings
* Attack/Defense performance model
* Poisson score distribution
* Most likely score prediction
* Top outcome optimization for Kicktipp scoring

### Market Integration

* Live betting odds integration via API-Football
* Hybrid probability model
* Current weighting:

  * 60% internal prediction model
  * 40% betting market probabilities

### Tournament Context

* Group Stage adjustments
* Knockout Stage adjustments
* Final-specific scoring adjustments
* Host nation bonus:

  * USA
  * Mexico
  * Canada

### Data Automation

* Automatic team statistics generation
* Automatic rating updates
* World Cup fixture retrieval
* Local timezone conversion (Europe/Berlin)

### Telegram Bot

Supported commands:

```text
/start
/help

/wmspiele
/wmspiel <id>
/wmtipp <id>
/wmtipps

/update_stats
/refresh

/evaluate
```

### Evaluation System

The project contains an evaluation framework to compare predictions against real match results.

Metrics include:

* Exact score hit rate
* Correct tendency rate
* Goal difference error
* Total goal error

Results are stored locally and protected against duplicate evaluations.

---

## Prediction Factors

Currently included:

* Elo Ratings
* Recent Form (last 10 matches)
* Attack Strength
* Defensive Strength
* Poisson Distribution
* Betting Odds
* Host Nation Bonus
* Tournament Phase Context
* Hybrid Market Model

Not yet included:

* Injuries
* Suspensions
* Expected Goals (xG)
* Weather Conditions
* Referee Effects
* Group Qualification Scenarios
* Player Market Values

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd kicktipp_engine_v6
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file:

```env
TELEGRAM_TOKEN=your_telegram_token
API_FOOTBALL_KEY=your_api_key

WORLD_CUP_LEAGUE_ID=1
WORLD_CUP_SEASON=2026
```

Never commit your `.env` file.

---

## Project Structure

```text
bot/
data/
evaluation/
formatting/
prediction/
scripts/

main.py
config.py
requirements.txt
```

---

## Disclaimer

This project was created for educational purposes and for participation in private football prediction competitions.

Predictions are probabilistic estimates and should not be considered financial or betting advice.

```
```
