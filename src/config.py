import os

socket_token = os.getenv('SLACK_SOCKET_TOKEN')
http_token = os.getenv("SLACK_HTTP_TOKEN")

BASE_DIR = os.getcwd()
print(f'BASE_DIR={BASE_DIR}')
STATS_DIR = f'{BASE_DIR}/stats'
LOG_DIR = f'{BASE_DIR}/logs'
LOG_FILE = f'{LOG_DIR}/wykop-taktyk.log'
ERROR_LOG_FILE = f'{LOG_DIR}/wykop-taktyk-errors.log'