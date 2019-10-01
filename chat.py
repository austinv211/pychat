
from chat_functions import _help, _myip, _myport, _connect, _terminate, _list, _send, _exit, COMMANDS_DICT, run_server

import asyncio
from functools import partial
from aioconsole import ainput, aprint
import threading


async def main():
    while True:
        command_str = await ainput('')
        lower_command_str = command_str.lower()
        command_call, *command_args = lower_command_str.split(' ')
        if command_call in COMMANDS_DICT:
            func_to_call = COMMANDS_DICT[command_call]
            result = func_to_call(*command_args)
            if result:
                await aprint(result)
        else:
            await aprint(f'Command: {command_call} {command_args} does not exist.')



if __name__ == "__main__":
    server_thread = threading.Thread(name='run_server', target=run_server)
    server_thread.start()
    asyncio.run(main())