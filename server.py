import socket_comms
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--bind-address', type=str, help='IP Address to bind to')
parser.add_argument('-p', '--port', type=int, help='Port to bind to')
parser.add_argument('--cert', type=str, help='SSL Certificate to use')
parser.add_argument('--key', type=str, help='SSL Key to use')
parser.add_argument('--insecure', action='store_true')

args = parser.parse_args()

if args.bind_address == None:
    args.bind_address = '0.0.0.0'

if args.cert == None:
    args.insecure = True

if args.port == None:
    if args.insecure:
        args.port = 3462
    else:
        args.port = 3463

comms = socket_comms.SocketCommunication(args)

comms.start_server()
