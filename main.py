import logging
import sys

from common.event_bus import event_bus, NEW_POST_TOPIC
from discord.client import DiscordClient
from reddit.client import RedditClient
from reddit.events import NewPostEventHandler

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()


if __name__ == '__main__':
    event_bus.subscribe(NEW_POST_TOPIC, NewPostEventHandler())

    client = RedditClient()
    comments = list(client.get_new_comments())
    logger.info(f"Found {len(comments)} comments")
    discord_client = DiscordClient()
    discord_client.post_message(reversed(comments))

    event_bus.consume()