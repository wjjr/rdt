import os
import sys

from rdt import *

if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) < 1 or not os.path.isfile(args[0]):
        print('E: must specify at least one file', file=sys.stderr)
        sys.exit(1)

    rdt_init(('127.0.0.1', 21678))

    for filename in args:
        filesize = os.path.getsize(filename)

        print(f'Sending file "{filename}" ({filesize} bytes) to server...', end='')

        with open(filename, 'rb') as file:
            rdt_send(bytes(f"{len(filename)}:{filename}{filesize}:", 'utf-8')
                     + file.read(1024))

            while file_bytes := file.read(1024):
                rdt_send(file_bytes)

            print(' Done.')

        print(f'Receiving file "{filename}" ({filesize} bytes) from server...', end='')

        with open(f'from_server--{filename}', 'wb') as file:
            to_receive = filesize

            while to_receive > 0:
                data, _ = rdt_recv()
                file.write(data)
                to_receive -= len(data)

            print(' Done.')
