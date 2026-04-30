# usage: uv run main.py | xclip (or equivalent)
# this will print a list of quests in release date order
# the idea is for this to be expanded to other quest orders

import datetime
import json
import logging
import sys
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from operator import attrgetter

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(message)s",
)
log = logging.getLogger(__name__)

UNIMPLEMENTED_QUESTS = (
    "The Frozen Door",
    "Into the Tombs",
)

UNIMPLEMENTED_BUT_NO_INTENTION_TO_ADD_QUESTS = ("Learning the Ropes",)

QUEST_HELPER_CUSTOM_ORDER = [
    "Balloon transport system to Crafting Guild",
    "Balloon transport system to Grand Tree",
    "Balloon transport system to Varrock",
    "Balloon transport system to Castle Wars",
    "In Search of Knowledge",  # For the ironman order
    "Hopespear's Will",  # For the ironman order
    "Barbarian Training",
    "Bear Your Soul",
    "The Enchanted Key",
    "Family Pest",
    "Mage Arena I",
    "Mage Arena II",
    "All Easy Achievement Diaries",
    "All Medium Achievement Diaries",
    "All Hard Achievement Diaries",
    "All Elite Achievement Diaries",
]


class DCJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)

        if isinstance(o, datetime.datetime):
            return o.isoformat()

        return super().default(o)


def clean_quest_name(quest_name: str) -> str:
    return (
        quest_name.upper()
        .replace(
            "KOUREND & KEBOS", "KOUREND"
        )  # for achievement diaries, should be removed
        .replace(
            "WESTERN PROVINCES", "WESTERN"
        )  # for achievement diaries, should be removed
        .replace(" DIARY", "")  # for achievement diaries, should be removed
        .replace(" (MINIQUEST)", "")
        .replace(" ", "_")
        .replace("'", "")
        .replace("&", "")
        .replace(".", "")
        .replace("!", "")
        .replace("-", "")
        .replace("Unlock: ", "")
    )


class QuestType(int, Enum):
    FREE_TO_PLAY_QUEST = 1
    MEMBERS_QUEST = 2
    MINI_QUEST = 3
    ACHIEVEMENT_DIARY = 4

    # e.g. Stronghold of Security
    CUSTOM_QUEST = 5

    BALLOON_UNLOCK = 5


