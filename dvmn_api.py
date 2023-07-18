import logging
import time

import requests
import telegram
from environs import Env

env = Env()
env.read_env()
DVMN_LONGPOLLING_URL = 'https://dvmn.org/api/long_polling/'


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_token: str, chat_id: int):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = telegram.Bot(token=tg_token)

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def get_code_review(token: str, timestamp: float, timeout: int = 120):
    headers = {'Authorization': f'Token {token}'}
    params = {'timestamp': timestamp}
    print(timestamp)
    response = requests.get(url=DVMN_LONGPOLLING_URL, headers=headers, data=params, timeout=timeout)
    print(response.status_code)
    print(response.request)
    print(response.json())
    return response.json()


def review_notification(info_review: dict):
    lesson_reviewed = f'Преподователь проверил урок {info_review["lesson_title"]}'
    lesson_url = info_review['lesson_url']
    if info_review['is_negative']:
        review_result = 'Работа не принята, требуется доработки'
    else:
        review_result = 'Работа принята, можно приступать к следующему уроку'
    return f'{lesson_reviewed}\n{lesson_url}\n{review_result}'


def run_long_polling(dvmn_token: str, error_timeout: int, logger: logging.Logger):
    # timestamp = time.time()
    timestamp = 1689366779.004384
    error_message = (
        f'An error has occured. Will try again in {error_timeout} seconds...'
    )
    while True:
        try:
            review = get_code_review(dvmn_token, timestamp, error_timeout)
            print(review)
        except (
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectTimeout
        ):
            logger.error(error_message)
            time.sleep(error_timeout)
            continue
        if review['status'] == 'timeout':
            timestamp = review['timestamp_to_request']
            print(timestamp)
        elif review['status'] == 'found':
            timestamp = review['last_attempt_timestamp']
            notification = review_notification(review["new_attempts"][0])
            logger.info(notification)


#
if __name__ == '__main__':
    dvmn_token = env.str('DVMN_TOKEN')
    error_timeout = env.int('ERROR_TIMEOUT')
    telegram_token = env.str('TELEGRAM_TOKEN')
    user_chat_id = env.str('TELEGRAM_CHAT_ID')
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('Logger')
    logger.addHandler(
        TelegramLogsHandler(tg_token=telegram_token, chat_id=user_chat_id)
    )

    run_long_polling(dvmn_token, error_timeout, logger=logger)
