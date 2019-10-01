from typing import Callable

import socket
import selectors
from typing import types
from aioconsole import aprint
import os
import random
import string

sel = selectors.DefaultSelector()
PORT_NUMBER = 5000
GLOBAL_CONNECTIONS = {}

LINE_SEP = '-----------------------------------'

#------ Server functions --------------

def accept_wrapper(sock: socket.socket) -> None:
    '''
    wrapper function to accept a socket connection 
    and register with the default selector
    '''
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from", addr)
    GLOBAL_CONNECTIONS[str(len(GLOBAL_CONNECTIONS))] = (*addr, sock, 'server')
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    '''
    service connection function, this is the server event loop
    '''
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print("echoing", repr(data.outb), "to", data.addr)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


def run_server():
    '''
    function to run the server event loop for the chat application.

    Uses non-blocking sockets
    '''
    try:
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_bind = (_myip(), PORT_NUMBER)
        lsock.bind(server_bind)
        lsock.listen()
        print("listening on", server_bind)
        lsock.setblocking(False)
        sel.register(lsock, selectors.EVENT_READ, data=None)
        try:
            while True:
                events = sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        accept_wrapper(key.fileobj)
                    else:
                        service_connection(key, mask)
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            sel.close()
    except:
        print('Server already running, Running in Client only mode')

# ----------- Client functions ------------

def start_connection(destination: str, port_num: str) -> socket.socket:
    '''
    function to start a connection to a server.

    returns the client tcp socket
    '''
    # create a tuple containing the host and port
    server_address = (destination, int(port_num))

    # create a random 16 letter string to use as a connection ID
    connection_id = ''.join(random.choice(string.ascii_lowercase) for i in range(16))

    # print that we are starting a connection to the server
    print("starting connection", connection_id, "to", server_address)

    # create a TCP socket (nonblocking)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_address) # like connect, but returns an error code rather than raising an exception when an error occurs

    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(addr=server_address, inb=b"", outb=b"")
    sel.register(sock, events, data=data)
    return sock

# ------------- Chat functions -----------------------

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
    # try:
    sock = start_connection(destination, port_num)
    GLOBAL_CONNECTIONS[str(len(GLOBAL_CONNECTIONS))] = (destination, port_num, sock, 'client')
    print(f'Connected to Destination: {(destination, port_num)}')
    # except:
    #     print(f'Error connecting to destination: {(destination, port_num)}')


def _list():
    '''
    Description:
    Display a numbered list of all the connections this process is part of. This numbered list will include
    connections initiated by this process and connections initiated by other processes. The output should
    display the IP address and the listening port of all the peers the process is connected to.
    '''
    res = 'id:\tIP address\tPort No.\n'
    for index, item in enumerate(GLOBAL_CONNECTIONS.items(), 0):
        res += f'{index}\t{item[1][0]}\t{item[1][1]}\n'
    return res


def _terminate(index: str):
    '''
    Description:
    This command will terminate the connection listed under the specified
    number when LIST is used to display all connections. E.g., terminate 2. In this example, the connection
    with 192.168.21.21 should end. An error message is displayed if a valid connection does not exist as
    number 2. If a remote machine terminates one of your connections, you should also display a message. 
    '''
    try:
        # need to send message to other end to close
        deleted_item = GLOBAL_CONNECTIONS.pop(index, None)
        if deleted_item[3] != 'server':
            deleted_item[2].close()
            sel.unregister(deleted_item[2])
        return f'Closed connection {deleted_item[:2]}'
    except:
        return f'Error terminating connection #{index}'
    


def _send():
    raise NotImplementedError


def _exit():
    '''
    Exits the program
    '''
    for item in GLOBAL_CONNECTIONS.items():
        item[1][2].close()
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