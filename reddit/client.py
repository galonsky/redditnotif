import itertools
import logging
from datetime import datetime, timedelta
from os import getenv
from typing import Optional, Generator
from zoneinfo import ZoneInfo

import redis
import requests
from requests import Response
from requests.auth import HTTPBasicAuth

from reddit.exceptions import PostNotFoundError
from reddit.structs import Comment


USER_AGENT = "redditnotif/1.0"
MAX_COMMENTS_PER_FETCH = 30
NEW_POST_HOURS_BEFORE_MIDNIGHT = getenv("NEW_POST_HOURS_BEFORE_MIDNIGHT", 1)


r = redis.Redis(host=getenv("REDIS_HOST"), port=6379, decode_responses=True)


logger = logging.getLogger()


class RedditClient:
    def __init__(self):
        self.access_token = r.get("access_token")
        if not self.access_token:
            self.access_token = self._get_new_access_token()

    def _get_new_access_token(self) -> str:
        logger.info("Fetching new access token")
        client_auth = HTTPBasicAuth(getenv("REDDIT_CLIENT_TOKEN"), getenv("REDDIT_CLIENT_SECRET"))
        post_data = {"grant_type": "password", "username": getenv("REDDIT_USERNAME"), "password": getenv("REDDIT_PASSWORD")}
        headers = {"User-Agent": USER_AGENT}
        response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
        token_dict = response.json()
        token = token_dict["access_token"]
        expires_in = token_dict["expires_in"]
        r.set("access_token", token, ex=expires_in - 60 * 10)
        logger.info("Fetched new access token")
        return token

    def _get_with_auth(self, url: str) -> Response:
        headers = {
            "Authorization": f"bearer {self.access_token}",
            "User-Agent": USER_AGENT
        }
        return requests.get(url, headers=headers)

    def _get_author_icon(self, comment: dict) -> Optional[str]:
        try:
            return comment["author_flair_richtext"][0]["u"]
        except (KeyError, IndexError):
            return None

    def get_todays_post_id(self) -> str:
        today_str = (
                datetime.now(tz=ZoneInfo("America/New_York")) +
                timedelta(hours=NEW_POST_HOURS_BEFORE_MIDNIGHT)
        ).strftime("%m/%d/%Y")
        cached = r.get(f"postid.{today_str}")
        if cached:
            return cached

        logger.info("Fetching today's post")
        response = self._get_with_auth(f"https://oauth.reddit.com{getenv('SUBREDDIT')}/new.json?limit=2")
        posts = [child['data'] for child in response.json()["data"]["children"]]

        posts_today = [post for post in posts if today_str in post["title"]]
        if not posts_today:
            raise PostNotFoundError
        r.set(f"postid.{today_str}", posts_today[0]["id"], ex=60 * 60 * 25)
        return posts_today[0]["id"]

    def get_new_comments(self) -> Generator[Comment, None, None]:
        post_id = self.get_todays_post_id()
        response = self._get_with_auth(f"https://oauth.reddit.com{getenv('SUBREDDIT')}/comments/{post_id}?depth=1")
        comments = [child["data"] for child in response.json()[1]["data"]["children"]]
        ids_to_add = set()
        for comment in itertools.islice(comments, MAX_COMMENTS_PER_FETCH):
            if r.sismember(f"commentids.{post_id}", comment["id"]):
                break
            ids_to_add.add(comment["id"])
            yield Comment(
                id=comment["id"],
                author=comment["author"],
                body=comment["body"],
                author_icon=self._get_author_icon(comment),
                timestamp=comment["created_utc"],
            )
        if ids_to_add:
            r.sadd(f"commentids.{post_id}", *ids_to_add)
            r.expire(f"commentids.{post_id}", 60 * 60 * 25)
