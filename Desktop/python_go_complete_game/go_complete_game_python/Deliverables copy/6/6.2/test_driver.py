import json
import sys
from go_referee import GoReferee

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

# print(command_list)

Referee = GoReferee()
names = 0

for command in command_list:
    if names != 2:
        output = Referee.assign_player(command)
        names += 1
        if output:
            # print(output)
            result_list += output
    else:
        # actions here, return board history before every action
        result_list.append(Referee.get_history())
        # print(Referee.get_history())
        output = Referee.perform_action(command)
        if output:
            # print(output)
            # someone won
            result_list.append(output)
            break

# print('end here')
# print(Referee.history[0].get_board_repr())


print(json.dumps(result_list))