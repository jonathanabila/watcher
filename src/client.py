import socket
import time

from constants import Screens
from helpers import decode_response, encode_commands

BUFFER_SIZE = 1014
INTERVAL = 5

s = socket.socket(type=socket.SOCK_DGRAM)


if __name__ == "__main__":
    print("Starting client...")
    while True:
        print("asking...")
        commands = [(Screens.CPU, None)]
        s.sendto(encode_commands(commands), ("0.0.0.0", 9991))

        raw_data, addr = s.recvfrom(BUFFER_SIZE)
        if raw_data:
            raw_response = decode_response(raw_data, commands)

            for response in raw_response:
                (command, args), message = response
                print(f"{command}: {message}")

        print("sleeping...")
        time.sleep(INTERVAL)
