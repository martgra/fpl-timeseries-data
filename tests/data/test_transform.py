from fpl import data
from fpl.data.transformations import add_team_name, create_opponents, get_team_opponents


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
