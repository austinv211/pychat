
from chat_functions import _help, _myip, _myport, _connect, _terminate, _list, _send, _exit, \
    COMMANDS_DICT, run_server, general_loop, set_port_number

import asyncio
from functools import partial
from aioconsole import ainput, aprint
import threading
import sys


async def main():
    # event loop for reading input from the user
    while True:
        command_str = await ainput('')
        lower_command_str = command_str.lower()
        command_call, *command_args = lower_command_str.split(' ')
        if command_call in COMMANDS_DICT:
            try:
                func_to_call = COMMANDS_DICT[command_call]
                result = func_to_call(*command_args)
                if result:
                    await aprint(result)
            except TypeError as e:
                if 'positional arguments but' in str(e):
                    await aprint('Invalid number of arguments provided to function')
        else:
            await aprint(f'Command: {command_call} does not exist. Arguments provided {" ".join([*command_args])}')



if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            new_port_num = int(sys.argv[1])
            if new_port_num > 1023 and new_port_num <= 65535:
                set_port_number(new_port_num)
        except:
            print('Error assigning port number from command line input.')
    event_thread = threading.Thread(name='general_loop', target=general_loop)
    event_thread.start()
    asyncio.run(main())