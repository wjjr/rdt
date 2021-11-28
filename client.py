from rdt import *


def run_client(address, simulate_unreliability, num_packets):
    rdt_init(address, simulate_unreliability=simulate_unreliability)

    try:
        for i in range(num_packets):
            rdt_send(bytes(f"{i:06d}\xff\xff\xff\xff\xff\xff\xff"
                           f"{i:06d}\xff\xff\xff\xff\xff\xff\xff"
                           f"{i:06d}", 'latin-1'))
            print(f"Sent packet -> {i:06}")
    except ConnectionError:
        print('Server looks tired, exiting...')

    rdt_stats(pprint=True)
