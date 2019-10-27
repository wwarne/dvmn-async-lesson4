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
    Establish connection with a chat server.

    It will try to reconnect after failing attempt.

    :param host: Chat server address
    :param port: Chat server port
    :param attempts: How many times to try before using delays
    :param delay: Delay before retry, seconds.
    """
    total_attempts = 0
    while True:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=60,
            )
            logging.info(f'Connection to the chat server {host}:{port} has been established.')
            return reader, writer
        except (ConnectionRefusedError, asyncio.TimeoutError, socket.gaierror):
            if total_attempts < attempts:
                logging.error('Connection error, retrying...')
                total_attempts += 1
            else:
                logging.error(f'Connection error. Retrying after {delay} sec.')
                await asyncio.sleep(delay)


@asynccontextmanager
async def connect_to_chat(
    host: str,
    port: int,
    attempts: int = 2,
    delay: int = 3,
) -> Tuple[StreamReader, StreamWriter]:
    """
    Context manager to provide reader&writer from chat connection.

    :param host: Chat server address
    :param port: Chat server port
    :param attempts:  How many times to try before using delays
    :param delay: Delay before retry, seconds
    """
    reader, writer = None, None
    try:
        logging.info('Trying to connect to the server.')
        reader, writer = await open_chat_connection(host, port, attempts, delay)
        yield reader, writer
    finally:
        logging.info('Closing connection to the server')
        if writer:
            writer.close()
            await writer.wait_closed()


async def read_line_from_chat(reader: StreamReader) -> str:
    """Grabs bytes string from connection and decode it into text."""
    chat_data = await reader.readline()
    try:
        return chat_data.decode(encoding='utf-8').strip()
    except (SyntaxError, UnicodeDecodeError):
        logging.error('Got message that can not be decoded', exc_info=True)
        return ''


def sanitize_message(message: str) -> str:
    r"""
    Clears message from `new line` symbols.

    new line symbol (`\\n`) means an end of the message as stated in chat protocol specification.
    """
    return message.replace('\r', '').replace('\n', ' ').strip()


async def write_line_to_chat(writer: StreamWriter, message: str) -> None:
    """Encode message and send it to the server."""
    message = sanitize_message(message).encode(encoding='utf-8') + b'\n'
    writer.write(message)
    await writer.drain()
    logging.debug(f'Send a message: {message}')


async def authorise(reader: StreamReader, writer: StreamWriter, token: str) -> Optional[str]:
    """Authorisation process."""
    logging.debug('Trying to authorise')
    greetings = await read_line_from_chat(reader)
    logging.debug(f'Greetings from the chat: {greetings}')
    await write_line_to_chat(writer, token)
    response = await read_line_from_chat(reader)
    response = json.loads(response)
    if not response:
        logging.error('Wrong token. Please check it or register new user with `--username` parameter')
        return None
    logging.debug(response)
    logging.info(f'Authorised as: {response.get("nickname")}')
    return response.get('nickname')


async def register(reader: StreamReader, writer: StreamWriter, nickname: str) -> str:
    """New user registration."""
    logging.debug('Trying to register')
    greetings = await read_line_from_chat(reader)
    logging.debug(f'Greetings from the chat: {greetings}')
    await write_line_to_chat(writer, '')  # say 'we don't have a token'
    ask_for_nickname = await read_line_from_chat(reader)
    logging.debug(f'Chat asks about nickname: {ask_for_nickname}')
    await write_line_to_chat(writer, nickname)
    response_content = await read_line_from_chat(reader)
    if not response_content:
        logging.error('Registration failed. Please try again later.')
        return ''
    response = json.loads(response_content)
    logging.debug(response)
    logging.debug(f'Registered as {response.get("nickname")}')
    logging.debug(f'New access token {response.get("account_hash")}')
    return response.get('account_hash')
