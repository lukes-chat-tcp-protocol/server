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
    def get_handlers_by_username(self, username):
        handlers = []
        for sid in self.conn_list:
            if self.conn_list[sid].mode.startswith('TO'):
                if self.conn_list[sid].client_env['username'] == username:
                    handlers.append(self.conn_list[sid])
        return handlers

class handleToMode:
    def __init__(self, sock, addr, mode, comms, session_manager):
        self.sock = sock
        self.comms = comms
        self.mode = mode
        self.addr = addr
        self.session_manager = session_manager
        self.sid = self.session_manager.add_conn(self)
        print('New connection from {} with mode {} and SID {}'.format(addr[0], mode, self.sid))
        self.client_env = {
            'login': False,
            'permission_level': None,
            'mode': mode,
            'FROM_sid': None,
            'username': None
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
                    self.client_env['username'] = username

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
                self.comms.send(self.sock, self.client_env, b'ACK')
        elif args[0] == 'SEND':
            if check_login(1):
                try:
                    username = base64.b64decode(args[1].encode()).decode('utf-8')
                    message = args[2]
                except IndexError:
                    self.comms.send(self.sock, self.client_env, b'ERROR InvalidCommand')
                except:
                    self.comms.send(self.sock, self.client_env, b'ERROR InvalidB64Code')
                else:
                    handlers = self.session_manager.get_handlers_by_username(username)
                    for handler in handlers:
                        handler = self.session_manager.get_handler_from_id(handler.client_env['FROM_sid'])
                        if not handler == None:
                            handler.msg_queue.append('RECV {} {}'.format(base64.b64encode(self.client_env['username'].encode()).decode('utf-8'), message).encode())
                    self.comms.send(self.sock, self.client_env, b'ACK')
        elif args[0] == 'CREATE_ACCOUNT':
            if check_login(2):
                try:
                    username = base64.b64decode(args[1].encode()).decode('utf-8')
                    password = base64.b64decode(args[2].encode()).decode('utf-8')
                    permission_level = int(args[3])
                except IndexError:
                    self.comms.send(self.sock, self.client_env, b'ERROR InvalidCommand')
                except ValueError:
                    self.comms.send(self.sock, self.client_env, b'ERROR InvalidCommand')
                except:
                    self.comms.send(self.sock, self.client_env, b'ERROR InvalidB64Code')
                else:
                    if self.client_env['permission_level'] > permission_level:
                        auth.create_account(username, password, permission_level)
                        self.comms.send(self.sock, self.client_env, b'ACK')
                    else:
                        self.comms.send(self.sock, self.client_env, b'ERROR PermissionDenied')
        elif args[0] == 'DELETE_ACCOUNT':
            if check_login(3):
                try:
                    username = base64.b64decode(args[1].encode()).decode('utf-8')
                except IndexError:
                    self.comms.send(self.sock, self.client_env, b'ERROR InvalidCommand')
                else:
                    if auth.delete_account(username):
                        self.comms.send(self.sock, self.client_env, b'ACK')
                    else:
                        self.comms.send(self.sock, self.client_env, b'ERROR AccountNotFound')
        elif args[0] == 'CHANGE_PERM_LEVEL':
            if check_login(2):
                try:
                    int(args[2])
                    username = base64.b64decode(args[1].encode()).decode('utf-8')
                except IndexError: 
                    self.comms.send(self.sock, self.client_env, b'ERROR InvalidCommand')
                except:
                    self.comms.send(self.sock, self.client_env, b'ERROR InvalidB64Code')
                else:
                    account_cpl = auth.get_perm_level(username)
                    if self.client_env['permission_level'] > int(args[2]) and not username == self.client_env['username'] and account_cpl < self.client_env['permission_level']:
                        if auth.change_perm_level(username, int(args[2])):
                            self.comms.send(self.sock, self.client_env, b'ACK')
                        else:
                            self.comms.send(self.sock, self.client_env, b'ERROR AccountNotFound')
                    else:
                        self.comms.send(self.sock, self.client_env, b'ERROR PermissionDenied')
        elif args[0] == 'CHANGE_PASSWORD':
            if check_login(1):
                try:
                    current_password = base64.b64decode(args[1].encode()).decode('utf-8')
                    new_password = base64.b64decode(args[2].encode()).decode('utf-8')
                except IndexError:
                    self.comms.send(self.sock, self.client_env, b'ERROR InvalidCommand')
                except:
                    self.comms.send(self.sock, self.client_env, b'ERROR InvalidB64Code')
                else:
                    if auth.change_password(self.client_env['username'], current_password, new_password):
                        self.comms.send(self.sock, self.client_env, b'ACK')
                    else:
                        self.comms.send(self.sock, self.client_env, b'ERROR PermissionDenied')
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
            print('New connection from {} with mode {} and SID {}'.format(addr[0], mode, self.sid))
            self.to_conn.client_env['FROM_sid'] = self.sid
            brk = False
            while True:
                for msg in self.msg_queue:
                    self.comms.send(self.sock, {'mode': mode}, msg)
                    if not self.mode.endswith('_TELNET'):
                        recv = self.comms.recv(self.sock, {'mode': mode}, 1024).decode('utf-8')
                        if recv == 'ACK':
                            pass
                        elif recv.startswith('ERROR'):
                            print('Warning: Connection {} sent back error: {}'.format(self.sid, recv.split(' ')[1]))
                        else:
                            self.sock.close()
                            brk = True
                            print('Warning: Connection {} closed after sending invalid response'.format(self.sid))
                self.msg_queue = []
                if brk:
                    break
