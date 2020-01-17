import json
import sys
from board_components.board import Board
from board_components.go_player import GoPlayerRemoteProxy

command_list = []
decoder = json.JSONDecoder()

if not sys.stdin.isatty():
    file = sys.stdin.read()
    s_len = len(file)
    end = 0

    while end != s_len:
        try:
            obj, end = decoder.raw_decode(file, idx=end)
            command_list.append(obj)
        except ValueError:
            end += 1

result_list = []

player = GoPlayerRemoteProxy()

for command in command_list:
    try:
        # catch assertion and contract exceptions
        if command[0] == "register":
            result = player.register()
        elif command[0] == "receive-stones":
            result = player.receive_stones(command[1])
        elif command[0] == "make-a-move":
            result = player.make_a_move(command[1])
        else:
            raise AssertionError("Invalid command!")
    except:
        result = 'GO has gone crazy!'
        
    if result == None:
        continue

    result_list.append(result)

    if result == 'GO has gone crazy!':
        break

print(json.dumps(result_list))

# close other threads and finish
sys.exit()