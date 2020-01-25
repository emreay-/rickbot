import os
import re
import logging

import certifi
import ssl as ssl_lib
from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter

from rick import RickBot

app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(
    os.environ["SLACK_SIGNING_SECRET"], "/slack/events", app)
slack_web_client = WebClient(token=os.environ['BOT_USER_ACCESS_TOKEN'])


@slack_events_adapter.on("message")
def message(payload):

    def _post_message(message):
        print(message)
        slack_web_client.chat_postMessage(**message)

    RickBot(_post_message).respond_to_message(payload)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    app.run(port=3000)