@dataclass
class Quest:
    quest_type: QuestType

    # e.g. 100
    number: int | None

    # e.g. 1 for RFD subquests
    subnumber: int | None

    # e.g. "Cook's Assistant"
    name: str

    # e.g. "Novice"
    difficulty: str

    # e.g. "Very Short"
    length: str

    quest_points: int

    # e.g. "Demon Slayer"
    series: str | None

    release_date: datetime.datetime

    optimal_order: int = -1

    optimal_ironman_order: int = -1

    qh_order: int = -1

    # Can be used to sort quests that have the same number in the above-set order list
    sub_order: int = 100

    # Can be used to sort quests that have the same number in the above-set order list
    ironman_sub_order: int = 100

    diary_difficulty: str = ""
    diary_region: str = ""

    def load_order(
        self,
        optimal_quest_order: list[str],
        ironman_optimal_quest_order: list[str],
        custom_name: str | None = None,
    ):
        name = custom_name or self.name

        if self.qh_order == -1:
            try:
                self.qh_order = QUEST_HELPER_CUSTOM_ORDER.index(name)
            except ValueError:
                pass

        if self.optimal_order == -1:
            try:
                self.optimal_order = optimal_quest_order.index(name)
            except ValueError:
                pass

        if self.optimal_ironman_order == -1:
            try:
                self.optimal_ironman_order = ironman_optimal_quest_order.index(name)
            except ValueError:
                pass

        if custom_name is None:
            if self.quest_type == QuestType.ACHIEVEMENT_DIARY:
                match self.diary_region:
                    case "Lumbridge":
                        # to handle
                        self.load_order(
                            optimal_quest_order,
                            ironman_optimal_quest_order,
                            f"{self.diary_difficulty} Lumbridge & Draynor Diary",
                        )

                self.load_order(
                    optimal_quest_order,
                    ironman_optimal_quest_order,
                    f"All {self.diary_difficulty} Achievement Diaries",
                )

            # Some quest names in the ironman guide are weird, try to handle them here
            match name:
                case "Recipe for Disaster/Another Cook's Quest":
                    self.load_order(
                        optimal_quest_order,
                        ironman_optimal_quest_order,
                        "Recipe for Disaster: Another Cook's quest",
                    )
                case "Recipe for Disaster/Freeing the Goblin generals":
                    self.load_order(
                        optimal_quest_order,
                        ironman_optimal_quest_order,
                        "Recipe for Disaster: Goblin generals",
                    )
                case "Recipe for Disaster/Freeing the Mountain Dwarf":
                    self.load_order(
                        optimal_quest_order,
                        ironman_optimal_quest_order,
                        "Recipe for Disaster: Dwarf",
                    )
                case "Recipe for Disaster/Freeing Evil Dave":
                    self.load_order(
                        optimal_quest_order,
                        ironman_optimal_quest_order,
                        "Recipe for Disaster: Evil Dave",
                    )
                case "Recipe for Disaster/Freeing Pirate Pete":
                    self.load_order(
                        optimal_quest_order,
                        ironman_optimal_quest_order,
                        "Recipe for Disaster: Pirate Pete",
                    )
                case "Recipe for Disaster/Freeing the Lumbridge Guide":
                    self.load_order(
                        optimal_quest_order,
                        ironman_optimal_quest_order,
                        "Recipe for Disaster: Lumbridge Guide",
                    )
                case "Recipe for Disaster/Freeing Skrach Uglogwee":
                    self.load_order(
                        optimal_quest_order,
                        ironman_optimal_quest_order,
                        "Recipe for Disaster: Skrach Uglogwee",
                    )
                case "Recipe for Disaster/Freeing Sir Amik Varze":
                    self.load_order(
                        optimal_quest_order,
                        ironman_optimal_quest_order,
                        "Recipe for Disaster: Sir Amik Varze",
                    )
                case "Recipe for Disaster/Freeing King Awowogei":
                    self.load_order(
                        optimal_quest_order,
                        ironman_optimal_quest_order,
                        "Recipe for Disaster: Awowogei",
                    )
                case "Recipe for Disaster/Defeating the Culinaromancer":
                    self.load_order(
                        optimal_quest_order,
                        ironman_optimal_quest_order,
                        "Recipe for Disaster: Defeating the Culinaromancer",
                    )
                case "Stronghold of Security":
                    # Stronghold of Security is not explicitly part of the ironman wiki order
                    # It's mentioned during the Romeo & Juliet step, so we put it under it
                    if self.optimal_ironman_order == -1:
                        self.optimal_ironman_order = ironman_optimal_quest_order.index(
                            "Romeo & Juliet"
                        )
                        self.ironman_sub_order = 110
                case "Meat and Greet":
                    # Meat and Greet is not explicitly part of the ironman wiki order
                    # We put it under Cabin Fever which is the same order it has in the normal wiki order
                    if self.optimal_ironman_order == -1:
                        self.optimal_ironman_order = ironman_optimal_quest_order.index(
                            "Cabin Fever"
                        )
                        self.ironman_sub_order = 110
                case "Death on the Isle":
                    # Death on the Isle is not explicitly part of the ironman wiki order
                    # We put it under The Feud which is the same order it has in the normal wiki order
                    if self.optimal_ironman_order == -1:
                        self.optimal_ironman_order = ironman_optimal_quest_order.index(
                            "The Feud"
                        )
                        self.ironman_sub_order = 110
                case "His Faithful Servants":
                    # His Faithful Servants is not explicitly part of the ironman wiki order
                    # We put it under The General's Shadow which is the same order it has in the normal wiki order
                    if self.optimal_ironman_order == -1:
                        self.optimal_ironman_order = ironman_optimal_quest_order.index(
                            "The General's Shadow"
                        )
                        self.ironman_sub_order = 110
                case "Ethically Acquired Antiquities":
                    # Ethically Acquired Antiquities is not explicitly part of the ironman wiki order
                    # We put it under Monkey Madness I which is the same order it has in the normal wiki order
                    if self.optimal_ironman_order == -1:
                        self.optimal_ironman_order = ironman_optimal_quest_order.index(
                            "Monkey Madness I"
                        )
                        self.ironman_sub_order = 110
                case "The Curse of Arrav":
                    # The Curse of Arrav is not explicitly part of the ironman wiki order
                    # We put it under Dragon Slayer II which is the same order it has in the normal wiki order
                    if self.optimal_ironman_order == -1:
                        self.optimal_ironman_order = ironman_optimal_quest_order.index(
                            "Dragon Slayer II"
                        )
                        self.ironman_sub_order = 110
                case "In Search of Knowledge":
                    # In Search of Knowledge is not explicitly part of the ironman wiki order
                    # We put it under Sins of the Father which is the same order it has in the normal wiki order
                    if self.optimal_ironman_order == -1:
                        self.optimal_ironman_order = ironman_optimal_quest_order.index(
                            "The Corsair Curse"
                        )
                        self.ironman_sub_order = 110
                case "Hopespear's Will":
                    # Hopespear's Will is not explicitly part of the ironman wiki order
                    # We put it under In Search of Knowledge which is the same order it has in the normal wiki order
                    if self.optimal_ironman_order == -1:
                        self.optimal_ironman_order = ironman_optimal_quest_order.index(
                            "The Corsair Curse"
                        )
                        self.ironman_sub_order = 120

    def quest_helper_enum_values(self) -> list[str]:
        if self.name in UNIMPLEMENTED_QUESTS:
            return [
                f"//QuestHelperQuest.{clean_quest_name(self.name)}, - Placeholder for future addition."
            ]

        if self.name in UNIMPLEMENTED_BUT_NO_INTENTION_TO_ADD_QUESTS:
            return [
                f"//QuestHelperQuest.{clean_quest_name(self.name)}, - Quest we are unlikely to add a helper for."
            ]

        if self.quest_type == QuestType.BALLOON_UNLOCK:
            return [
                f"QuestHelperQuest.{clean_quest_name(self.name.replace('system to ', ''))}",
            ]

        if self.quest_type == QuestType.ACHIEVEMENT_DIARY:
            # TODO: Fix this to just align with osrs wiki naming?

            if "Easy" in self.name:
                return [
                    f"QuestHelperQuest.{clean_quest_name(self.name.replace('Easy ', ''))}_EASY",
                ]
            elif "Medium" in self.name:
                return [
                    f"QuestHelperQuest.{clean_quest_name(self.name.replace('Medium ', ''))}_MEDIUM",
                ]
            elif "Hard" in self.name:
                return [
                    f"QuestHelperQuest.{clean_quest_name(self.name.replace('Hard ', ''))}_HARD",
                ]
            elif "Elite" in self.name:
                return [
                    f"QuestHelperQuest.{clean_quest_name(self.name.replace('Elite ', ''))}_ELITE",
                ]
            else:
                assert f"unhandled achievement diary difficulty for {self.name}"

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


