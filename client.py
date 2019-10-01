#!/usr/bin/env python3
import socket
import random
import string


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

    return sock
