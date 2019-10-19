import logging
import asyncio
import socket
from contextlib import asynccontextmanager
from typing import Tuple
from asyncio.streams import StreamReader, StreamWriter


async def open_chat_connection(host: str,
                               port: int,
                               attempts: int = 2,
                               delay: int = 3) -> Tuple[StreamReader, StreamWriter]:
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
async def connect_to_chat(host: str,
                          port: int,
                          attempts: int = 2,
                          delay: int = 3) -> Tuple[StreamReader, StreamWriter]:
    """
    Контекстный менеджер, возвращающий reader&writer к чату

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
    data = await reader.readline()
    try:
        msg = data.decode(encoding='utf-8').strip()
    except (SyntaxError, UnicodeDecodeError):
        logging.error('Получено ошибочное сообщение', exc_info=True)
        return ''
    logging.debug(f'Получили строку {msg}')
    return msg
