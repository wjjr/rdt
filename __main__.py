import argparse

from client import run_client
from server import run_server

LOOPBACK_HOSTNAME = '127.0.0.1'
DEFAULT_PORT = 21678

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RDT Application')
    subparsers = parser.add_subparsers(title='Application type', dest='type',
                                       metavar='[server | client]', required=True)

    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument('-u', dest='simulate_unreliability', action='store_true',
                               help=f"simulate unreliability (default: enabled if hostname is {LOOPBACK_HOSTNAME})")
    common_parser.add_argument('-c', dest='num_packets', type=int, default=100000,
                               help=f"number of packets to send/receive (default: 100000)")

    server_parser = subparsers.add_parser('server', aliases=['s'], help='RDT Server', parents=[common_parser])
    server_parser.add_argument('hostname', type=str, default=LOOPBACK_HOSTNAME, nargs='?',
                               help=f"host address to listen in (default: {LOOPBACK_HOSTNAME})")
    server_parser.add_argument('port', type=int, default=DEFAULT_PORT, nargs='?',
                               help=f"port number to listen in (default: {DEFAULT_PORT})")

    client_parser = subparsers.add_parser('client', aliases=['c'], help='RDT Client', parents=[common_parser])
    client_parser.add_argument('hostname', type=str, default=LOOPBACK_HOSTNAME, nargs='?',
                               help=f"server address (default: {LOOPBACK_HOSTNAME})")
    client_parser.add_argument('port', type=int, default=DEFAULT_PORT, nargs='?',
                               help=f"server port number (default: {DEFAULT_PORT})")

    args = parser.parse_args()

    address = (args.hostname, args.port)
    simulate_unreliability = args.simulate_unreliability or args.hostname == LOOPBACK_HOSTNAME

    if args.type[0] == 's':
        run_server(address, simulate_unreliability, args.num_packets)
    else:
        run_client(address, simulate_unreliability, args.num_packets)
