#!/usr/bin/env python

from __future__ import print_function

from argparse import ArgumentParser
import json
import os
import sys
import socket
import socketserver
from .desktop import desktop


def debug(message, *args):
    if os.environ.get('SNIP_DEBUG') == '1':
        print(message.format(*args))


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


class ServerHandler(socketserver.StreamRequestHandler):

    def handle(self):
        self.data = self.rfile.readline().strip()
        response = {'error': False}
        try:
            message = json.loads(self.data)
            debug('message {}', message)
            if message['command'] == 'copy':
                desktop.copy(message['content'])
            elif message['command'] == 'paste':
                response['content'] = desktop.paste()
            elif message['command'] == 'open':
                desktop.open(message['url'])
        except Exception:
            response['error'] = True
            trace = str(sys.exc_info())
            print(trace)
            response['message'] = trace

        payload = json.dumps(response) + '\n'
        self.wfile.write(bytes(payload, 'utf-8'))


def listen(args):
    server = socketserver.TCPServer((args.host, args.port), ServerHandler)
    print('Listening on - {}:{}'.format(args.host, args.port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()


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
