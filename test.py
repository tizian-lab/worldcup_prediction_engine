from data.api_client import test_odds
from prediction.odds import extract_match_winner_odds

success, data = test_odds()

print(success)

if success:
    result = extract_match_winner_odds(data.get("response", []))
    print(result)