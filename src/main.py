import logging
import os
import time

import schedule
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.web import WebClient

logger = logging.getLogger('dp-stats')
logger.setLevel(logging.DEBUG)

socket_token = os.getenv('SLACK_SOCKET_TOKEN')
http_token = os.getenv("SLACK_HTTP_TOKEN")
stats_channel_id = 'C028X1XUVKN'

top_n = 3
channels = {}
users = {}


def post_stats(client: SocketModeClient):
    sorted_channels = {k: v for k, v in sorted(channels.items(), key=lambda item: item[1])}
    message = "--------------\n"
    message += "last hour\n"
    for channel_id, number in list(sorted_channels.items())[-top_n:].__reversed__():
        channel_name = client.web_client.conversations_info(channel=channel_id)['channel']['name']
        message += f'{channel_name}: {number}\n'
    client.web_client.chat_postMessage(channel=stats_channel_id, text=message)
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


def process(client: SocketModeClient, req: SocketModeRequest):
    if req.type == "events_api":
        response = SocketModeResponse(envelope_id=req.envelope_id)
        client.send_socket_mode_response(response)
    if req.payload['event']['type'] == 'message':
        message = req.payload['event']['text']
        channel_id = req.payload['event']['channel']
        user_id = req.payload['event']['user']
        if channel_id != stats_channel_id:
            new_message(user_id, channel_id)
            channel_name = client.web_client.conversations_info(channel=channel_id)['channel']['name']
            user_name = client.web_client.users_info(user=user_id)['user']['profile']['display_name']
            logger.info(f'[{channel_name}] {user_name}: {message}')


def add_console_logger(level):
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def main():
    add_console_logger(logging.DEBUG)
    logger.info('start')
    web_client = WebClient(token=http_token)
    socket_client = SocketModeClient(
        app_token=socket_token,
        web_client=web_client,
    )
    socket_client.socket_mode_request_listeners.append(process)
    socket_client.connect()
    schedule.every(1).hours.do(lambda: post_stats(socket_client))

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
