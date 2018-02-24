# Snipsnip
Simple client/server which can be used to forward clipboard and browse commands
to your VM's host.

Client:
```
usage: snipsnip client [-h] [--port PORT] [--host HOST]
                       {copy,paste,say,open,youtube} ...

positional arguments:
  {copy,paste,say,open,youtube}

optional arguments:
  -h, --help            show this help message and exit
  --port PORT
  --host HOST
```

Server:
```
usage: snipsnip server [-h] [--port PORT] [--host HOST]

optional arguments:
  -h, --help   show this help message and exit
  --port PORT
  --host HOST
```

To install, simply run:
```
pip install snipsnip
```

## Youtube Sound Playback
For the Youtube playback to work you will need to have `ffmpeg` of installed.
You can install it using brew:
```sh
brew install ffmpeg
```
