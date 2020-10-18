"""Get odds."""
import datetime
import json
import os

import requests


def get_odds(market="h2h", uri="https://api.the-odds-api.com/v3/odds", api_key=None):
    """Return odds.

    Args:
        market (str, optional): Type of odds to return. Valid values: "h2h", "totals", "spread".
            Defaults to "h2h".
        uri (str, optional): URL to odds-api. Defaults to "https://api.the-odds-api.com/v3/odds".
        api_key ([type], optional): API key. Defaults to None.

    Returns:
        dict: Odds for EPL
    """
    download_time = str(datetime.datetime.now())
    odds_response = requests.get(
        uri,
        params={
            "api_key": api_key,
            "sport": "soccer_epl",
            "region": "uk",
            "mkt": market,  # totals
        },
    )
    odds = json.loads(odds_response.text)
    odds["download_time"] = download_time
    return odds
