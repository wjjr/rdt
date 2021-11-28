import errno
import os
import random
import socket
import threading
import time

MAX_DATA_SIZE = 2 ** 15
DELAY_RATE = 0.0
LOSS_RATE = 0.0
CORRUPTION_RATE = 0.001
DUPLICATION_RATE = 0.0

__rdt_stats = {
    'sent': 0,
    'received': 0
}

__udt_stats = {
    'sent': 0,
    'delayed': 0,
    'lost': 0,
    'corrupt': 0,
    'duplicated': 0,
    'safe': 0,
    'received': 0
}


class __RDT:
    socket: socket.socket
    bound = False
    simulate_unreliability = False
    init = False


def rdt_init(address: tuple[str, int], bind=False, simulate_unreliability=False) -> None:
    __RDT.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if bind:
        __RDT.socket.bind(address)
        __RDT.bound = True
    else:
        __RDT.socket.connect(address)

    __RDT.simulate_unreliability = simulate_unreliability
    __RDT.init = True


def rdt_send(data: bytes, address: tuple[str, int] = None) -> int:
    if not __RDT.init:
        raise OSError(errno.EDESTADDRREQ, os.strerror(errno.EDESTADDRREQ) + ': Call rdt_init')
    if __RDT.bound and address is None:
        raise OSError(errno.EDESTADDRREQ, os.strerror(errno.EDESTADDRREQ))
    elif len(data) > MAX_DATA_SIZE:
        raise OSError(errno.EMSGSIZE, os.strerror(errno.EMSGSIZE))

    time.sleep(1e-6)  # throttling

    pkt = __make_pkt(data)

    size = __udt_send(pkt, address)
    __rdt_stats['sent'] += 1

    return size


def rdt_recv() -> [tuple[bytes, tuple[str, int]], bytes]:
    if not __RDT.init:
        raise OSError(errno.EDESTADDRREQ, os.strerror(errno.EDESTADDRREQ) + ': Call rdt_init')

    pkt, address = __udt_recv()
    __rdt_stats['received'] += 1

    data = __extract(pkt)

    if __RDT.bound:
        return data, address
    else:
        return data


def __make_pkt(data: bytes) -> bytes:
    return data


def __extract(pkt: bytes) -> bytes:
    return pkt


def rdt_stats(pprint=False):
    if not pprint:
        return {
            'rdt': __rdt_stats,
            'udt': __udt_stats
        }

    print('\nRDT stats:')
    print(f"* Received {__rdt_stats['received']} packets")
    print(f"* Sent {__rdt_stats['sent']} packets")

    udt_p = (100 / __udt_stats['sent']) if __udt_stats['sent'] > 0 else 0

    print('\nUDT stats:')
    print(f"* Received {__udt_stats['received']} packets")
    print(f"* Sent {__udt_stats['sent']} packets")

    if __RDT.simulate_unreliability and __udt_stats['sent'] > 0:
        print(f"  {__udt_stats['safe']:6d} ({__udt_stats['safe'] * udt_p:7.3f}%) safe packets")
        print(f"  {__udt_stats['delayed']:6d} ({__udt_stats['delayed'] * udt_p:7.3f}%) delayed packets")
        print(f"  {__udt_stats['lost']:6d} ({__udt_stats['lost'] * udt_p:7.3f}%) lost packets")
        print(f"  {__udt_stats['corrupt']:6d} ({__udt_stats['corrupt'] * udt_p:7.3f}%) corrupt packets")
        print(f"  {__udt_stats['duplicated']:6d} ({__udt_stats['duplicated'] * udt_p:7.3f}%) duplicated packets")


def __udt_send(pkt: bytes, address: tuple[str, int] = None, *, _is_recursion=False) -> int:
    __udt_stats['sent'] += 1 if not _is_recursion else 0

    if __RDT.simulate_unreliability and not _is_recursion:
        if random.random() < DELAY_RATE:
            __udt_stats['delayed'] += 1

            threading.Timer(1e-3, lambda: __udt_send(pkt, address, _is_recursion=True)).start()

            return len(pkt)
        elif random.random() < LOSS_RATE:
            __udt_stats['lost'] += 1

            return len(pkt)
        elif random.random() < CORRUPTION_RATE:
            __udt_stats['corrupt'] += 1

            mask = 0x00

            for bit in random.sample(range(8), random.randint(1, 2)):
                mask |= (1 << bit)

            pkt = bytearray(pkt)
            pkt[random.randrange(len(pkt))] ^= mask
            pkt = bytes(pkt)
        elif random.random() < DUPLICATION_RATE:
            __udt_stats['duplicated'] += 1

            __udt_send(pkt, address, _is_recursion=True)
        else:
            __udt_stats['safe'] += 1

    if address is not None:
        return __RDT.socket.sendto(pkt, address)
    else:
        return __RDT.socket.send(pkt)


def __udt_recv() -> tuple[bytes, tuple[str, int]]:
    data, address = __RDT.socket.recvfrom(MAX_DATA_SIZE)

    __udt_stats['received'] += 1

    return data, address


__all__ = ['rdt_init', 'rdt_send', 'rdt_recv', 'rdt_stats']
