"""Common transformation."""
import hashlib
import json

import requests

from fpl.data.io import load_json


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


def add_team_name(elements: list, teams: list):
    """Add team name to element.

    Args:
        elements (list[dict]): list holding the elements
        teams (list[dict]): list holding teams
    """
    teams = {i["id"]: i["name"] for i in teams}
    list(map(lambda x: x.update({"team_name": teams[x["team"]]}), elements))


def create_opponents(
    teams_data: list, fixtures_uri="https://fantasy.premierleague.com/api/fixtures/", sort=False
) -> dict:
    """Return the fixtures list for each PL team.

    Args:
        teams_data (list): List holding teams data loaded from /api/boostrap-static dump
        fixtures_uri (str, optional): Path the FPL fixtures list.
            Defaults to "https://fantasy.premierleague.com/api/fixtures/".
        sort (boolean, optional): Sort opponents on gameweek. Defaults to False.

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


def get_team_opponents(all_teams: list, team_name: str, from_gameweek=1, number_fixtures=37):
    """Return fixtures data for a specific team.

    Args:
        all_teams (list): All teams fixtures list.
        team_name (str): The name of team to return fixtures on
        from_gameweek (int, optional): Fixtures from gameweek. Defaults to 1.
        number_fixtures (int, optional): Number of fixtures to return. Defaults to 37.

    Example:
        all_teams = create_opponents(
        data["teams"], fixtures_uri="https://fantasy.premierleague.com/api/fixtures/")
        fixtures = get_team_opponents(all_teams, "Man City", 1, 5)

    Returns:
        dict: {
        "opponents": list,
        "in_gameweeks": dict,
        "postponed": boolen,
        "has_double_gw": boolean,
    }
    """
    team_fixtures = all_teams[team_name][from_gameweek : from_gameweek + number_fixtures]
    if from_gameweek + number_fixtures > len(all_teams[team_name]):
        number_fixtures = len(all_teams[team_name]) - from_gameweek

    gameweeks = [i["gameweek"] for i in team_fixtures]
    gameweeks = {
        i: gameweeks.count(i)
        for i in range(from_gameweek + 1, from_gameweek + number_fixtures + 1, 1)
    }
    return {
        "opponents": team_fixtures,
        "in_gameweeks": gameweeks,
        "postponed": bool([i for i in gameweeks if gameweeks[i] < 1]),
        "has_double_gw": bool([i for i in gameweeks if gameweeks[i] > 1]),
    }


def _add_next_five(element: dict, all_teams: list):
    """Add next 5 fixtures to an element.

    Args:
        element (dict): Player element from /bootstrap-static
        all_teams (list): All teams element from /boostrap-static
    """
    data = get_team_opponents(all_teams, element["team_name"], element["gameweek"], 5)
    opponents_extracted = {}
    for i, y in enumerate(data["opponents"]):
        if y["gameweek"]:
            opponents_extracted.update(
                {
                    "n+{}_opponent".format(i): y["team"],
                    "n+{}_difficulty".format(i): y["difficulty"],
                    "n+{}_venue".format(i): y["venue"],
                    "n+{}_gw".format(i): y["gameweek"],
                }
            )
        else:
            opponents_extracted.update(
                {
                    "n+{}_opponent".format(i): None,
                    "n+{}_difficulty".format(i): None,
                    "n+{}_venue".format(i): None,
                    "n+{}_gw".format(i): element["gameweek"] + 1 + i,
                }
            )

    element.update(opponents_extracted)
    del data["opponents"]
    del data["in_gameweeks"]
    element.update(data)


def add_opponents(elements: list, all_teams: list):
    """Update all elements with fixtures.

    Args:
        elements (list): List holding elements
        all_teams (list): List holding teams
    """
    list(map(lambda x: _add_next_five(x, all_teams), elements))


if __name__ == "__main__":
    pass
