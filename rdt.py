import errno
import os
import socket
import time

MAX_DATA_SIZE = 2 ** 15


class __RDT:
    init: bool = False
    socket: socket.socket


def rdt_init(address: tuple[str, int], bind: bool = False) -> None:
    __RDT.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if bind:
        __RDT.socket.bind(address)
    else:
        __RDT.socket.connect(address)

    __RDT.init = True


def rdt_send(data: bytes, address: tuple[str, int] = None) -> int:
    if not __RDT.init:
        raise OSError(errno.EDESTADDRREQ, os.strerror(errno.EDESTADDRREQ) + ': Call rdt_init')
    elif len(data) > MAX_DATA_SIZE:
        raise OSError(errno.EMSGSIZE, os.strerror(errno.EMSGSIZE))

    time.sleep(1e-6)  # throttling

    pkt = __make_pkt(data)
    return __udt_send(pkt, address)


def rdt_recv() -> tuple[bytes, tuple[str, int]]:
    if not __RDT.init:
        raise OSError(errno.EDESTADDRREQ, os.strerror(errno.EDESTADDRREQ) + ': Call rdt_init')

    pkt, address = __udt_recv()
    data = __extract(pkt)

    return data, address


def __make_pkt(data: bytes) -> bytes:
    return data


def __extract(pkt: bytes) -> bytes:
    return pkt


def __udt_send(pkt: bytes, address: tuple[str, int] = None) -> int:
    if address is not None:
        return __RDT.socket.sendto(pkt, address)
    else:
        return __RDT.socket.send(pkt)


def __udt_recv() -> tuple[bytes, tuple[str, int]]:
    return __RDT.socket.recvfrom(MAX_DATA_SIZE)


__all__ = ['rdt_init', 'rdt_send', 'rdt_recv']
