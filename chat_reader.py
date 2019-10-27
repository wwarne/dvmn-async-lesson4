import argparse
import asyncio
import logging
import os
from datetime import datetime
from typing import AsyncIterator

from aiofile import AIOFile

from common_tools import connect_to_chat, read_line_from_chat

READ_HOST = 'minechat.dvmn.org'
READ_PORT = 5000
HISTORY_PATH = 'minechat.history'


def create_parser() -> argparse.ArgumentParser:
    """Creates a arg_parser to process command line arguments."""
    parser = argparse.ArgumentParser('Minechat client')
    p_group = parser.add_argument_group('Chat reader settings')
    p_group.add_argument('--host', type=str, help='Chat address', default=os.getenv('MINECHAT_READ_HOST', READ_HOST))
    p_group.add_argument('--port', type=int, help='Chat port', default=os.getenv('MINECHAT_READ_PORT', READ_PORT))
    p_group.add_argument(
        '--history',
        metavar='FILEPATH',
        type=str, help='Path to a history file',
        default=os.getenv('MINECHAT_HISTORY_PATH', HISTORY_PATH),
    )
    p_group.add_argument(
        '--verbose',
        help='Show more information',
        action='store_true',
        default=os.getenv('MINECHAT_READ_VERBOSE', False),
    )
    return parser


async def chat_messages_stream(host: str, port: int) -> AsyncIterator[str]:
    """Reads messages from chat and yields it one by one."""
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
                        logging.info('Got an empty message. Usually it happens because of connection problems.')
                        break
                    yield new_msg
                except asyncio.TimeoutError:
                    logging.info('There were no messages for a long time. Reconnecting to a chat.')
                    break


async def chat_spy(host: str, port: int, history: str) -> None:
    """Connect to a chat to see new messages and save them all to a file."""
    async with AIOFile(history, 'a', encoding='utf-8') as afp:
        async for msg in chat_messages_stream(host, port):
            current_datetime = datetime.now().strftime('%d.%m.%y %H:%M')
            line = f'[{current_datetime}] {msg}\n'
            print(line, end='')
            await afp.write(line)


if __name__ == '__main__':
    arg_parser = create_parser()
    options = arg_parser.parse_args()
    logging_level = logging.DEBUG if options.verbose is True else logging.INFO
    logging.basicConfig(format='[%(asctime)s]  %(message)s', datefmt="%d.%m.%Y %H:%M:%S", level=logging_level)
    try:
        asyncio.run(chat_spy(options.host, options.port, options.history))
    except KeyboardInterrupt:
        pass
