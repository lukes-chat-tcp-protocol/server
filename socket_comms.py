import socket
import threading
import base64
import auth_mgmt
import cmd_mgmt
import ssl

auth = auth_mgmt.AuthenticationManagement()

class SocketCommunication:
    def __init__(self, args):
        if args.insecure:
            print('WARNING! Running in insecure mode. Only do this if this is a development enviorment.')
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            if args.key == None:
                self.ssl_context.load_cert_chain(certfile=args.cert)
            else:
                self.ssl_context.load_cert_chain(certfile=args.cert, keyfile=args.key)
            self.sock = self.ssl_context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self.bind_address = args.bind_address
        self.port = args.port
        self.conns = []
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    def start_server(self):
        self.sock.bind((self.bind_address, self.port))
        self.sock.listen(0)
        print('Listening for connections on {}:{}'.format(self.bind_address, self.port))
        while True:
            conn, addr = self.sock.accept()
            threading.Thread(target=self.handle_connection, args=[conn, addr]).start()
    
    def send(self, conn, client_env, data):
        if client_env['mode'].endswith('_TELNET'):
            conn.send(data + b'\r\n')
        else:
            conn.send(data)
    def recv(self, conn, client_env, size):
        if client_env['mode'].endswith('_TELNET'):
            data = conn.recv(size).replace(b'\r', b'').replace(b'\n', b'')
        else:
            data = conn.recv(size)
        return data
    
    def handle_connection(self, conn, addr):
        self.conns.append({
            'conn_obj': conn,
            'address': addr[0]
        })
        conn.send(b'SEND_MODE ')
        try:
            mode = conn.recv(1024).decode('utf-8').replace('\n', '').replace('\r', '')
        except UnicodeDecodeError:
            conn.close()
        else:
            if mode.startswith('TO'):
                cmd = cmd_mgmt.handleToMode(conn, addr, mode, self)
            elif mode.startswith('FROM'):
                self.send(conn, {'mode': mode}, b'Mode temporarily not supported')
                conn.close()
            else:
                self.send(conn, {'mode': mode}, b'Unknown mode')
                conn.close()
