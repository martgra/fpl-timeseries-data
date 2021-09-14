import requests
from bs4 import BeautifulSoup
import random

from requests.api import head
def get_points(season_url):

    soup = _get_soup(season_url)

    table = soup.find_all(id="page_competition_1_block_competition_tables_13_block_competition_league_table_1_table")[0]

    teams=[]

    for i in table.find_all("tr"):
        try:
            team = i.find("td",{"class": "text team large-link"})
            points = i.find("td",{"class": "number points"})
            teams.append((team.text, points.text))
        except:
            pass

    return teams


def _get_soup(url):
    UAS = ("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1", 
        "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
        )


    ua = UAS[random.randrange(len(UAS))]

    headers = {'user-agent': ua}


    content = requests.get(url, headers=headers).content
    return BeautifulSoup(content, features="html.parser")


def get_value(value_url):
    content = _get_soup(value_url)

    table =  content.find_all(id="yw1")[0]

    team_values = []
    for i in table.find_all("tr"):
        try:
            team_name = i.find("td", {"class": "hauptlink no-border-links"}).text
            team_pre_value = i.find("td", {"class": "rechts"}).text.split("m")[0].split("€")[-1]
            team_current_value = i.find("td", {"class": "rechts hauptlink"}).text.split("m")[0].split("€")[-1]
            team_current_value = team_current_value.split("bn")[0]
            team_pre_value = team_pre_value.split("bn")[0]
            team_values.append((team_name, float(team_current_value), float(team_pre_value)))
        except:
            pass

    return sorted(team_values)



url = "https://www.transfermarkt.com/premier-league/marktwerteverein/wettbewerb/GB1/plus/1?stichtag=2019-01-01"

teams = get_value(url)
print(len(teams))

for i in teams:
    print(i[2])


# teams_2022 = get_points("https://nr.soccerway.com/national/england/premier-league/20212022/regular-season/r63396/")
# teams_2021 = get_points("https://nr.soccerway.com/national/england/premier-league/20172018/regular-season/r41547/")

# teams_2021_dict = {i[0]: i[1] for i in teams_2021}

# teams_22 = [i[0] for i in teams_2022]

# for i in sorted(teams_22):
#     print(teams_2021_dict.get(i))