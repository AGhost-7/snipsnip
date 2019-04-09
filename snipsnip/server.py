import json
import socketserver
from .desktop import desktop
from .debug import debug
import sys


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
