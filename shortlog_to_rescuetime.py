from __future__ import annotations

import argparse
from collections import UserString
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys
from typing import List

import keyring
import requests


class ShortDescription(UserString):
    """A string shortened to at most 255 characters."""

    def __init__(self, description):
        self.data = description[:255]


@dataclass
class Highlight:
    date: datetime
    description: ShortDescription


@dataclass
class ApiResponse:
    message: str


def main(api_key: str, shortlog_directory: Path, date: datetime) -> None:
    try:
        log_lines = read_shortlog_lines(shortlog_directory, date)
    except FileNotFoundError:
        print(
            f"Could not find shortlog file for {date:%Y-%m-%d} in {shortlog_directory}",
            file=sys.stderr,
        )
        return

    highlights = parse_log_lines(log_lines)
    for h in highlights:
        try:
            # print(h)
            response = post_highlight(h, api_key)
            print(f"{response.message} ({h.description})")
        except requests.HTTPError as exc:
            print(f"Encountered HTTPError for highlight {h}")
            print(exc)


def read_shortlog_lines(shortlog_directory: Path, date: datetime) -> List[str]:
    log_file = shortlog_directory.joinpath(f"shortlog-{date:%Y-%m-%d}.txt")
    return [line for line in log_file.read_text().splitlines() if line]


def parse_log_lines(lines: List[str]) -> List[Highlight]:
    return [
        Highlight(
            date=datetime.strptime(date, "%Y-%m-%d %H:%M:%S"),
            description=ShortDescription(description),
        )
        for date, description in [line.split(" | ") for line in lines]
    ]


def post_highlight(highlight: Highlight, api_key=str) -> ApiResponse:
    api_url = "https://www.rescuetime.com/anapi/highlights_post"
    response = requests.post(
        url=api_url,
        params={
            "key": api_key,
            "highlight_date": highlight.date.strftime("%Y-%m-%d"),
            # Call str on the description because requests seems to
            # otherwise only use the last character.
            "description": str(highlight.description),
        },
    )
    response.raise_for_status()
    return ApiResponse(message=response.json()["message"])


if __name__ == "__main__":
    yesterday = (datetime.today() - timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("username", type=str)
    parser.add_argument("directory", type=Path)
    parser.add_argument(
        "--date",
        type=lambda d: datetime.strptime(d, "%Y-%m-%d"),
        default=yesterday,
        required=False,
    )
    args = parser.parse_args(sys.argv[1:])

    api_key = keyring.get_password(service_name="rescuetime", username=args.username)
    main(api_key, shortlog_directory=args.directory, date=args.date)
