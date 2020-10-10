"""Common transformation."""
import hashlib
from pathlib import Path

import requests

import fpl.data.io as io


def get_game_week(events: list) -> int:
    """Get the gameweek from a events list.

    Args:
        data_dump (list[dict]): list holding event dicts

    Returns:
        int: Current gameweek
    """
    gw = list(filter(lambda x: x["is_current"] is True, events))
    if gw:
        return gw[0]["id"]
    return 0


def create_id(element: dict) -> str:
    """Create a unique element id.

    Args:
        element (dict): The transformed document to be inserted to Cosmos,
            missing the required ["id"]

    Returns:
        str: Unique ID created from elements["code", download_time]
    """
    return hashlib.md5(
        str(element["code"]).encode("utf-8") + str(element["download_time"]).encode("utf-8")
    ).hexdigest()


def add_gw_and_download_time(elements: list, download_time: str, gameweek: int):
    """Add gameweek and download_time to element.

    Args:
        elements (list[dict]): elements to to add downloadtime and gameweek to.
        download_time (str): The time elements was downloaded
        gameweek (int): Current gameweek
    """
    list(map(lambda x: x.update({"download_time": download_time, "gameweek": gameweek}), elements))


def add_unique_id(elements: list):
    """Adding unique id to document and moving fpl_id to player_id.

    Args:
        elements (list[dict]): list holding the elements
    """
    list(map(lambda x: x.update({"player_id": x.pop("id")}), elements))
    list(map(lambda x: x.update({"id": create_id(x)}), elements))


def create_opponents(
    teams_data: list, fixtures_uri="https://fantasy.premierleague.com/api/fixtures/", sort=False
) -> dict:
    """Return the fixtures list for each PL team.

    Args:
        teams_data (list): List holding teams data loaded from /api/boostrap-static dump
        fixtures_uri (str, optional): Path the FPL fixtures list.
            Defaults to "https://fantasy.premierleague.com/api/fixtures/".

    Returns:
        dict: {team_name: [{team: str, difficulty: int, venue: str}]}
    """
    url = fixtures_uri
    fpl_json = requests.get(url).json()
    name_mapping = {i["id"]: i["name"] for i in teams_data}
    teams = set([i["team_a"] for i in fpl_json])
    all_teams = {}
    for y in teams:
        opponents = []
        for i in fpl_json:
            if i["team_h"] == y:
                opponents.append(
                    {
                        "team": name_mapping[i["team_a"]],
                        "difficulty": i["team_h_difficulty"],
                        "venue": "h",
                        "gameweek": i["event"],
                    }
                )
            if i["team_a"] == y:
                opponents.append(
                    {
                        "team": name_mapping[i["team_h"]],
                        "difficulty": i["team_a_difficulty"],
                        "venue": "a",
                        "gameweek": i["event"],
                    }
                )

        if sort:
            all_teams[name_mapping[y]] = sorted(
                opponents, key=lambda i: i["gameweek"] if i["gameweek"] else 99999
            )
        else:
            all_teams[name_mapping[y]] = opponents

    return all_teams
