from fpl import data
from fpl.data.transformations import (
    _add_next_five,
    add_gw_and_download_time,
    add_opponents,
    add_team_name,
    add_unique_id,
    create_id,
    create_opponents,
    get_game_week,
    get_team_opponents,
)
from tests.conftest import data_object, fixtures_object, teams_fixtures


def test_create_opponents(teams_fixtures, data_object):
    """Test of teams_fixtures."""
    teams_events = create_opponents(
        data_object["teams"], fixtures_uri="https://fantasy.premierleague.com/api/mock/"
    )
    for i in teams_events:
        assert len(teams_events[i]) == 38
        assert len(set(y["team"] for y in teams_events[i])) == 19
    assert teams_events["Man City"][0]["gameweek"] == None
    assert type(teams_events["Man City"][-1]["gameweek"]) == int

    teams_events = create_opponents(
        data_object["teams"], fixtures_uri="https://fantasy.premierleague.com/api/mock/", sort=True
    )
    assert teams_events["Man City"][-1]["gameweek"] is None
    assert type(teams_events["Man City"][0]["gameweek"]) == int


def test_get_team_opponents(teams_fixtures, data_object):
    teams_events = create_opponents(
        data_object["teams"], fixtures_uri="https://fantasy.premierleague.com/api/mock/", sort=True
    )
    fixtures = get_team_opponents(teams_events, "Man City", 0, 5)
    assert len(fixtures["opponents"]) == 5
    assert fixtures["postponed"] is True
    assert fixtures["has_double_gw"] is False
    assert fixtures["in_gameweeks"][1] == 0
    assert len(fixtures["in_gameweeks"]) == 5

    fixtures = get_team_opponents(teams_events, "Liverpool", 0, 40)
    assert len(fixtures["opponents"]) == 38
    assert fixtures["postponed"] is False
    assert fixtures["has_double_gw"] is False
    assert fixtures["in_gameweeks"][1] == 1
    assert len(fixtures["in_gameweeks"]) == 38

    teams_events = create_opponents(
        data_object["teams"], fixtures_uri="https://fantasy.premierleague.com/api/mock/"
    )
    fixtures = get_team_opponents(teams_events, "Man City", 0, 5)
    assert len(fixtures["opponents"]) == 5
    assert fixtures["postponed"] is True
    assert fixtures["has_double_gw"] is False
    assert fixtures["in_gameweeks"][1] == 0
    assert len(fixtures["in_gameweeks"]) == 5


def test_add_team_name(data_object):
    add_team_name(data_object["elements"], data_object["teams"])
    team = {i["id"]: i["name"] for i in data_object["teams"]}
    for i in data_object["elements"]:
        assert i["team_name"] == team[i["team"]]


def test_get_gameweek(data_object):
    assert get_game_week(data_object["events"]) == 1
    data_object["events"][0]["is_current"] = False
    data_object["events"][3]["is_current"] = True
    assert get_game_week(data_object["events"]) == 4
    data_object["events"][3]["is_current"] = False
    data_object["events"][0]["is_current"] = False
    assert get_game_week(data_object["events"]) == 0


def test_create_id(data_object):
    data_object["elements"][0]["download_time"] = data_object["download_time"]
    assert len(create_id(data_object["elements"][0])) == 32


def test_add_gw_and_download_time(data_object):
    add_gw_and_download_time(data_object["elements"], data_object["download_time"], 4)
    for i in data_object["elements"][:10]:
        assert i["download_time"] == data_object["download_time"]
        assert i["gameweek"] == 4


def test_add_next_five(data_object, fixtures_object, teams_fixtures):
    all_teams = create_opponents(
        data_object["teams"], fixtures_uri="https://fantasy.premierleague.com/api/mock/"
    )

    data_object["elements"][0]["team_name"] = "Arsenal"
    for i in range(10):
        data_object["elements"][0]["gameweek"] = i
        _add_next_five(data_object["elements"][0], all_teams)
        assert data_object["elements"][0]["n+0_gw"] == i + 1
        assert not data_object["elements"][0]["postponed"]

    data_object["elements"][1]["team_name"] = "Man City"
    data_object["elements"][1]["gameweek"] = 0
    _add_next_five(data_object["elements"][1], all_teams)
    assert data_object["elements"][1]["n+0_gw"] == 1
    assert not data_object["elements"][1]["n+0_opponent"]
    assert data_object["elements"][1]["n+1_opponent"] == "Wolves"
    assert data_object["elements"][1]["postponed"]


def test_add_opponents(data_object, teams_fixtures):
    all_teams = create_opponents(
        data_object["teams"], fixtures_uri="https://fantasy.premierleague.com/api/mock/"
    )
    list(
        map(
            lambda x: x.update({"team_name": "Arsenal", "gameweek": 0}),
            data_object["elements"],
        )
    )
    add_opponents(data_object["elements"], all_teams)

    for i in data_object["elements"][:10]:
        assert "postponed" in i.keys()
        assert "has_double_gw" in i.keys()
        assert "n+0_opponent" in i.keys()
        assert "n+4_opponent" in i.keys()
        assert "n+5_opponent" not in i.keys()


def test_add_unique_id(data_object):
    list(
        map(
            lambda x: x.update({"download_time": data_object["download_time"]}),
            data_object["elements"],
        )
    )
    add_unique_id(data_object["elements"])
    for i in data_object["elements"][:10]:
        assert "player_id" in i.keys()
        assert "id" in i.keys()
        assert len(i["id"]) == 32
