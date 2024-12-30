import requests
from bs4 import BeautifulSoup, Comment, Tag

FILES = [
    (
        "https://oldschool.runescape.wiki/w/Optimal_quest_guide",
        "data/optimal-quest-guide.html",
    ),
    (
        "https://oldschool.runescape.wiki/w/Quests/List",
        "data/quest-list.html",
    ),
    (
        "https://oldschool.runescape.wiki/w/Optimal_quest_guide/Ironman",
        "data/ironman-optimal-quest-guide.html",
    ),
]

USER_AGENT = "hi I'm pajlada on Discord, just doing some stuff for quest helper"


def main() -> None:
    for url, output_path in FILES:
        r = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
            },
        )
        with open(output_path, "w") as fh:
            data = BeautifulSoup(r.text, "html.parser")
            for comment in data.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            inner_content = data.find("div", attrs={"id": "mw-content-text"})
            assert isinstance(inner_content, Tag)
            print(f"Writing '{url}' to '{output_path}'")
            fh.write(inner_content.prettify())


if __name__ == "__main__":
    main()
