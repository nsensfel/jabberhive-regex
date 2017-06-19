#!/bin/env python3
import argparse
import re

import socket
import _thread

class ClientState:
    CLIENT_IS_SENDING_DOWNSTREAM = 1
    CLIENT_IS_SENDING_UPSTREAM = 2
    CLIENT_IS_CONNECTING = 3
    CLIENT_IS_TERMINATING = 4

def client_main (source, params):
    pattern = re.compile(params.regex)
    state = ClientState.CLIENT_IS_CONNECTING
    t_connect = None
    f_connect = None
    current_target = None

    try:
        while True:
            if (state == ClientState.CLIENT_IS_SENDING_DOWNSTREAM):
                try:
                    in_data = b""

                    while True:
                        in_char = source.recv(1)
                        in_data = (in_data + in_char)

                        if (in_char == b"\n"):
                            break
                        elif (in_char == b''):
                            raise Exception("Disconnected client")

                    up_data = in_data.decode("UTF-8")
                    valid = 1
                except UnicodeDecodeError:
                    valid = 0

                if ((valid == 1) and pattern.match(up_data)):
                    if (t_connect != None):
                        t_connect.sendall(in_data)
                        current_target = 't'
                        state = ClientState.CLIENT_IS_SENDING_UPSTREAM
                        print("[Matched] Sending upstream...")
                    else:
                        source.send(b"!P \n")
                        print("Matched")
                else:
                    if (f_connect != None):
                        f_connect.sendall(in_data)
                        current_target = 'f'
                        state = ClientState.CLIENT_IS_SENDING_UPSTREAM
                        print("[No match] Sending upstream...")
                    else:
                        source.sendall(b"!P \n")
                        print("Did not match")
            elif (state == ClientState.CLIENT_IS_SENDING_UPSTREAM):
                matched = 0
                c = b"\0"

                while (c != b"\n"):
                    print("67: sending upstream")
                    if (current_target == 't'):
                        c = t_connect.recv(1)
                    else:
                        c = f_connect.recv(1)

                    source.send(c)

                    if ((matched == 0) and (c == b"!")):
                        matched = 1
                    elif ((matched == 1) and ((c == b"P") or (c == b"N"))):
                        matched = 2
                    elif ((matched == 2) and (c == b" ")):
                        print("Sending downstream...")
                        state = ClientState.CLIENT_IS_SENDING_DOWNSTREAM
                    else:
                        matched = -1

            elif (state == ClientState.CLIENT_IS_CONNECTING):
                print("Connecting to downstream...")
                if (params.destination_true != None):
                    t_connect = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    t_connect.connect(params.destination_true)

                if (params.destination_false != None):
                    f_connect = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    f_connect.connect(params.destination_false)

                print("Sending downstream...")
                state = ClientState.CLIENT_IS_SENDING_DOWNSTREAM
            else:
                break
    except:
        print("Closing")
        source.close()

        if (t_connect != None):
            t_connect.close()

        if (f_connect != None):
            f_connect.close()

################################################################################
## ARGUMENTS HANDLING ##########################################################
################################################################################

parser = argparse.ArgumentParser(
    description = (
        "Generates a list of instructions to construct the Structural Level."
    )
)

parser.add_argument(
    '-s',
    '--socket-name',
    type = str,
    required = True,
    help = 'Name of the UNIX socket for this filter.'
)

parser.add_argument(
    '-t',
    '--destination-true',
    type = str,
    help = 'UNIX socket this filter sends to when a match is found.',
)

parser.add_argument(
    '-f',
    '--destination-false',
    type = str,
    help = 'UNIX socket this filter sends to when a match is found.',
)

parser.add_argument(
    '-r',
    '--regex',
    type = str,
    required = True,
    help = 'The regex to test the message against.',
)

args = parser.parse_args()

################################################################################
## MAIN ########################################################################
################################################################################
server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

server_socket.bind(args.socket_name)
server_socket.listen(5)

while True:
    (client, client_address) = server_socket.accept()
    _thread.start_new_thread(client_main, (client, args))

