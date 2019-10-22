import argparse
import os

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


if __name__ == '__main__':
    parser = create_parser()
    options = parser.parse_args()
    print(options)
