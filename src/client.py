import socket

from helpers import decode_response, encode_commands

BUFFER_SIZE = 1014

s = socket.socket(type=socket.SOCK_DGRAM)


def get_details(screen, *args):
    commands = [(screen, args)]
    print(f"asking with: {(screen, args)}")

    s.sendto(encode_commands(commands), ("0.0.0.0", 9991))

    raw_data, addr = s.recvfrom(BUFFER_SIZE)
    if raw_data:
        raw_response = decode_response(raw_data, commands)
        _, details = raw_response[0]

        return details
