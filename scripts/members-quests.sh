#!/bin/sh

set -eu

script_dir="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
data_file="$script_dir/../data/members-quests.json"

create_label() {
    quest_name="$1"
    case "$quest_name" in
        Recipe\ for\ Disaster/*)
            quest_name="RFD: ${quest_name#Recipe for Disaster/}"
            ;;
        Recipe\ for\ Disaster)
            >&2 echo "Skipping quest with exact name 'Recipe for Disaster'"
            return
            ;;
    esac

    case "$quest_name" in
        */*)
            >&2 echo "Refusing to create label for quest with '/': '$quest_name'"
            exit 1
            ;;
    esac

    label_name="q: $quest_name"

    >&2 echo "Creating label from quest '$quest_name': '$label_name'"
    gh label create "$label_name" --description "Issues relating to the members quest $quest_name" --color "#cccccc" --force
}

jq -r '.[].name' "$data_file" | while IFS= read -r name; do
    create_label "$name"
done
