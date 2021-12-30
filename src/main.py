import logging
import os
import time


import schedule
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.web import WebClient

from config import STATS_DIR, http_token, socket_token, LOG_DIR, ERROR_LOG_FILE, LOG_FILE
from logger import logger, add_file_logger, add_error_file_logger, add_console_logger
from stats import handle_message, post_stats


def process(client: SocketModeClient, req: SocketModeRequest):
    if req.type == "events_api":
        response = SocketModeResponse(envelope_id=req.envelope_id)
        client.send_socket_mode_response(response)
    if req.payload['event']['type'] == 'message':
        handle_message(req, client)


def create_dirs():
    if not os.path.isdir(LOG_DIR):
        logger.debug(f'Creating log dir in:{LOG_DIR}')
        os.mkdir(LOG_DIR)
        logger.debug('Created')
    else:
        logger.debug(f'LOG_DIR={LOG_DIR}')
    if not os.path.isdir(STATS_DIR):
        logger.debug(f'Creating stats dir in:{STATS_DIR}')
        os.mkdir(STATS_DIR)
        logger.debug('Created')
    else:
        logger.debug(f'STATS_DIR={STATS_DIR}')
    pass


def main():
    add_console_logger(logging.DEBUG)
    logger.info('start')
    create_dirs()
    add_file_logger(LOG_FILE, logging.DEBUG)
    add_error_file_logger(ERROR_LOG_FILE)
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
