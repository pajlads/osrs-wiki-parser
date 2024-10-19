# usage: uv run main.py | xclip (or equivalent)
# this will print a list of quests in release date order
# the idea is for this to be expanded to other quest orders

from dataclasses import dataclass
from functools import cmp_to_key
from typing import Optional
from operator import attrgetter

import datetime

from bs4 import BeautifulSoup, NavigableString, Tag
import re

UNIMPLEMENTED_QUESTS = ("The Frozen Door", "Into the Tombs")


def clean_quest_name(quest_name: str) -> str:
    return (
        quest_name.upper()
        .replace(" ", "_")
        .replace("'", "")
        .replace("&", "")
        .replace(".", "")
        .replace("!", "")
        .replace("-", "")
    )


def find_wiki_table(name: str):
    def is_wiki_table(tag: Tag) -> bool:
        # print(f"Tag: {tag}")
        if tag.name != "table":
            return False
        if "wikitable" not in tag.attrs["class"]:
            return False
        headers = [tag.text.strip().lower() for tag in tag.find_all("th")]
        if "name" not in headers or "release date" not in headers:
            return False
        section = tag.find_previous("span", attrs={"class": "mw-headline"})
        if section is None:
            return False
        return section.text.lower() == name.lower()

    return is_wiki_table


@dataclass
class Quest:
    # e.g. 100
    number: Optional[int]

    # e.g. 1 for RFD subquests
    subnumber: Optional[int]

    # e.g. "Cook's Assistant"
    name: str

    # e.g. "Novice"
    difficulty: str

    # e.g. "Very Short"
    length: str

    quest_points: Optional[int]

    # e.g. "Demon Slayer"
    series: Optional[str]

    release_date_str: str
    release_date: datetime.datetime

    def quest_helper_enum_values(self) -> list[str]:
        if self.name in UNIMPLEMENTED_QUESTS:
            return [
                f"//QuestHelperQuest.{clean_quest_name(self.name)}, - Placeholder for future addition."
            ]

        if self.name == "Shield of Arrav":
            return [
                "QuestHelperQuest.SHIELD_OF_ARRAV_BLACK_ARM_GANG",
                "QuestHelperQuest.SHIELD_OF_ARRAV_PHOENIX_GANG",
            ]

        if self.name == "Desert Treasure I":
            return [
                "QuestHelperQuest.DESERT_TREASURE",
            ]

        if self.name == "Recipe for Disaster":
            return []

        if self.name == "Recipe for Disaster/Another Cook's Quest":
            return [
                "QuestHelperQuest.RECIPE_FOR_DISASTER_START",
            ]

        if self.name == "Recipe for Disaster/Freeing the Mountain Dwarf":
            return [
                "QuestHelperQuest.RECIPE_FOR_DISASTER_DWARF",
            ]

        if self.name == "Recipe for Disaster/Freeing the Goblin generals":
            return [
                "QuestHelperQuest.RECIPE_FOR_DISASTER_WARTFACE_AND_BENTNOZE",
            ]

        if self.name == "Recipe for Disaster/Freeing Pirate Pete":
            return [
                "QuestHelperQuest.RECIPE_FOR_DISASTER_PIRATE_PETE",
            ]

        if self.name == "Recipe for Disaster/Freeing the Lumbridge Guide":
            return [
                "QuestHelperQuest.RECIPE_FOR_DISASTER_LUMBRIDGE_GUIDE",
            ]

        if self.name == "Recipe for Disaster/Freeing Evil Dave":
            return [
                "QuestHelperQuest.RECIPE_FOR_DISASTER_EVIL_DAVE",
            ]

        if self.name == "Recipe for Disaster/Freeing King Awowogei":
            return [
                "QuestHelperQuest.RECIPE_FOR_DISASTER_MONKEY_AMBASSADOR",
            ]

        if self.name == "Recipe for Disaster/Freeing Sir Amik Varze":
            return [
                "QuestHelperQuest.RECIPE_FOR_DISASTER_SIR_AMIK_VARZE",
            ]

        if self.name == "Recipe for Disaster/Freeing Skrach Uglogwee":
            return [
                "QuestHelperQuest.RECIPE_FOR_DISASTER_SKRACH_UGLOGWEE",
            ]

        if self.name == "Recipe for Disaster/Defeating the Culinaromancer":
            return [
                "QuestHelperQuest.RECIPE_FOR_DISASTER_FINALE",
            ]

        if self.name == "Desert Treasure II - The Fallen Empire":
            return [
                "QuestHelperQuest.DESERT_TREASURE_II",
            ]

        if self.name == "Perilous Moons":
            # TODO: This should probably be fixed
            return [
                "QuestHelperQuest.PERILOUS_MOON",
            ]

        if self.name == "Mage Arena I":
            # TODO: This should probably be fixed
            return [
                "QuestHelperQuest.THE_MAGE_ARENA",
            ]

        if self.name == "Mage Arena II":
            # TODO: This should probably be fixed
            return [
                "QuestHelperQuest.THE_MAGE_ARENA_II",
            ]

        if self.name == "The Enchanted Key":
            # TODO: This should probably be fixed
            return [
                "QuestHelperQuest.ENCHANTED_KEY",
            ]

        return [f"QuestHelperQuest.{clean_quest_name(self.name)}"]


