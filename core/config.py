from yaml import safe_load

with open("config.yml") as f:
    _config = safe_load(f)

token = _config["token"]
prefix = _config["prefix"]
postgres_uri = _config["postgres_uri"]

_keys = _config["keys"]
osu_client_id = _keys["osu"]["client_id"]
osu_client_secret = _keys["osu"]["client_secret"]
finnhub_key = _keys["finnhub_key"]
nasa_key = _keys["nasa_key"]
perspective_key = _keys["perspective_key"]