def load_quests(
    path: str,
    quest_type: QuestType,
    optimal_quest_order: list[str],
    ironman_optimal_quest_order: list[str],
) -> list[Quest]:
    quests: list[Quest] = []

    with open(path) as fh:
        payload = json.loads(fh.read())
        for p in payload:
            number = p["number"]
            subnumber = None
            if isinstance(number, str):
                parts = number.split(".", 1)
                number = int(parts[0])
                subnumber = int(parts[1])

            q = Quest(
                quest_type,
                number,
                subnumber,
                p["name"],
                p["difficulty"],
                p["length"],
                p["quest_points"],
                p["series"],
                datetime.datetime.strptime(p["release_date"], "%Y-%m-%d"),
            )

            q.load_order(optimal_quest_order, ironman_optimal_quest_order)
            quests.append(q)

    return quests


def custom_quest(
    name: str,
    release_date: datetime.datetime,
    optimal_quest_order: list[str],
    ironman_optimal_quest_order: list[str],
) -> Quest:
    q = Quest(
        QuestType.CUSTOM_QUEST,
        None,
        None,
        name,
        "N/A",
        "N/A",
        0,
        None,
        release_date,
    )

    q.load_order(optimal_quest_order, ironman_optimal_quest_order)

    return q


def balloon_unlock(
    name: str,
    release_date: datetime.datetime,
    optimal_quest_order: list[str],
    ironman_optimal_quest_order: list[str],
) -> Quest:
    q = Quest(
        QuestType.BALLOON_UNLOCK,
        None,
        None,
        name,
        "N/A",
        "N/A",
        0,
        None,
        release_date,
    )

    q.load_order(optimal_quest_order, ironman_optimal_quest_order)

    return q


def diary(
    difficulty: str,
    region: str,
    release_date: datetime.datetime,
    optimal_quest_order: list[str],
    ironman_optimal_quest_order: list[str],
) -> Quest:
    name = f"{difficulty} {region} Diary"

    q = Quest(
        QuestType.ACHIEVEMENT_DIARY,
        None,
        None,
        name,
        "N/A",
        "N/A",
        0,
        None,
        release_date,
        diary_region=region,
        diary_difficulty=difficulty,
    )

    q.load_order(optimal_quest_order, ironman_optimal_quest_order)

    return q


