import base64
import auth_mgmt
import uuid

auth = auth_mgmt.AuthenticationManagement()

class SessionManager:
    def __init__(self):
        self.conn_list = {}
    def add_conn(self, handler):
        sid = str(uuid.uuid4())
        self.conn_list[sid] = handler
        return sid
    def get_handler_from_id(self, sid):
        try:
            handler = self.conn_list[sid]
        except IndexError:
            return None
        else:
            return handler
    def get_id_from_handler(self, handler):
        for sid in self.conn_list:
            if self.conn_list[sid] == handler:
                return sid

class handleToMode:
    def __init__(self, sock, addr, mode, comms, session_manager):
        self.sock = sock
        self.comms = comms
        self.mode = mode
        self.addr = addr
        self.session_manager = session_manager
        self.sid = self.session_manager.add_conn(self)
        print('New connection from {} with mode {}'.format(addr[0], mode))
        self.client_env = {
            'login': False,
            'permission_level': None,
            'mode': mode,
            'FROM_sid': None
        }
        self.comms.send(self.sock, self.client_env, b'READY')
        while True:
            try:
                recv = self.comms.recv(self.sock, self.client_env, 1024).decode('utf-8')
            except UnicodeDecodeError:
                self.comms.send(self.sock, self.client_env, b'ERROR InvalidCommand')
            else:
                args = recv.split(' ')
                resp = self.process_command(recv, args)
                if resp == 'break':
                        break
                else:
                    self.client_env = resp

        self.sock.close()
    
    def process_command(self, recv, args):
        def check_login(permission_level):
            if self.client_env['login']:
                if self.client_env['permission_level'] >= permission_level:
                    return True
                else:
                    self.comms.send(self.sock, self.client_env, b'ERROR PermissionDenied')
            else:
                self.comms.send(self.sock, self.client_env, b'ERROR LoginRequired')
                return False
        if args[0] == 'CLOSE':
            return 'break'
        elif args[0] == 'LOGIN':
            try:
                username = base64.b64decode(args[1]).decode('utf-8')
                password = base64.b64decode(args[2]).decode('utf-8')
            except IndexError:
                self.comms.send(self.sock, self.client_env, b'ERROR InvalidCommand')
            except:
                self.comms.send(self.sock, self.client_env, b'ERROR InvalidB64Code')
            else:
                auth_attempt = auth.login(username, password)
                if auth_attempt == False:
                    self.comms.send(self.sock, self.client_env, b'ERROR LoginFailed')
                else:
                    self.comms.send(self.sock, self.client_env, b'ACK')
                    self.client_env['login'] = True
                    self.client_env['permission_level'] = auth_attempt

            return self.client_env
        elif args[0] == 'CONSOLE_LOG':
            if check_login(3):
                try:
                    print(base64.b64decode(args[1].encode()).decode('utf-8'))
                except IndexError:
                    self.comms.send(self.sock, self.client_env, b'ERROR InvalidCommand')
                except:
                    self.comms.send(self.sock, self.client_env, b'ERROR InvalidB64Code')
                else:
                    self.comms.send(self.sock, self.client_env, b'ACK')
        elif args[0] == 'GET_ID':
            self.comms.send(self.sock, self.client_env, self.sid.encode())
        elif args[0] == 'ECHO_FROM':
            if self.client_env['FROM_sid'] == None:
                self.comms.send(self.sock, self.client_env, b'ERROR NoFROMSession')
            else:
                from_handler = self.session_manager.get_handler_from_id(self.client_env['FROM_sid'])
                from_handler.msg_queue.append(recv.encode())
        else:
            self.comms.send(self.sock, self.client_env, b'ERROR InvalidCommand')
        return self.client_env

class handleFromMode:
    def __init__(self, sock, addr, mode, comms, session_manager, sid):
        self.sock = sock
        self.comms = comms
        self.mode = mode
        self.addr = addr
        self.session_manager = session_manager
        self.sid = self.session_manager.add_conn(self)
        self.to_conn_sid = sid
        self.to_conn = self.session_manager.get_handler_from_id(self.to_conn_sid)
        self.msg_queue = []
        if self.to_conn == None:
            self.comms.send(self.sock, {'mode': mode}, b'TO Connection not found')
            self.sock.close()
        else:
            print('New connection from {} with mode {}'.format(addr[0], mode))
            self.to_conn.client_env['FROM_sid'] = self.sid
            while True:
                for msg in self.msg_queue:
                    self.comms.send(self.sock, {'mode': mode}, msg)
                self.msg_queue = []
