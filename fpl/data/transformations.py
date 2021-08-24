"""Common transformation."""
import hashlib

import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm

from fpl.data.io import list_data_dir, load_json


def get_game_week(events: list) -> int:
    """Get the gameweek from a events list.

    Args:
        data_dump (list[dict]): list holding event dicts

    Returns:
        int: Current gameweek
    """
    gw = list(filter(lambda x: x["is_current"] is True, events))

    return gw[0]["id"] if gw else 0


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


def create_opponents(fixtures: dict, sort=False) -> dict:
    """Return the fixtures list for each PL team.

    Args:
        fixtures (dict, optional): fixtures
        sort (boolean, optional): Sort opponents on gameweek. Defaults to False.

    Returns:
        dict: {team_id: [{team_id: int, difficulty: int, venue: str}]}
    """
    all_teams = {}
    for team_id in range(1,21):
        opponents = []
        for event in fixtures["fixtures"]:
            if event["team_h"] == team_id:
                opponents.append(
                    {
                        "team_id": event["team_a"],
                        "difficulty": event["team_h_difficulty"],
                        "venue": "h",
                        "gameweek": event["event"],
                    }
                )
            if event["team_a"] == team_id:
                opponents.append(
                    {
                        "team_id": event["team_h"],
                        "difficulty": event["team_a_difficulty"],
                        "venue": "a",
                        "gameweek": event["event"],
                    }
                )

        if sort:
            all_teams[team_id] = sorted(
                opponents, key=lambda i: i["gameweek"] if i["gameweek"] else 99999
            )
        else:
            all_teams[team_id] = opponents
    return all_teams


def to_csv(entity="teams", data_path="data/raw/2021-fpl-data", fixtures_path="data/raw/2021_fixtures/"):
    """Transform data and save as CSV.

    Args:
        entity (str, optional): Entity to grab from JSON.
        data_path (str, optional): Path to dir holding JSON dumps. Defaults to "data".
    """
    elements = []
    fixtures_list = list_data_dir(fixtures_path)

    for data in tqdm(list_data_dir(data_path)):
        try:
            data = load_json(data)
            add_gw_and_download_time(
                data[entity], data["download_time"], get_game_week(data["events"])
            )
            
            
            if entity == "teams":
           
                fixtures = load_json(_nearest(fixtures_list, data["download_time"]))
                all_fixtures_list = create_opponents(fixtures)
                list(map(lambda x: _add_next_opponents(x, data[entity], all_fixtures_list) , data["teams"]))
            
            elements.extend(data[entity])
        # Add transformations here
        except TypeError:
            print(f"Something is wrong in {data}")

    return pd.DataFrame(elements)


def _nearest(items, pivot):
    if isinstance(items[0], str):
        items = [(datetime.strptime(i, "%Y-%m-%d %H:%M:%S.%f"),i) for i in items]
    else:
        items = [(datetime.strptime(i.name.split(".")[0].split("_")[0], "%Y-%m-%dT%H-%M-%SZ"),i) for i in items]  
    if isinstance(pivot,str):
        pivot = datetime.strptime(pivot, "%Y-%m-%d %H:%M:%S.%f")
        
    return min(items, key=lambda x : abs(x[0] - pivot) if (x[0] <= pivot) else timedelta(days=100000))[1]

def _elaborate_opponent(opponent, teams_data, num):
    opponent_data = teams_data[opponent["team_id"]]
    return {
        f"opponent_{num}_name": opponent_data["name"],
        f"opponent_{num}_venue": opponent["venue"],
        f"opponent_{num}_strengh_attack": opponent_data["strength_attack_home"] if opponent[f"venue"] == "h" else opponent_data["strength_attack_away"],
        f"opponent_{num}_strengh_defence": opponent_data["strength_defence_home"] if opponent[f"venue"] == "h" else opponent_data["strength_defence_away"],
        # Have to check for NaN by comparing NaN == NaN returns False. 
        f"opponent_{num}_played_in_gw": int(opponent["gameweek"]) if isinstance(opponent["gameweek"], (int, float)) and opponent["gameweek"] == opponent["gameweek"] else -1 
    }


def _add_next_opponents(team, teams: dict, all_fixtures: list, num_opponents=5):
    """Add next 5 fixtures to an element.

    Args:
        element (dict): Player element from /bootstrap-static
        all_teams (list): All teams element from /boostrap-static
    """
    if not isinstance(teams, dict):  
        teams = {i["id"]: i for i in teams}
        
    for num, opponent in enumerate(all_fixtures[team["id"]][team["gameweek"]:team["gameweek"]+5]):
        team.update(_elaborate_opponent(opponent, teams, num))


if __name__ == "__main__":
    to_csv(data_path="/home/vagrant/dev/fpl2021/data/raw/2021-fpl-data", fixtures_path="/home/vagrant/dev/fpl2021/data/raw/2021-fpl-fixtures")