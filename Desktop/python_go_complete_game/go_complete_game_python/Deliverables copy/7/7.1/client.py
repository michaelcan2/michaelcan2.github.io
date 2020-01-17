import socket
import json
from board_components.go_player import GoPlayerRemote
import sys

decoder = json.JSONDecoder()

with open('go.config') as json_file:
    data = json.load(json_file)
    IP = data['IP']
    port = data['port']

player = GoPlayerRemote()
done = False

def start_client():
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((IP, port))
                while True:
                    command = s.recv(32768)
                    # print(command)
                    if command:
                        # print('command1:', command.decode('utf-8'))
                        # decoder result is (command, str_length)
                        command = decoder.raw_decode(command.decode('utf-8'))[0]
                        if command[0] == 'shutdown':
                            break

                        # print('command:', command)
                        result = player.send(command)
                        s.sendall(bytes(json.dumps(result), 'utf-8'))

                        if result == 'GO has gone crazy!':
                            break
            # done, break out of client loop
            break

        except ConnectionRefusedError:
            pass
            # print('retrying connection')

try:
    start_client()
except ConnectionResetError:
    # program is done now
    pass