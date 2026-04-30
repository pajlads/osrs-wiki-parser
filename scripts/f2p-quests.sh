#!/bin/sh

set -eu

script_dir="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
data_file="$script_dir/../data/free-to-play-quests.json"

create_label() {
    quest_name="$1"
    label_name="q: $quest_name"

    >&2 echo "Creating label from quest '$quest_name': '$label_name'"
    gh label create "$label_name" --description "Issues relating to the F2P quest $quest_name" --color "#cccccc" --force
}

jq -r '.[].name' "$data_file" | while IFS= read -r name; do
    create_label "$name"
done
