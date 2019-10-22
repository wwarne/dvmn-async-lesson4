# Lesson 04 - Minecraft undeground chat

Help for babushka Zina.


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
```

You can also set environmental variables:

* `MINECHAT_READ_HOST` - Chat address (ip or host name)
* `MINECHAT_READ_PORT` - Chat port
* `MINECHAT_HISTORY_PATH` - Path to a history file, all messages will be saved there

The command-line arguments are have more priority than environmental variables.


# Project Goals

The code is written for educational purposes.
