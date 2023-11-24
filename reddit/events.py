from os import getenv

from common.event_bus import EventHandler
from reddit.client import RedditClient


class NewPostEventHandler(EventHandler):
    def handle(self, payload: dict) -> None:
        client = RedditClient()
        new_post_id = payload["new_post_id"]
        old_post_id = payload["old_post_id"]
        content = f"New daily thread is posted [here](https://www.reddit.com{getenv('SUBREDDIT')}/comments/{new_post_id})"
        client.post_comment(old_post_id, content)