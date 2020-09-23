import hashlib


def get_game_week(data_dump):
    try:
        return list(filter(lambda x: x["is_current"] == True, data_dump))[0]["id"]
    except:
        return 0


def create_id(document):
    return hashlib.md5(str(document["code"]).encode("utf-8") + str(document["download_time"]).encode("utf-8")).hexdigest()


def add_gw_and_download_time(elements, download_time, gameweek):
    list(map(lambda x: x.update(
        {
            "download_time": download_time,
            "gameweek": gameweek
        }), elements))


def add_unique_id(elements):
    list(map(lambda x: x.update(
        {"player_id": x.pop("id")}), elements))
    list(map(lambda x: x.update(
        {"id": create_id(x)}), elements))
