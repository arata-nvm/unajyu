import os
import random
import requests

CATEGORIES = {
    "ラーメン屋",
    "ステーキハウス",
    "どんぶり屋",
    "カフェ",
    "うどん屋",
    "和食店",
    "デリ",
    "ファミリーレストラン",
    "洋食レストラン",
    "ドーナツ屋",
    "とんかつ屋",
    "カレーライス店",
    "寿司屋",
}

VENUES = {
    "ココス",
    "ガスト",
    "クラレット",
    "JEWEL OF INDIA",
    "福軒餃子",
    "Starbucks",
    "豚真拉麺 一休 本店",
    "えん弥",
    "つけめん・まぜそば むじゃき",
    "油そば 油虎",
    "桃ちゃん弁当",
    "活龍大衆麺処 真壁屋",
    "銀の豚",
    "活龍",
    "珈琲館",
    "ドルフ",
    "松のや つくば東大通り店",
    "すき家",
    "ジョイフル",
    "清六家",
    "山岡家",
    "七福軒",
    "松屋・マイカリー食堂 つくば西大通り店",
    "はま寿司",
    "吉野家",
    "カレーうどんZEYO.",
    "松屋 つくば東大通店",
    "俺の生きる道W",
}

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
SWARM_TOKEN = os.environ["SWARM_TOKEN"]


def get_activities(marker=""):
    URL = f"https://api.foursquare.com/v2/activities/recent?locale=ja&v=20231107&m=swarm&limit=100&oauth_token={SWARM_TOKEN}"
    if marker:
        URL += f"&beforeMarker={marker}"

    res = requests.get(URL)
    if res.status_code != 200:
        print("[-] failed to get data")
        exit()

    return res.json()["response"]["activities"]


def choice_venues():
    venues = list(VENUES)
    bad_venues = set()

    marker = ""
    weights = [1] * len(venues)
    for _ in range(10):
        activities = get_activities(marker)
        marker = activities["trailingMarker"]

        for item in activities["items"]:
            venue = item["checkin"]["venue"]
            if "city" not in venue["location"] or venue["location"]["city"] != "つくば市":
                continue

            categories = [category["name"] for category in venue["categories"]]
            name = venue["name"]
            if all([category not in CATEGORIES for category in categories]):
                continue

            bad_venues.add(name)

            if name in venues:
                weights[venues.index(name)] *= 0.9
    return (random.choices(venues, weights=weights, k=5), bad_venues)


from discord import Intents, Client, Interaction
from discord.app_commands import CommandTree


class MyClient(Client):
    def __init__(self, intents: Intents) -> None:
        super().__init__(intents=intents)
        self.tree = CommandTree(self)

    async def setup_hook(self) -> None:
        await self.tree.sync()

    async def on_ready(self):
        print(f"login: {self.user.name} [{self.user.id}]")


intents = Intents.default()
client = MyClient(intents=intents)


@client.tree.command()
async def random_unajyu(interaction: Interaction):
    await interaction.response.defer()
    try:
        venues, bad_venues = choice_venues()
    except:
        await interaction.followup.send("error")
        return
    content = "🙆‍♀\n"
    content += "\n".join([f"- {venue}" for venue in venues])
    content += "🙅‍♀\n"
    content += "\n".join([f"- {venue}" for venue in bad_venues])
    await interaction.followup.send(content)


client.run(DISCORD_TOKEN)
