# Fantasy Premier League 2020/2021

Basert på følgende tutorial:
https://towardsdatascience.com/fantasy-premier-league-value-analysis-python-tutorial-using-the-fpl-api-8031edfe9910
Oppsett

### Getting started

Repoet baserer seg på python3 og jupyter med jupytext for smidig versjonskontroll.

```bash
git clone https://github.com/martgra/fpl2021.git
cd fpl2021
python3 -m venv venv
source venv/bin/activate
pip install -r requirements
```



### Datasett
Datasettet fra Fantasy finnes på følgende link.
https://fantasy.premierleague.com/api/bootstrap-static/

Per nå lastes det ned hver 6. time og lagres som et "snapshot" med format
```
%Y-%m-%dT%H:%M:%SZ_data.json
```

Tilgang til disse dataene krever "connection string" som fåes av repo-eier. Brukes sammen med modulen azure_storage.py
```python
# Last ned nåværende data
python fpl/azure_storage.py
```


API - andre nyttige metoder

* Kampprogram: https://fantasy.premierleague.com/api/fixtures/
* Et lags historie: https://fantasy.premierleague.com/api/entry/{}/history/
* Et bestemt lags score i år: https://fantasy.premierleague.com/api/entry/{team-id}/
* Score i en bestemt "classic"-liga: https://fantasy.premierleague.com/api/leagues-classic/{league-id}/standings/
* Score i bestemt "H2H"-liga: https://fantasy.premierleague.com/api/leagues-h2h/{league-id}/standings/
* Siste transfers: https://fantasy.premierleague.com/api/entry/{team-id}/transfers-latest/
* My Team https://fantasy.premierleague.com/api/my-team/{team-id}/ *

*For å bruke "my team api" er autentikasjon påkrevd se link
https://medium.com/@bram.vanherle1/fantasy-premier-league-api-authentication-guide-2f7aeb2382e4)

### Andre nyttige lenker

* Reddit-tråd om FPL API
    https://www.reddit.com/r/FantasyPL/comments/c64rrx/fpl_api_url_has_been_changed/
* Blogpost om FPL API (her må man bytte ut drf med api)
    https://medium.com/@YourMumSaysWhat/how-to-get-data-from-the-fantasy-premier-league-api-4477d6a334c3
* Historiske data for FPL
    https://github.com/vaastav/Fantasy-Premier-League


### Time series

<div class="flourish-embed flourish-bar-chart-race" data-src="visualisation/3314375" data-url="https://flo.uri.sh/visualisation/3314375/embed" aria-label=""><script src="https://public.flourish.studio/resources/embed.js"></script></div>