import logging
import time

import requests
import telegram
from environs import Env

DVMN_LONGPOLLING_URL = 'https://dvmn.org/api/long_polling/'

logger = logging.getLogger('Logger')
logging.basicConfig(format="%(process)d %(levelname)s %(message)s")

start_bot = 'Бот запущен'


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_token: str, chat_id: int):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def get_code_review(token: str, timestamp: float, timeout: int = 120):
    headers = {'Authorization': f'Token {token}'}
    params = {'timestamp': timestamp}
    response = requests.get(url=DVMN_LONGPOLLING_URL, headers=headers, data=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def create_review_notification(info_review: dict):
    lesson_reviewed = f'Преподователь проверил урок {info_review["lesson_title"]}'
    lesson_url = info_review['lesson_url']
    if info_review['is_negative']:
        review_result = 'Работа не принята, требуется доработки'
    else:
        review_result = 'Работа принята, можно приступать к следующему уроку'
    return f'{lesson_reviewed}\n{lesson_url}\n{review_result}'


def run_long_polling(dvmn_token: str, error_timeout: int, logger: logging.Logger):
    timestamp = time.time()
    error_message = (
        f'An error has occured. Will try again in {error_timeout} seconds...'
    )
    while True:
        try:
            try:
                review = get_code_review(dvmn_token, timestamp, error_timeout)
            except requests.exceptions.ReadTimeout:
                continue
            except (
                    requests.exceptions.HTTPError,
                    requests.RequestException
            ):
                logger.error(error_message)
                time.sleep(error_timeout)
                continue

            if review['status'] == 'timeout':
                timestamp = review['timestamp_to_request']
            elif review['status'] == 'found':
                timestamp = review['last_attempt_timestamp']
                notification = create_review_notification(review["new_attempts"][0])
                bot.send_message(chat_id=user_chat_id, text=notification)
        except:
            logging.exception("Бот упал с ошибкой:")


if __name__ == '__main__':
    env = Env()
    env.read_env()
    dvmn_token = env.str('DVMN_TOKEN')
    error_timeout = env.int('ERROR_TIMEOUT')
    telegram_token = env.str('TELEGRAM_TOKEN')
    user_chat_id = env.str('TELEGRAM_CHAT_ID')
    bot = telegram.Bot(token=telegram_token)
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)
    logger.addHandler(
        TelegramLogsHandler(bot, chat_id=user_chat_id)
    )
    logger.info(start_bot)
    run_long_polling(dvmn_token, error_timeout, logger=logger)
