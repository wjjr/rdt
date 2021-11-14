from rdt import *

if __name__ == '__main__':
    rdt_init(('127.0.0.1', 21678), bind=True)

    while True:
        data, address = rdt_recv()

        try:
            b_filename_len, data = data.split(b':', 1)
            filename_len = int(b_filename_len)
            filename = data[:filename_len].decode('utf-8')

            b_filesize, data = data[filename_len:].split(b':', 1)
            filesize = int(b_filesize)

            print(f'Receiving file "{filename}" ({filesize} bytes) from {address[0]}:{address[1]}...', end='')

            with open(f"from_client--{filename}", 'wb') as file:
                file.write(data)
                to_receive = filesize - len(data)

                while to_receive > 0:
                    data, _ = rdt_recv()
                    file.write(data)
                    to_receive -= len(data)

                print(' Done.')

            print(f'Sending file "{filename}" ({filesize} bytes) to {address[0]}:{address[1]}...', end='')

            with open(f"from_client--{filename}", 'rb') as file:
                while file_bytes := file.read(1024):
                    rdt_send(file_bytes, address)

                print(' Done.')
        except:
            raise
