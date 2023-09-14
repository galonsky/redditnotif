import logging
import sys

from discord.client import DiscordClient
from reddit.client import RedditClient


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()


if __name__ == '__main__':
    client = RedditClient()
    comments = list(client.get_new_comments())
    logger.info(f"Found {len(comments)} comments")
    discord_client = DiscordClient()
    discord_client.post_message(reversed(comments))