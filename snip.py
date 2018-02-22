#!/usr/bin/env python

from __future__ import print_function

from argparse import ArgumentParser
import json
import os
from subprocess import Popen, PIPE
import sys
import socket

try:
    import socketserver
except ImportError:
    import SocketServer as socketserver


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
    open_parser = client_subparsers.add_parser('open')
    open_parser.add_argument('url')

    args = parser.parse_args()

    return args


class ServerHandler(socketserver.StreamRequestHandler):

    def _wait(self, response, proc):
        proc.wait()
        if proc.returncode != 0:
            response['message'] = proc.stderr.read()
            response['error'] = True

    def handle(self):
        self.data = self.rfile.readline().strip()
        response = {'error': False}
        try:
            message = json.loads(self.data)
            debug('message {}'.format(message))
            if message['command'] == 'copy':
                proc = Popen(['pbcopy'], stdin=PIPE, stderr=PIPE)
                proc.stdin.write(message['content'])
                proc.stdin.close()
                self._wait(response, proc)
            elif message['command'] == 'paste':
                proc = Popen(['pbpaste'], stdout=PIPE, stderr=PIPE)
                response['content'] = proc.stdout.read()
                self._wait(response, proc)
            elif message['command'] == 'open':
                proc = Popen(
                    ['open', message['url']], stdout=PIPE, stderr=PIPE)
                self._wait(response, proc)
        except Exception:
            response['error'] = True
            response['message'] = str(sys.exc_info())
        self.wfile.write(json.dumps(response) + '\n')


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
        if sys.version_info.major == 3:
            serialized = bytes(json.dumps(message) + '\n', 'utf-8')
        else:
            serialized = json.dumps(message) + '\n'

        sock.sendall(serialized)

        buf = ''
        linefeed = False
        while not linefeed:
            if sys.version_info.major == 3:
                received = str(sock.recv(1024), 'utf-8')
            else:
                received = sock.recv(1024)
            if '\n' in received:
                linefeed = True
                buf += received

        return json.loads(buf)
    finally:
        sock.close()


def send_command(args):
    command = args.command
    if command not in ('copy', 'paste', 'open'):
        raise Exception('Invalid command ' + args.command)

    message = {'command': command}

    if command == 'copy':
        message['content'] = sys.stdin.read()
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


args = parse_arguments()

if args.mode == 'server':
    listen(args)
elif args.mode == 'client':
    send_command(args)