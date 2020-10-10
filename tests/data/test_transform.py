from fpl.data.transformations import create_opponents
from tests.conftest import data_object


def test_teams_fixtures(teams_fixtures, data_object):
    """Test of teams_fixtures."""
    teams_events = create_opponents(
        data_object["teams"], fixtures_uri="https://fantasy.premierleague.com/api/mock/"
    )
    for i in teams_events:
        assert len(teams_events[i]) == 38
        assert len(set(y["team"] for y in teams_events[i])) == 19
    print(teams_events["Man City"])
