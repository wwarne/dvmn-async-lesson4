import asyncio
import json
import logging
import socket
from asyncio.streams import StreamReader, StreamWriter
from contextlib import asynccontextmanager
from typing import Optional, Tuple


async def open_chat_connection(
    host: str,
    port: int,
    attempts: int = 2,
    delay: int = 3,
) -> Tuple[StreamReader, StreamWriter]:
    """
    Устанавливает соединение с сервером чата.

    При неудачной попытке соединения пробует переподключиться.

    :param host: Адрес сервера
    :param port: Порт сервера
    :param attempts: Количество попыток соединения перед увеличением задержки перед повторным соединением
    :param delay: Задержка перед повторным соединением, сек.
    """
    total_attempts = 0
    while True:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=60,
            )
            logging.info('Установлено соединение с сервером чата')
            return reader, writer
        except (ConnectionRefusedError, asyncio.TimeoutError, socket.gaierror):
            if total_attempts < attempts:
                logging.error('Нет соединения, повторная попытка')
                total_attempts += 1
            else:
                logging.error(f'Нет соединения. Повторная попытка через {delay} сек.')
                await asyncio.sleep(delay)


@asynccontextmanager
async def connect_to_chat(
    host: str,
    port: int,
    attempts: int = 2,
    delay: int = 3,
) -> Tuple[StreamReader, StreamWriter]:
    """
    Контекстный менеджер, возвращающий reader&writer к чату.

    :param host: Адрес сервера
    :param port: Порт сервера
    :param attempts:  Количество попыток соединения перед увеличением задержки перед повторным соединением
    :param delay: Задержка перед повторным соединением, сек.
    """
    reader, writer = None, None
    try:
        logging.info('Пытаемся подключиться к серверу чата')
        reader, writer = await open_chat_connection(host, port, attempts, delay)
        yield reader, writer
    finally:
        logging.info('Закрываем соединение с чатом')
        if writer:
            writer.close()
            await writer.wait_closed()


async def read_line_from_chat(reader: StreamReader) -> str:
    """Получает байтовую строку и переводит её в обычную."""
    chat_data = await reader.readline()
    try:
        return chat_data.decode(encoding='utf-8').strip()
    except (SyntaxError, UnicodeDecodeError):
        logging.error('Получено ошибочное сообщение', exc_info=True)
        return ''


def sanitize_message(message: str) -> str:
    """
    Очищает сообщение от символов переноса строки.

    В протоколе взаимодействия с сервером знак переноса строки \n обозначает конец сообщения.
    """
    return message.replace('\r', '').replace('\n', ' ').strip()


async def write_line_to_chat(writer: StreamWriter, message: str) -> None:
    """Кодирует и отправляет строку в путешествие в сторону чата."""
    message = sanitize_message(message).encode(encoding='utf-8') + b'\n'
    writer.write(message)
    await writer.drain()
    logging.debug(f'Отправили сообщение {message}')


async def authorise(reader: StreamReader, writer: StreamWriter, token: str) -> Optional[str]:
    """Процесс авторизации пользователя в чате."""
    logging.debug('Пробуем авторизоваться')
    greetings = await read_line_from_chat(reader)
    logging.debug(f'Приветствие чата: {greetings}')
    await write_line_to_chat(writer, token)
    response = await read_line_from_chat(reader)
    response = json.loads(response)
    if not response:
        logging.error('Неправильный токен или сервер не работает')
        return None
    logging.debug(response)
    logging.debug(f'Авторизован в чате как {response.get("nickname")}')
    return response.get('nickname')


async def register(reader: StreamReader, writer: StreamWriter, nickname: str) -> str:
    """Регистрация нового пользователя в чате."""
    logging.debug('Пробуем зарегистрироваться')
    greetings = await read_line_from_chat(reader)
    logging.debug(f'Приветствие чата: {greetings}')
    await write_line_to_chat(writer, '')  # говорим, что у нас нет токена
    ask_for_nickname = await read_line_from_chat(reader)
    logging.debug(f'Предложение выбрать свой никнейм: {ask_for_nickname}')
    await write_line_to_chat(writer, nickname)
    response_content = await read_line_from_chat(reader)
    if not response_content:
        logging.error('Не удалось зарегистрироваться, попробуйте позднее')
        return ''
    response = json.loads(response_content)
    logging.debug(response)
    logging.debug(f'Зарегистрирован как {response.get("nickname")}')
    logging.debug(f'Новый токен {response.get("account_hash")}')
    return response.get('account_hash')