def load_quest_list(
    optimal_quest_order: list[str],
    ironman_optimal_quest_order: list[str],
) -> list[Quest]:
    DIARY_DIFFICULTIES = ["Easy", "Medium", "Hard", "Elite"]
    DIARIES = [
        ("Ardougne", datetime.datetime(2015, 3, 5)),
        ("Desert", datetime.datetime(2015, 3, 5)),
        ("Falador", datetime.datetime(2015, 3, 5)),
        ("Fremennik", datetime.datetime(2015, 3, 5)),
        ("Kandarin", datetime.datetime(2015, 3, 5)),
        ("Karamja", datetime.datetime(2007, 5, 8)),  # this is not entirely correct
        ("Kourend & Kebos", datetime.datetime(2019, 1, 10)),
        ("Lumbridge", datetime.datetime(2015, 3, 5)),
        ("Morytania", datetime.datetime(2015, 3, 5)),
        ("Varrock", datetime.datetime(2015, 3, 5)),
        ("Western Provinces", datetime.datetime(2015, 3, 5)),
        ("Wilderness", datetime.datetime(2015, 3, 5)),
    ]

    custom_quests = [
        custom_quest(
            "Stronghold of Security",
            datetime.datetime(2006, 7, 4),
            optimal_quest_order,
            ironman_optimal_quest_order,
        ),
        custom_quest(
            "Knight Waves Training Grounds",
            datetime.datetime(2007, 7, 24),
            optimal_quest_order,
            ironman_optimal_quest_order,
        ),
        balloon_unlock(
            "Balloon transport system to Crafting Guild",
            datetime.datetime(2006, 11, 6),
            optimal_quest_order,
            ironman_optimal_quest_order,
        ),
        balloon_unlock(
            "Balloon transport system to Varrock",
            datetime.datetime(2006, 11, 6),
            optimal_quest_order,
            ironman_optimal_quest_order,
        ),
        balloon_unlock(
            "Balloon transport system to Castle Wars",
            datetime.datetime(2006, 11, 6),
            optimal_quest_order,
            ironman_optimal_quest_order,
        ),
        balloon_unlock(
            "Balloon transport system to Grand Tree",
            datetime.datetime(2006, 11, 6),
            optimal_quest_order,
            ironman_optimal_quest_order,
        ),
    ]
    for difficulty in DIARY_DIFFICULTIES:
        for region, release_date in DIARIES:
            custom_quests.append(
                diary(
                    difficulty,
                    region,
                    release_date,
                    optimal_quest_order,
                    ironman_optimal_quest_order,
                )
            )

    f2p_quests = load_quests(
        "data/free-to-play-quests.json",
        QuestType.FREE_TO_PLAY_QUEST,
        optimal_quest_order,
        ironman_optimal_quest_order,
    )
    members_quests = load_quests(
        "data/members-quests.json",
        QuestType.MEMBERS_QUEST,
        optimal_quest_order,
        ironman_optimal_quest_order,
    )
    mini_quests = load_quests(
        "data/miniquests.json",
        QuestType.MINI_QUEST,
        optimal_quest_order,
        ironman_optimal_quest_order,
    )

    return custom_quests + f2p_quests + members_quests + mini_quests


def load_optimal_quest_order() -> list[str]:
    with open("data/optimal-quest-guide.json") as fh:
        return json.load(fh)


def load_ironman_optimal_quest_order() -> list[str]:
    with open("data/ironman-optimal-quest-guide.json") as fh:
        return json.load(fh)


def sort_by_release_date(quest: Quest):
    return (
        quest.release_date,
        quest.number or -1,
        quest.subnumber or -1,
        quest.name,
    )


def print_quest_order_by_release_date(quests: list[Quest]) -> None:
    body = ""

    body += "\t\t// Quests\n"
    for quest in filter(
        lambda q: (
            q.quest_type in (QuestType.FREE_TO_PLAY_QUEST, QuestType.MEMBERS_QUEST)
        ),
        sorted(quests, key=sort_by_release_date),
    ):
        quest_enums = quest.quest_helper_enum_values()
        for s in quest_enums:
            if s.strip().startswith("//"):
                body += f"\t\t{s}\n"
            else:
                body += f"\t\t{s},\n"

    body += "\t\t// Miniquests\n"
    for quest in filter(
        lambda q: q.quest_type == QuestType.MINI_QUEST,
        sorted(quests, key=sort_by_release_date),
    ):
        quest_enums = quest.quest_helper_enum_values()
        for s in quest_enums:
            if s.strip().startswith("//"):
                body += f"\t\t{s}\n"
            else:
                body += f"\t\t{s},\n"

    print(body.strip().rstrip(","))


