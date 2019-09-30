#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import random
import string

DEFAULT_SELECTOR = selectors.DefaultSelector()

CLIENT_SOCKETS = {}


def start_connection(destination: str, port_num: str):
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


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print("received", repr(recv_data), "from connection", data.connid)
            data.recv_total += len(recv_data)
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print("sending", repr(data.outb), "to connection", data.connid)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

try:
    while True:
        events = DEFAULT_SELECTOR.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Check for a socket being monitored to continue.
        if not DEFAULT_SELECTOR.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    DEFAULT_SELECTOR.close()