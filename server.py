import socket_comms

comms = socket_comms.SocketCommunication('0.0.0.0', 3462)

comms.start_server()
