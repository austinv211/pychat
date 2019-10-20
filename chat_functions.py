from typing import Callable
import socket
import selectors
from typing import types
from aioconsole import aprint
import os
import time

# ----- GLOBAL CONSTANTS ----------
DEFAULT_SELECTOR = selectors.DefaultSelector() # the default selector to use for IO from sockets
PORT_NUMBER = 5000 # the port number to run the server on, this will be the default if no port number gets set at start
GLOBAL_CONNECTIONS = {} # a global dictionary to store our connections
LINE_SEP = '-----------------------------------' # Line separator constat
EVENTS = selectors.EVENT_READ | selectors.EVENT_WRITE # the events to check for in our selector


#------ Server functions --------------

def set_port_number(port_num: int) -> None:
    global PORT_NUMBER
    PORT_NUMBER = port_num

def accept_wrapper(sock: socket.socket) -> None:
    '''
    wrapper function to accept a socket connection 
    and register with the default selector
    '''
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from", addr)
    conn_id = str(len(GLOBAL_CONNECTIONS))
    GLOBAL_CONNECTIONS[conn_id] = (addr[0], addr[1], conn, 'server')
    conn.setblocking(False)
    data = types.SimpleNamespace(connid=conn_id, addr=addr, messages=[], inb=b"", outb=b"")
    DEFAULT_SELECTOR.register(conn, EVENTS, data=data)

def service_connection(key, mask):
    '''
    service connection function, this is the server event loop
    '''
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            if recv_data.decode() != '_x01_exit':
                print(f'\nMessage Received from { data.addr[0] }\nSender\'s Port: { data.addr[1] }\nMessage: \"{ recv_data.decode() }\"\n')
            else:
                found_key = None
                for key, value in GLOBAL_CONNECTIONS.items():
                    if value[0] == data.addr[0] and value[1] == data.addr[1]:
                        found_key = key
                        break
                if found_key:
                    _terminate(found_key, received_exit=True)
                
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            if data.outb.decode() != '_x01_exit':
                print(f'\nMessage \"{ data.outb.decode() }\" Sent to Connection ID: { data.connid }\n')
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
        DEFAULT_SELECTOR.register(lsock, selectors.EVENT_READ, data=None)
    except:
        print('Server already running, Running in Client only mode')

# ----------- Client functions ------------

def start_connection(destination: str, port_num: str, conn_id: str) -> socket.socket:
    '''
    function to start a connection to a server.

    returns the client tcp socket
    '''
    # create a tuple containing the host and port
    server_address = (destination, int(port_num))

    # print that we are starting a connection to the server
    print(f'starting connection to: {server_address}')

    # create a TCP socket (nonblocking)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_address) # like connect, but returns an error code rather than raising an exception when an error occurs

    data = types.SimpleNamespace(connid=conn_id, addr=server_address, messages=[], inb=b"", outb=b"")
    DEFAULT_SELECTOR.register(sock, EVENTS, data=data)
    return sock

# ------------- General Event Loop -------------------

def general_loop():
    run_server()
    try:
        while True:
            events_to_check = DEFAULT_SELECTOR.select(timeout=None)
            for key, mask in events_to_check:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    finally:
        DEFAULT_SELECTOR.close()

# ------------- Chat functions -----------------------

def _help(func_name: str = None) -> None:
    '''
    Command Name:
    help
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
    Command Name:
    myip
    Description:
    Display the IP address of this process.
    Note: The IP should not be your “Local” address (127.0.0.1). It should be the actual IP of the computer.

    Command Line Usage: myip

    Example:
    > myip
    192.168.1.8
    '''
    try:
        address_list = socket.gethostbyname_ex(socket.gethostname())[2]
        for address in address_list:
            if address != '127.0.0.1':
                return address
        print('Could not get IP address. Exiting ...')
        _exit()
    except:
        print('Error Getting IP.')

def _myport() -> None:
    '''
    Command Name:
    myport
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
    Command Name:
    connect
    Description:
    This command establishes a new TCP connection to the specified
    <destination> at the specified < port no>. The <destination> is the IP address of the computer. Any attempt
    to connect to an invalid IP should be rejected and suitable error message should be displayed. Success or
    failure in connections between two peers should be indicated by both the peers using suitable messages.
    Self-connections and duplicate connections should be flagged with suitable error messages
    '''
    try:
        conn_id = str(len(GLOBAL_CONNECTIONS))
        sock = start_connection(destination, port_num, conn_id)
        GLOBAL_CONNECTIONS[conn_id] = (destination, port_num, sock, 'client')
        print(f'Connected to Destination: {(destination, port_num)}')
    except:
        print(f'Error connecting to destination: {(destination, port_num)}')


def _list():
    '''
    Command Name:
    list
    Description:
    Display a numbered list of all the connections this process is part of. This numbered list will include
    connections initiated by this process and connections initiated by other processes. The output should
    display the IP address and the listening port of all the peers the process is connected to.
    '''
    res = 'id:\tIP address\tPort No.\n'
    for index, item in enumerate(GLOBAL_CONNECTIONS.items(), 0):
        res += f'{index}\t{item[1][0]}\t{item[1][1]}\n'
    return res


def _terminate(index: str, received_exit=False):
    '''
    Command Name:
    terminate
    Description:
    This command will terminate the connection listed under the specified
    number when LIST is used to display all connections. E.g., terminate 2. In this example, the connection
    with 192.168.21.21 should end. An error message is displayed if a valid connection does not exist as
    number 2. If a remote machine terminates one of your connections, you should also display a message. 
    '''
    try:
        if not received_exit:
            _send(index, '_x01_exit')
            time.sleep(3)
        else:
            print(f'Terminating Connection {index} due to peer disconnect.')
        deleted_item = GLOBAL_CONNECTIONS.pop(index, None)
        if deleted_item[3] != 'server':
            deleted_item[2].close()
            DEFAULT_SELECTOR.unregister(deleted_item[2])
        return f'Closed connection {deleted_item[:2]}'
    except:
        return f'Error terminating connection #{index}'
    


def _send(connection_id: str, *argv):
    '''
    Command Name:
    send
    Description:
    send <connection id.> <message> (For example, send 3 Oh! This project is a piece of cake). This will
    send the message to the host on the connection that is designated by the number 3 when command “list” is
    used. The message to be sent can be up-to 100 characters long, including blank spaces. On successfully
    executing the command, the sender should display “Message sent to <connection id>” on the screen. On
    receiving any message from the peer, the receiver should display the received message along with the
    sender information.
    '''
    # get the socket at the connection id
    destination, port_num, sock, _ = GLOBAL_CONNECTIONS.get(connection_id)
    message_to_send = ' '.join([arg for arg in argv])
    DEFAULT_SELECTOR.modify(sock, events=EVENTS, data=types.SimpleNamespace(connid=connection_id, addr=(destination, port_num), messages=[message_to_send.encode()], inb=b"", outb=b""))


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