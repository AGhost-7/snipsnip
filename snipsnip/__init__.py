#!/usr/bin/env python

from __future__ import print_function

from argparse import ArgumentParser
import json
import sys
import socket
from .desktop import desktop
from os import path, environ
from .server import listen
from .debug import debug


def parse_arguments():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='mode')
    subparsers.required = True

    server_parser = subparsers.add_parser('server')
    server_parser.add_argument('--port', default=8099, type=int)
    server_parser.add_argument('--host', default='localhost')

    client_parser = subparsers.add_parser('client')
    client_parser.add_argument('--port', default=8099, type=int)
    client_parser.add_argument('--host', default='localhost')
    client_subparsers = client_parser.add_subparsers(dest='command')

    client_subparsers.add_parser('copy')
    client_subparsers.add_parser('paste')
    say_parser = client_subparsers.add_parser('say')
    say_parser.add_argument('content', nargs='*')
    open_parser = client_subparsers.add_parser('open')
    open_parser.add_argument('url')

    subparsers.add_parser('copy')
    subparsers.add_parser('paste')
    open_parser = subparsers.add_parser('open')
    open_parser.add_argument('url')

    args = parser.parse_args()

    return args


def parse_xclip_arguments():
    parser = ArgumentParser()
    parser.add_argument(
        '-in',
        '-i',
        action='store_const',
        dest='mode',
        const=True,
        default=False)
    parser.add_argument(
        '-out',
        '-o',
        action='store_const',
        dest='mode',
        const='paste')
    parser.add_argument('-selection', nargs=1)

    args = parser.parse_args()

    if 'DISPLAY' not in environ:
        args.command = args.mode
        args.mode = 'client'
        args.port = int(environ.get('SNIPSNIP_PORT', 8099))
        args.host = environ.get('SNIPSNIP_HOST', 'localhost')

    return args


def parse_xsel_arguments():
    parser = ArgumentParser()
    parser.add_argument(
        '--clipboard', '-b',
        action='store_const',
        default=False,
        const=True)
    parser.add_argument(
        '--output', '-o',
        action='store_const',
        const='paste',
        dest='mode')
    parser.add_argument(
        '--input', '-i',
        action='store_const',
        const='copy',
        dest='mode')
    args = parser.parse_args()
    if 'DISPLAY' not in environ:
        args.command = args.mode
        args.mode = 'client'
        args.port = int(environ.get('SNIPSNIP_PORT', 8099))
        args.host = environ.get('SNIPSNIP_HOST', 'localhost')
    return args


def request(args, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:

        sock.connect((args.host, args.port))
        serialized = bytes(json.dumps(message) + '\n', 'utf-8')

        sock.sendall(serialized)

        buf = ''
        linefeed = False
        while not linefeed:
            received = str(sock.recv(1024), 'utf-8')
            if '\n' in received:
                linefeed = True
                buf += received

        return json.loads(buf)
    finally:
        sock.close()


def send_command(args):
    command = args.command
    message = {'command': command}

    if command == 'copy':
        message['content'] = sys.stdin.read()
    elif command == 'say':
        message['content'] = ' '.join(args.content)
    elif command == 'open':
        message['url'] = args.url

    response = request(args, message)

    debug('Sent {}', message)
    debug('Response {}', response)

    if response['error']:
        sys.stderr.write(response['message'])
        sys.exit(1)
    elif command == 'paste':
        sys.stdout.write(response['content'])


def main():
    script_name = path.basename(sys.argv[0])
    # TODO: support xsel emulation as well.
    if script_name == 'xclip':
        args = parse_xclip_arguments()
    elif script_name == 'xsel':
        args = parse_xsel_arguments()
    else:
        args = parse_arguments()

    if args.mode == 'server':
        listen(args)
    elif args.mode == 'client':
        send_command(args)
    elif args.mode == 'paste':
        text = desktop.paste()
        sys.stdout.write(text)
    elif args.mode == 'copy':
        content = sys.stdin.read()
        desktop.copy(content)
    elif args.mode == 'open':
        desktop.open(args.url)
