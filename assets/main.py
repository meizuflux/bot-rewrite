import requests
from urllib.request import urlretrieve
import time
import shutil
import sys

category = sys.argv[1]
url = "https://api.waifu.pics/many/sfw/" + category
print("url: ", url)
json = {"exclude": []}


data = requests.post(url, json=json).json()
print(data)
for i in data["files"]:
    fn = i.split("https://i.waifu.pics/")[1]
    response = requests.get(i, stream=True)
    time.sleep(0.6)
    with open("D:/coding/bot-rewrite/assets/" + category + "/" + fn, "wb") as out_file:
        shutil.copyfileobj(response.raw, out_file)
