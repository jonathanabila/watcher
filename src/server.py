import socket

from factories import CommandsFactory
from helpers import decode_message, encode_message

BUFFER_SIZE = 1024
PORT = 9991

s = socket.socket(type=socket.SOCK_DGRAM)
s.bind(("0.0.0.0", PORT))


if __name__ == "__main__":
    print("Starting server...")
    while True:
        raw_data, addr = s.recvfrom(BUFFER_SIZE)

        if raw_data:
            raw_commands = decode_message(raw_data)

            commands = CommandsFactory.build(raw_commands)
            answers = []
            for command in commands:
                answers.append(command.execute())

            s.sendto(encode_message(answers), addr)

        print("awaiting...")
