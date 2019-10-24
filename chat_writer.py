import argparse
import asyncio
import logging
import os
import socket
import sys
from asyncio.streams import StreamWriter
from typing import Optional
from common_tools import (
    authorise,
    connect_to_chat,
    register,
    write_line_to_chat,
)

WRITE_HOST = 'minechat.dvmn.org'
WRITE_PORT = 5050


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser('Minechat message sender')
    g = parser.add_argument_group('Sender settings')
    g.add_argument('--host', type=str, help='Chat address', default=os.getenv('MINECHAT_WRITE_HOST', WRITE_HOST))
    g.add_argument('--port', type=int, help='Chat port', default=os.getenv('MINECHAT_WRITE_PORT', WRITE_PORT))
    g.add_argument('--message', type=str, help='Message to send')
    group = g.add_mutually_exclusive_group()
    group.add_argument('--token', type=str, help='Authorization token', )
    group.add_argument('--username', type=str, help='Your username for register (if token is not set)')
    return parser

def validate_options(properties: argparse.Namespace) -> None:
    if not properties.token and not properties.username:
        print('Нужно указать или токен доступа или имя пользователя для регистрации')
        sys.exit(1)
    if properties.token and not properties.message:
        print('Укажите сообщение для отправки в чат (--message)')
        sys.exit(1)


async def submit_message(writer: StreamWriter, message: str) -> None:
    """Отправляет сообщение в чат"""
    await write_line_to_chat(writer, message)
    await write_line_to_chat(writer, '')


async def main_sender(host: str, port: int, token: Optional[str], username: Optional[str], message: Optional[str]) -> None:
    """Отправка сообщения"""
    if username:
        async with connect_to_chat(host, port) as (reader, writer):
            try:
                token = await asyncio.wait_for(register(reader, writer, username), 10)
                print(f'Сохраните ваш токен для доступа в чат {token}')
            except asyncio.TimeoutError:
                logging.error('Не удалось зарегистрироваться, попробуйте позднее')
                return
    if token:
        async with connect_to_chat(host, port) as (reader, writer):
            try:
                auth_result = await asyncio.wait_for(authorise(reader, writer, token), 10)
                if not auth_result:
                    logging.error(f'Не удалось авторизоваться с токеном {token}')
                    return
                if message:
                    await asyncio.wait_for(submit_message(writer, message), 10)
            except (ConnectionRefusedError, ConnectionError, asyncio.TimeoutError, socket.gaierror):
                logging.error('Ошибка при отправке соединения', exc_info=True)

if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s]  %(message)s', datefmt="%d.%m.%Y %H:%M:%S", level=logging.DEBUG)
    parser = create_parser()
    options = parser.parse_args()
    validate_options(options)

    asyncio.run(main_sender(options.host, options.port, options.token, options.username, options.message))
