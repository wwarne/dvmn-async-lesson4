import argparse
import asyncio
import logging
import os
from datetime import datetime
from typing import AsyncIterator

from aiofile import AIOFile

from common_tools import read_line_from_chat, connect_to_chat

READ_HOST = 'minechat.dvmn.org'
READ_PORT = 5000
HISTORY_PATH = 'minechat.history'


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser('Minechat client')
    g = parser.add_argument_group('Chat reader settings')
    g.add_argument('--host', type=str, help='Chat address', default=os.getenv('MINECHAT_READ_HOST', READ_HOST))
    g.add_argument('--port', type=int, help='Chat port', default=os.getenv('MINECHAT_READ_PORT', READ_PORT))
    g.add_argument('--history', metavar='FILEPATH', type=str, help='Path to a history file',
                   default=os.getenv('MINECHAT_HISTORY_PATH', HISTORY_PATH))
    return parser


async def chat_messages_stream(host: str, port: int) -> AsyncIterator[str]:
    while True:
        async with connect_to_chat(host, port) as (reader, writer):
            while True:
                try:
                    new_msg = await asyncio.wait_for(read_line_from_chat(reader), timeout=60)
                    """
                    Then remote server is falling down, readline() starts to return an empty bytestring - b''
                    so read_line_from_chat returns an empty string
                    """
                    if not new_msg:
                        logging.info('Получено пустое сообщение. Обычно такое бывает из-за обрыва соединения.')
                        break
                    yield new_msg
                except asyncio.TimeoutError:
                    logging.info('Долго не было сообщений в чате. Переподключимся')
                    break


async def chat_spy(host: str, port: int, history: str) -> None:
    async with AIOFile(history, 'a', encoding='utf-8') as afp:
        async for msg in chat_messages_stream(host, port):
            current_datetime = datetime.now().strftime('%d.%m.%y %H:%M')
            line = f'[{current_datetime}] {msg}\n'
            print(line, end='')
            await afp.write(line)


if __name__ == '__main__':
    parser = create_parser()
    options = parser.parse_args()
    asyncio.run(chat_spy(options.host, options.port, options.history))