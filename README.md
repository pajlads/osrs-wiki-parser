# osrs-wiki-parser

This project is intended to be used with the RuneLite Quest Helper plugin, to ensure we use the wiki-created optimal quest guide, and use their data for things like release dates. No `wiki-is-wrong` label.

## Usage

### Updating data from wiki

```python3
uv run data/update.py
```

### Get quest list by release date

```python3
uv run main.py quests-by-release-date
```

### Get quest list ordered by OSRS wiki's Optimal Quest Guide

```python3
uv run main.py quests-by-optimal-guide
```
