import itertools
from datetime import datetime, timezone
from os import getenv
from typing import Iterable, Iterator, TypeVar

import requests

from reddit.structs import Comment


T = TypeVar("T")


def grouper(iterator: Iterator[T], n: int) -> Iterator[list[T]]:
    while chunk := list(itertools.islice(iterator, n)):
        yield chunk


class DiscordClient:

    def _build_request(self, comments: Iterable[Comment]) -> dict:
        return {
            "embeds": [
                {
                    "author": {
                        "name": comment.author,
                        "icon_url": comment.author_icon,
                    },
                    "description": comment.body,
                    "timestamp": datetime.fromtimestamp(comment.timestamp, tz=timezone.utc).isoformat()
                } for comment in comments
            ]
        }

    def post_message(self, comments: Iterable[Comment]):
        for comments in grouper(iter(comments), 10):
            response = requests.post(getenv("DISCORD_WEBHOOK_URL"), json=self._build_request(comments))
            print(response.status_code)
            print(response.text)