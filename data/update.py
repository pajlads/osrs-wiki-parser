from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime

import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Page:
    page: str
    sectiontitle: str | None
    sectionid: int | None
    outputfile: str
    method: str


PAGES: list[Page] = [
    Page(
        page="Optimal_quest_guide",
        sectiontitle="Quests",
        sectionid=None,
        outputfile="data/optimal-quest-guide.json",
        method="table",
    ),
    Page(
        page="Optimal_quest_guide/Ironman",
        sectiontitle="Questing_Order",
        sectionid=None,
        outputfile="data/ironman-optimal-quest-guide.json",
        method="table",
    ),
    Page(
        page="User:Pajlada/Quest_helper",
        sectiontitle=None,
        sectionid=1,
        outputfile="data/free-to-play-quests.json",
        method="list",
    ),
    Page(
        page="User:Pajlada/Quest_helper",
        sectiontitle=None,
        sectionid=2,
        outputfile="data/members-quests.json",
        method="list",
    ),
    Page(
        page="User:Pajlada/Quest_helper",
        sectiontitle=None,
        sectionid=3,
        outputfile="data/miniquests.json",
        method="list",
    ),
]

WIKI_API_URL = "https://oldschool.runescape.wiki/api.php"
USER_AGENT = "hi I'm pajlada on Discord, just doing some stuff for quest helper"


def cell_text(cell: Tag) -> str:
    return " ".join(cell.stripped_strings)


def parse_series(value: str) -> dict[str, int | str | None] | None:
    if value == "N/A":
        return None

    match = re.fullmatch(r"(.+),\s*#([0-9A-Za-z]+)", value)
    if not match:
        return {"name": value.strip()}

    number = match.group(2)

    print(value)

    return {
        "name": match.group(1).strip(),
        "number": number,
    }


def find_quest_table(soup: BeautifulSoup) -> Tag:
    for table in soup.select("table.oqg-table"):
        headers = {cell_text(th).lower() for th in table.select("tr th")}
        if {"name", "difficulty", "length", "series", "release date"}.issubset(headers):
            return table

    raise ValueError("could not find the quest table (table.oqg-table)")


def parse_number(value: str | None) -> int | str | None:
    if value is None:
        return None

    if value.isdigit():
        return int(value)

    return value


def parse_rows(table: Tag) -> list[dict[str, object]]:
    headers = [cell_text(th).strip().lower() for th in table.select("tr th")]
    quests: list[dict[str, object]] = []

    for row in table.select("tr[data-rowid]"):
        cells = row.find_all("td", recursive=False)
        if len(cells) < len(headers):
            raise ValueError(
                f"tr[data-rowid]: got {len(cells)} columns, expected at least {len(headers)}"
            )

        row_data = {
            headers[index]: cell_text(cells[index]) for index in range(len(headers))
        }

        release_date = datetime.strptime(row_data["release date"], "%d %B %Y").date()
        quests.append(
            {
                "number": parse_number(row_data.get("#")),
                "name": row_data["name"],
                "difficulty": row_data["difficulty"],
                "length": row_data["length"],
                "quest_points": int(row_data[""]) if "" in row_data else 0,
                "series": parse_series(row_data["series"]),
                "release_date": release_date.isoformat(),
            }
        )

    return quests


def parse_quests(html) -> list[dict[str, object]]:
    soup = BeautifulSoup(html, "html.parser")
    table = find_quest_table(soup)
    return parse_rows(table)


def main() -> None:
    for page in PAGES:
        print(page)
        params = {
            "action": "parse",
            "page": page.page,
            "prop": "text",
            "disabletoc": 1,
            "disableeditsection": 1,
            "format": "json",
        }
        if page.sectiontitle:
            params["sectiontitle"] = page.sectiontitle
        elif page.sectionid:
            params["section"] = page.sectionid

        data = requests.get(
            WIKI_API_URL,
            headers={
                "User-Agent": USER_AGENT,
            },
            params=params,
        ).json()

        html = data["parse"]["text"]["*"]
        soup = BeautifulSoup(html, "html.parser")

        quests = []

        if page.method == "table":
            quests = []
            for tr in soup.select("table.oqg-table tr[data-rowid]"):
                print(f"tr: {tr}\n")
                first_link = tr.select_one("td a[title]")
                print(f"first link: {first_link}\n\n")
                if not first_link:
                    continue

                if not first_link.parent:
                    continue

                name = (
                    first_link.parent.get_text(strip=False)
                    .replace("Unlock: ", "")
                    .replace(" (miniquest)", "")
                    .strip()
                )

                quests.append(name)
        elif page.method == "list":
            quests = parse_quests(html)

        with open(page.outputfile, "w") as fh:
            fh.write(json.dumps(quests, indent=4))


if __name__ == "__main__":
    main()
