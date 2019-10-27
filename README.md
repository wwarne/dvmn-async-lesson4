# Lesson 04 - Minecraft undeground chat

Help for a professional Minecraft player - babushka Zina.



# Requirements

* python 3.7+ is recommended
* [Poetry](https://poetry.eustace.io/) for dependency management. 

# How to use

## Reading chat messages


```bash
$ python chat_reader.py --help
usage: Minechat client [-h] [--host HOST] [--port PORT] [--history FILEPATH]

optional arguments:
  -h, --help          show this help message and exit

Chat reader settings:
  --host HOST         Chat address (ip or host name)
  --port PORT         Chat port
  --history FILEPATH  Path to a history file, all messages will be saved there
  --verbose           Show more information on a screen
```

You can also set environmental variables:

* `MINECHAT_READ_HOST` - Chat address (ip or host name)
* `MINECHAT_READ_PORT` - Chat port
* `MINECHAT_HISTORY_PATH` - Path to a history file, all messages will be saved there
* `MINECHAT_READ_VERBOSE` - Show debug information on screen

The command-line arguments have more priority than environmental variables.

## Sending chat messages

First of all you will need to register your username and write down your token for authentication.

```bash
$ python chat_writer.py --username "My very unique username"
> Please save this access token: 70563b20-f69c-11e9-8154-0242ac110002
```

With token you can send chat messages as follow:

```bash
$ python chat_writer.py --token "70563b20-f69c-11e9-8154-0242ac110002" --message "Hello everyone! Do you want to know some Minecraft secrets?"
```

You can also set token as environmental variables:

* `MINECHAT_WRITE_HOST` - Chat address (ip or host name)
* `MINECHAT_WRITE_PORT` - Chat port for writing
* `MINECHAT_TOKEN` - Token to access the chat
* `MINECHAT_WRITE_VERBOSE` - Show debug information on screen


```bash
$ python chat_writer.py --help

usage: Minechat message sender [-h] [--host HOST] [--port PORT]
                               [--message MESSAGE] [--verbose]
                               [--token TOKEN | --username USERNAME]

optional arguments:
  -h, --help           show this help message and exit

Sender settings:
  --host HOST          Chat address (ip or host name)
  --port PORT          Chat port
  --message MESSAGE    Message to send
  --verbose            Show more information in output
  --token TOKEN        Authorization token
  --username USERNAME  Your username for register (if token is not set)
```

# Project Goals

The code is written for educational purposes.
