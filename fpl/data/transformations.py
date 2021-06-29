"""Common transformation."""
import hashlib


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