def print_quests_enum_by_optimal_order(quests: list[Quest]) -> None:
    body = ""

    for quest in filter(
        lambda q: q.optimal_order > -1,
        sorted(quests, key=attrgetter("optimal_order", "sub_order")),
    ):
        quest_enums = quest.quest_helper_enum_values()
        for s in quest_enums:
            if s.strip().startswith("//"):
                body += f"\t\t{s}\n"
            else:
                body += f"\t\t{s},\n"

    unordered_quests = list(
        filter(
            lambda q: q.optimal_order == -1,
            sorted(quests, key=attrgetter("qh_order", "name")),
        )
    )
    if len(unordered_quests) > 0:
        body += "\t\t// Quests & mini quests that are not part of the OSRS Wiki's Optimal Quest Guide\n"

        for quest in unordered_quests:
            quest_enums = quest.quest_helper_enum_values()
            for s in quest_enums:
                if s.strip().startswith("//"):
                    continue
                else:
                    body += f"\t\t{s},\n"
                    # body += f"\t\t// {quest.qh_order} ({quest.name}),\n"

    print(body.strip().rstrip(","))


def print_quests_enum_by_ironman_optimal_order(quests: list[Quest]) -> None:
    body = ""

    for quest in filter(
        lambda q: q.optimal_ironman_order > -1,
        sorted(quests, key=attrgetter("optimal_ironman_order", "ironman_sub_order")),
    ):
        quest_enums = quest.quest_helper_enum_values()
        for s in quest_enums:
            if s.strip().startswith("//"):
                body += f"\t\t{s}\n"
            else:
                body += f"\t\t{s},\n"

            # body += f"\t\t// {quest.optimal_ironman_order} | {quest.qh_order} ({quest.name}),\n"

    unordered_quests = list(
        filter(
            lambda q: q.optimal_ironman_order == -1,
            sorted(quests, key=attrgetter("qh_order", "name")),
        )
    )
    if len(unordered_quests) > 0:
        body += "\t\t// Quests & mini quests that are not part of the OSRS Wiki's Optimal Ironman Quest Guide\n"

        for quest in unordered_quests:
            quest_enums = quest.quest_helper_enum_values()
            for s in quest_enums:
                if s.strip().startswith("//"):
                    continue
                else:
                    body += f"\t\t{s},\n"
                    # body += f"\t\t// {quest.qh_order} ({quest.name}),\n"

    print(body.strip().rstrip(","))


def main() -> None:
    COMMANDS = [
        "quests-by-release-date",
        "quests-by-optimal-order",
        "ironman-quests-by-optimal-order",
        "quests",
    ]

    command = "quests-by-release-date"
    if len(sys.argv) >= 2:
        command = sys.argv[1]

    optimal_quest_order = load_optimal_quest_order()
    ironman_optimal_quest_order = load_ironman_optimal_quest_order()
    quests = load_quest_list(optimal_quest_order, ironman_optimal_quest_order)

    match command:
        case "quests-by-release-date":
            SUBCOMMANDS = [
                "enum",
            ]
            subcommand = "enum"
            if len(sys.argv) >= 3:
                subcommand = sys.argv[2]

            match subcommand:
                case "enum":
                    print_quest_order_by_release_date(quests)
                case other:
                    log.warning(
                        f"Unknown subcommand '{other}'. Available subcommands: {', '.join(SUBCOMMANDS)}"
                    )

        case "quests-by-optimal-order":
            log.info(
                "Outputting optimal quest order - see OptimalQuestGuide.java in Quest Helper",
            )
            SUBCOMMANDS = [
                "enum",
            ]
            subcommand = "enum"
            if len(sys.argv) >= 3:
                subcommand = sys.argv[2]

            match subcommand:
                case "enum":
                    print_quests_enum_by_optimal_order(quests)
                case other:
                    log.warning(
                        f"Unknown subcommand '{other}'. Available subcommands: {', '.join(SUBCOMMANDS)}"
                    )

        case "ironman-quests-by-optimal-order":
            log.info(
                "Outputting optimal ironman quest order - see IronmanOptimalQuestGuide.java in Quest Helper",
            )
            SUBCOMMANDS = [
                "enum",
            ]
            subcommand = "enum"
            if len(sys.argv) >= 3:
                subcommand = sys.argv[2]

            match subcommand:
                case "enum":
                    print_quests_enum_by_ironman_optimal_order(quests)
                case other:
                    log.warning(
                        f"Unknown subcommand '{other}'. Available subcommands: {', '.join(SUBCOMMANDS)}"
                    )

        case "quests":
            print(json.dumps(quests, cls=DCJSONEncoder))

        case other:
            log.info(
                f"Unknown command '{other}'. Available commands: {', '.join(COMMANDS)}"
            )


if __name__ == "__main__":
    main()
