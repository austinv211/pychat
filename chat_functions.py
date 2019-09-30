from typing import Callable

import socket
import selectors
from typing import types
from aioconsole import aprint
import os

from client import start_connection

sel = selectors.DefaultSelector()
PORT_NUMBER = 5000
GLOBAL_CONNECTIONS = {}

LINE_SEP = '-----------------------------------'


def _help(func_name: str = None) -> None:
    '''
    Description:
    Display information about the available user interface options or command manual.

    :param func_name: The function name you would like to get help on

    Command Line Usage: help <function_name>

    Example:
    > help myip
    '''
    if func_name:
        if func_name in COMMANDS_DICT:
            return COMMANDS_DICT[func_name].__doc__
        else:
            return f'Help for command ({func_name}) not found.'
    else:
        return f'\n{LINE_SEP}'.join([item[1].__doc__ for item in COMMANDS_DICT.items() if item[1].__doc__])


def _myip() -> None:
    '''
    Description:
    Display the IP address of this process.
    Note: The IP should not be your “Local” address (127.0.0.1). It should be the actual IP of the computer.

    Command Line Usage: myip

    Example:
    > myip
    192.168.1.8
    '''
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        print('Error Getting IP.')

def _myport() -> None:
    '''
    Description:
    Display the port on which this process is listening for incoming connections.

    Command Line Usage: myport

    Example:
    > myport
    5000
    '''
    print(PORT_NUMBER)


def _connect(destination: str, port_num: str) -> None:
    '''
    Description:
    This command establishes a new TCP connection to the specified
    <destination> at the specified < port no>. The <destination> is the IP address of the computer. Any attempt
    to connect to an invalid IP should be rejected and suitable error message should be displayed. Success or
    failure in connections between two peers should be indicated by both the peers using suitable messages.
    Self-connections and duplicate connections should be flagged with suitable error messages
    '''
    try:
        sock = start_connection(destination, port_num)
        GLOBAL_CONNECTIONS[(destination, port_num)] = sock
        print(f'Connected to Destination: {(destination, port_num)}')
    except:
        print(f'Error connecting to destination: {(destination, port_num)}')



def _list():
    '''
    Description:
    Display a numbered list of all the connections this process is part of. This numbered list will include
    connections initiated by this process and connections initiated by other processes. The output should
    display the IP address and the listening port of all the peers the process is connected to.
    '''
    res = 'id:\tIP address\tPort No.\n'
    for index, item in enumerate(GLOBAL_CONNECTIONS.items(), 0):
        res += f'{index}\t{item[0][0]}\t{item[0][1]}\n'
    return res


def _terminate():
    raise NotImplementedError


def _send():
    raise NotImplementedError


def _exit():
    '''
    Exits the program
    '''
    for item in GLOBAL_CONNECTIONS.items():
        item[1].close()
    os._exit(1)

#set a commands dictionary, this will store our possible commands and functions for said command
COMMANDS_DICT = {
    'help': _help,
    'myip': _myip,
    'myport': _myport,
    'connect': _connect,
    'list': _list,
    'terminate': _terminate,
    'send': _send,
    'exit': _exit 
    }