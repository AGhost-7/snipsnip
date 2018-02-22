# Snipsnip
Simple client/server which can be used to forward clipboard and browse comamnds
to your VM's host.

Client:
```
usage: snipsnip client [-h] [--port PORT] [--host HOST] {copy,paste,open} ...

positional arguments:
  {copy,paste,open}

optional arguments:
  -h, --help         show this help message and exit
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
