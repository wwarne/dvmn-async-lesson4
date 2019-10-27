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
    """Creates a arg_parser to process command line arguments."""
    parser = argparse.ArgumentParser('Minechat message sender')
    p_group = parser.add_argument_group('Sender settings')
    p_group.add_argument('--host', type=str, help='Chat address', default=os.getenv('MINECHAT_WRITE_HOST', WRITE_HOST))
    p_group.add_argument('--port', type=int, help='Chat port', default=os.getenv('MINECHAT_WRITE_PORT', WRITE_PORT))
    p_group.add_argument('--message', type=str, help='Message to send')
    p_group.add_argument('--verbose', help='Show more information', action='store_true', default=os.getenv('MINECHAT_WRITE_VERBOSE', False))
    exc_group = p_group.add_mutually_exclusive_group()
    exc_group.add_argument('--token', type=str, help='Authorization token', default=os.getenv('MINECHAT_TOKEN') )
    exc_group.add_argument('--username', type=str, help='Your username for register (if token is not set)')
    return parser

def validate_options(properties: argparse.Namespace) -> None:
    """Validate resulting options from argument arg_parser."""
    if not properties.token and not properties.username:
        print('Please specify a token (--token) or a username (--username) key.')
        sys.exit(1)
    if properties.token and not properties.message:
        print('Please specify a message to send (--message)')
        sys.exit(1)


async def submit_message(writer: StreamWriter, message: str) -> None:
    """Send a message to a chat."""
    await write_line_to_chat(writer, message)
    await write_line_to_chat(writer, '')


async def main_sender(host: str, port: int, token: Optional[str], username: Optional[str], message: Optional[str]) -> None:
    """Main logic for a chat sending process."""
    if username:
        async with connect_to_chat(host, port) as (reader, writer):
            try:
                token = await asyncio.wait_for(register(reader, writer, username), 10)
                print(f'Please save this access token: {token}')
            except asyncio.TimeoutError:
                logging.error('Registration failed. Please try again later.')
                return
    if token:
        async with connect_to_chat(host, port) as (reader, writer):
            try:
                auth_result = await asyncio.wait_for(authorise(reader, writer, token), 10)
                if not auth_result:
                    logging.error(f'Authorisation with the token `{token}` has failed.')
                    return
                if message:
                    print(message, end='', flush=True)
                    await asyncio.wait_for(submit_message(writer, message), 10)
                    print(' [✓]')
            except (ConnectionRefusedError, ConnectionError, asyncio.TimeoutError, socket.gaierror):
                print(' [X]')
                logging.error('Error with connection to the server', exc_info=True)

if __name__ == '__main__':

    parser = create_parser()
    options = parser.parse_args()
    validate_options(options)
    logging_level = logging.DEBUG if options.verbose is True else logging.INFO
    logging.basicConfig(format='[%(asctime)s]  %(message)s', datefmt="%d.%m.%Y %H:%M:%S", level=logging_level)
    asyncio.run(main_sender(options.host, options.port, options.token, options.username, options.message))