def get_quests(quest_table: Tag | NavigableString | None) -> list[Quest]:
    assert isinstance(quest_table, Tag)

    quests: list[Quest] = []

    headers = [tag.text.strip().lower() for tag in quest_table.find_all("th")]
    for row in quest_table.find_all("tr"):
        assert isinstance(row, Tag)

        data = row.find_all("td")
        if not data:
            # skip header / empty rows
            continue

        quest_data = {}
        for i in range(0, len(data)):
            quest_data[headers[i]] = re.sub(
                r" +", " ", data[i].text.strip().replace("\n", "")
            )

        series = quest_data["series"] or "N/A"
        number_str = quest_data.get("#", None)
        number: Optional[int] = None
        subnumber: Optional[int] = None
        if number_str is not None:
            if "." in number_str:
                parts = number_str.split(".", 1)
                number = int(parts[0])
                subnumber = int(parts[1])
            else:
                number = int(number_str)

        quest_points = 0
        if "" in quest_data:
            quest_points = int(quest_data[""])

        release_date_str = quest_data["release date"]
        release_date = datetime.datetime.strptime(release_date_str, "%d %B %Y")

        quests.append(
            Quest(
                number,
                subnumber,
                quest_data["name"],
                quest_data["difficulty"],
                quest_data["length"],
                quest_points,
                None if series == "N/A" else series,
                release_date_str,
                release_date,
            )
        )

    return quests


def sort_by_release_date(quest: Quest):
    return (
        quest.release_date,
        quest.number or -1,
        quest.subnumber or -1,
        quest.name,
    )


def print_quest_order_by_release_date(
    f2pQuests: list[Quest], membersQuests: list[Quest], miniQuests: list[Quest]
) -> None:
    body = ""
    body += "\t\t// Quests\n"
    for quest in sorted(f2pQuests + membersQuests, key=sort_by_release_date):
        quest_enums = quest.quest_helper_enum_values()
        for s in quest_enums:
            if s.strip().startswith("//"):
                body += f"\t\t{s}\n"
            else:
                body += f"\t\t{s},\n"
    body += "\t\t// Miniquests\n"
    for quest in sorted(miniQuests, key=sort_by_release_date):
        quest_enums = quest.quest_helper_enum_values()
        for s in quest_enums:
            if s.strip().startswith("//"):
                body += f"\t\t{s}\n"
            else:
                body += f"\t\t{s},\n"

    print(body.strip().rstrip(","))


def main() -> None:
    with open("data/quest-list.html", "r") as fh:
        html = "".join(fh.readlines())
    data = BeautifulSoup(html, "html.parser")

    f2pQuests = get_quests(data.find(find_wiki_table("Free-to-play quests")))
    membersQuests = get_quests(data.find(find_wiki_table("Members' Quests")))
    miniQuests = get_quests(data.find(find_wiki_table("Miniquests")))

    print_quest_order_by_release_date(f2pQuests, membersQuests, miniQuests)


if __name__ == "__main__":
    main()
