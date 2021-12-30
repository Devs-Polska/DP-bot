import csv

from slack_sdk.socket_mode import SocketModeClient

from config import STATS_DIR
from logger import logger
from datetime import date

top_n = 5
channels = {}
users = {}
stats_channel_id = 'C028X1XUVKN'


def post_stats(client: SocketModeClient):
    sorted_channels = {k: v for k, v in sorted(channels.items(), key=lambda item: item[1])}
    message_lines = ["--------------", "last hour"]
    for channel_id, number in list(sorted_channels.items())[-top_n:].__reversed__():
        channel_name = client.web_client.conversations_info(channel=channel_id)['channel']['name']
        message_lines.append(f'{channel_name}: {number}')

    if len(message_lines) == 2:
        message_lines = ["--------------", "no messages in last hour"]

    client.web_client.chat_postMessage(channel=stats_channel_id, text="\n".join(message_lines))
    logger.info(message_lines)
    channels.clear()
    users.clear()


def new_message(user, channel):
    if channel in channels:
        channels[channel] += 1
    else:
        channels[channel] = 1
    if user in users:
        users[user] += 1
    else:
        users[user] = 1


def save_message(timestamp, user_id, channel_id):
    file_name = date.fromtimestamp(1628147197)
    path = f'{STATS_DIR}/{file_name}'
    with open(path, "a+") as f:
        csv.writer(f).writerow([timestamp, user_id, channel_id])


def handle_message(req, client):
    message = req.payload['event']['text']
    channel_id = req.payload['event']['channel']
    user_id = req.payload['event']['user']
    timestamp = req.payload['event_time']
    if channel_id != stats_channel_id:
        new_message(user_id, channel_id)
        channel_name = client.web_client.conversations_info(channel=channel_id)['channel']['name']
        user_name = client.web_client.users_info(user=user_id)['user']['profile']['display_name']
        save_message(timestamp, user_id, channel_id)
        logger.debug(f'[{channel_name}] {user_name}: {message}')
