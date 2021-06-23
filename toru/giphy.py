import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()
_GIPHY_KEY = os.getenv("GIPHY_KEY")
_rating = "g"


def get_gif(tag: str = "") -> str:
    tag.replace(" ", "+")

    r = requests.get(
        "https://api.giphy.com/v1/gifs/random?api_key=%s&tag=%s&rating=%s"
        % (_GIPHY_KEY, tag, _rating)
    )

    if r.status_code == 200:
        cat_gif = json.loads(r.content)
        res = cat_gif["data"]["embed_url"]
        return res
    else:
        return "no gif for u"


def cat_gif() -> str:
    return get_gif("cat")
