#!/bin/sh

set -eu

script_dir="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
data_file="$script_dir/../data/diaries.json"

create_label() {
    diary_name="$1"
    label_name="d: $diary_name"

    >&2 echo "Creating label from diary '$diary_name': '$label_name'"
    gh label create "$label_name" --description "Issues relating to the diary $diary_name" --color "#cccccc" --force
}

jq -r '.[]' "$data_file" | while IFS= read -r name; do
    create_label "$name"
done
