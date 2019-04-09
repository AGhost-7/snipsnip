
import os


def debug(message, *args):
    if os.environ.get('SNIP_DEBUG') == '1':
        print(message.format(*args))
