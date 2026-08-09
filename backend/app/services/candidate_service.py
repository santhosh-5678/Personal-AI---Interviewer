import json
from pathlib import Path


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "candidates.json"
)


def load_candidates():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


def get_candidate(candidate_id: str):

    data = load_candidates()

    # candidates.json contains:
    # {
    #     "candidates": [...]
    # }
    candidates = data["candidates"]

    for candidate in candidates:

        member = candidate.get("member", {})

        if member.get("id") == candidate_id:
            return candidate

    return None