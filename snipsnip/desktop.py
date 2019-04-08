from subprocess import Popen, PIPE
import sys
import codecs

import pyperclip

UTF8Writer = codecs.getwriter('utf-8')


class BaseDesktop(object):
    def copy(self, content):
        pyperclip.copy(content)

    def paste(self):
        return pyperclip.paste()

    def _call(self, args):
        proc = Popen(args, stdout=PIPE, stderr=PIPE)
        proc.wait()
        if proc.returncode != 0:
            raise Exception(proc.stderr.read())


class MacOsDesktop(BaseDesktop):

    def open(self, uri):
        self._call(['open', uri])


class X11Desktop(BaseDesktop):

    def open(self, uri):
        # TODO: use direct x11 calls so that it works when the socket is
        # mounted through the container.
        self._call(['xdg-open', uri])


if sys.platform == 'linux':
    desktop = X11Desktop()
else:
    desktop = MacOsDesktop()
