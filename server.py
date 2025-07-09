import socket
import threading
import json
import random
import os

# Colores y abreviaturas
COLORS = ['red', 'green', 'yellow', 'blue']
COLOR_ABBR = {'red': 'R', 'green': 'G', 'yellow': 'Y', 'blue': 'B'}

# Casillas seguras (índices en el recorrido principal)
SAFE_POSITIONS = [0, 8, 13, 21, 26, 34, 39, 47]

# Posiciones de inicio en el recorrido principal para cada color
START_POSITIONS = {
    'red': 0,
    'green': 13,
    'yellow': 26,
    'blue': 39
}

# Casillas de entrada al pasillo final para cada color
HOME_ENTRY = {
    'red': 51,
    'green': 12,
    'yellow': 25,
    'blue': 38
}

# Longitud del recorrido principal y del pasillo final
MAIN_PATH_LEN = 52
HOME_PATH_LEN = 6

USERS_FILE = 'users.json'

class Player:
    def __init__(self, username, nombre, color):
        self.username = username
        self.nombre = nombre
        self.color = color
        self.pieces = [f"{color[0].upper()}{i+1}" for i in range(4)]
        self.connected = True

class Piece:
    def __init__(self, color, number):
        self.color = color
        self.number = number  # 1-4
        self.id = f"{COLOR_ABBR[color]}{number}"
        self.position = -1  # -1: base, 0-51: recorrido, 100-106: pasillo final/meta
        self.finished = False

    def is_at_base(self):
        return self.position == -1

    def is_on_board(self):
        return 0 <= self.position < MAIN_PATH_LEN

    def is_in_home_path(self):
        return 100 <= self.position <= 100 + HOME_PATH_LEN

    def is_at_goal(self):
        return self.position == 100 + HOME_PATH_LEN

class Board:
    def __init__(self, players_colors):
        self.pieces = []
        for color in players_colors:
            for i in range(1, 5):
                self.pieces.append(Piece(color, i))
        # Estado: {piece_id: position}
        self.state = {piece.id: piece.position for piece in self.pieces}
        self.players_colors = players_colors

    def get_piece(self, piece_id):
        for p in self.pieces:
            if p.id == piece_id:
                return p
        return None

    def get_pieces_by_color(self, color):
        return [p for p in self.pieces if p.color == color]

    def get_pieces_at(self, position):
        return [p for p in self.pieces if p.position == position]

    def is_safe_square(self, pos):
        return pos in SAFE_POSITIONS

    def can_enter_board(self, piece, dice_value):
        # Solo puede salir de base con 6 y si la casilla de salida no está bloqueada
        if piece.is_at_base() and dice_value == 6:
            start_pos = START_POSITIONS[piece.color]
            # No puede entrar si hay bloqueo propio
            others = [p for p in self.get_pieces_at(start_pos) if p.color == piece.color]
            return len(others) < 2
        return False

    def can_move(self, piece, dice_value):
        if piece.finished:
            return False
        if piece.is_at_base():
            return self.can_enter_board(piece, dice_value)
        # Si está en recorrido principal
        if piece.is_on_board():
            steps_left = (HOME_ENTRY[piece.color] - piece.position) % MAIN_PATH_LEN
            if dice_value > steps_left:
                # ¿Puede entrar al pasillo final?
                home_steps = dice_value - steps_left - 1
                if home_steps < HOME_PATH_LEN:
                    # Verifica bloqueo en pasillo final
                    home_pos = 100 + home_steps
                    others = [p for p in self.get_pieces_at(home_pos) if p.color == piece.color]
                    return len(others) < 2
                else:
                    return False
            else:
                # Verifica bloqueo en destino
                dest = (piece.position + dice_value) % MAIN_PATH_LEN
                others = [p for p in self.get_pieces_at(dest) if p.color == piece.color]
                return len(others) < 2
        # Si está en pasillo final
        if piece.is_in_home_path():
            dest = piece.position + dice_value
            if dest > 100 + HOME_PATH_LEN:
                return False
            others = [p for p in self.get_pieces_at(dest) if p.color == piece.color]
            return len(others) < 2
        return False

    def move_piece(self, piece, dice_value):
        if not self.can_move(piece, dice_value):
            return False
        if piece.is_at_base():
            # Sale de base
            piece.position = START_POSITIONS[piece.color]
        elif piece.is_on_board():
            steps_left = (HOME_ENTRY[piece.color] - piece.position) % MAIN_PATH_LEN
            if dice_value > steps_left:
                # Entra al pasillo final
                home_steps = dice_value - steps_left - 1
                piece.position = 100 + home_steps
            else:
                # Avanza en el recorrido principal
                piece.position = (piece.position + dice_value) % MAIN_PATH_LEN
        elif piece.is_in_home_path():
            piece.position += dice_value
            if piece.position == 100 + HOME_PATH_LEN:
                piece.finished = True
        # Actualiza estado
        self.state[piece.id] = piece.position
        return True

    def check_capture(self, piece):
        # Solo si no es casilla segura
        if piece.is_on_board() and not self.is_safe_square(piece.position):
            others = [p for p in self.get_pieces_at(piece.position) if p.color != piece.color and not p.is_at_base() and not p.finished]
            if len(others) == 1:
                captured = others[0]
                captured.position = -1
                captured.finished = False
                self.state[captured.id] = -1
                return captured.id
        return None

    def check_block(self, position, color):
        # Devuelve True si hay bloqueo propio en esa casilla
        pieces = [p for p in self.get_pieces_at(position) if p.color == color]
        return len(pieces) >= 2

    def get_board_state(self):
        return {p.id: p.position for p in self.pieces}

class GameManager:
    def __init__(self, player_colors):
        self.board = Board(player_colors)
        self.player_colors = player_colors
        self.current_turn = 0  # índice en player_colors
        self.dice_value = None
        self.six_count = 0  # Para controlar tres 6 seguidos
        self.last_piece_moved = None

    def current_player(self):
        return self.player_colors[self.current_turn]

    def roll_dice(self):
        self.dice_value = random.randint(1, 6)
        return self.dice_value

    def can_player_move(self, color):
        # ¿El jugador actual puede mover alguna ficha con el valor del dado?
        for piece in self.board.get_pieces_by_color(color):
            if self.board.can_move(piece, self.dice_value):
                return True
        return False

    def move_piece(self, piece_id):
        piece = self.board.get_piece(piece_id)
        if not piece or piece.color != self.current_player():
            return False, "No es tu turno o ficha inválida"
        if not self.board.can_move(piece, self.dice_value):
            return False, "Movimiento no permitido"
        self.board.move_piece(piece, self.dice_value)
        self.last_piece_moved = piece
        # Captura
        captured = self.board.check_capture(piece)
        # Avance de 20 si captura
        if captured:
            self.board.move_piece(piece, 20)
        # Meta
        if piece.is_at_goal():
            # Puedes agregar lógica de victoria aquí
            pass
        # Control de 6 seguidos
        if self.dice_value == 6:
            self.six_count += 1
            if self.six_count == 3:
                # Regla: tres 6 seguidos, la última ficha movida vuelve a base
                piece.position = -1
                piece.finished = False
                self.board.state[piece.id] = -1
                self.six_count = 0
                self.next_turn()
                return True, "Tres 6 seguidos, ficha regresa a base"
            else:
                # Repite turno
                return True, "Sacaste 6, repites turno"
        else:
            self.six_count = 0
            self.next_turn()
            return True, "Turno terminado"
    
    def next_turn(self):
        self.current_turn = (self.current_turn + 1) % len(self.player_colors)
        self.dice_value = None
        self.last_piece_moved = None

# Funciones para enviar/recibir JSON por socket
def send_json(sock, data):
    msg = json.dumps(data) + "\n"
    sock.sendall(msg.encode())

def recv_json(sock):
    buffer = ""
    while True:
        chunk = sock.recv(4096).decode()
        if not chunk:
            return None
        buffer += chunk
        if "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            return json.loads(line)

# --- Usuarios ---
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# --- Servidor TCP ---
class LudoServer:
    def __init__(self, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.server_socket = None
        self.accept_thread = None
        self.running = False
        self._init_server()
        self.users = load_users()  # {username: {password, nombre, apellido}}
        self.clients = {}  # {username: (socket, thread)}
        self.lock = threading.Lock()
        self.game_state = None  # Estado central del juego
        self.player_order = []  # Lista de usernames en orden de turno
        self.player_colors = {}  # {username: color}
        self.current_turn_idx = 0
        self.last_dice_roll = None
        self.board = None

    def _init_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(8)
        print(f"Servidor escuchando en {self.host}:{self.port}")

    def start(self, with_input=True):
        self.running = True
        if self.accept_thread is None or not self.accept_thread.is_alive():
            self.accept_thread = threading.Thread(target=self.accept_clients, daemon=True)
            self.accept_thread.start()
        print("Servidor iniciado. Esperando conexiones...")
        if with_input:
            while self.running:
                cmd = input("[ADMIN] > ").strip()
                if cmd == 'usuarios':
                    print(self.users)
                elif cmd == 'salir':
                    print("Cerrando servidor...")
                    self.stop_server()
                    break
        else:
            while self.running:
                import time
                time.sleep(1)
        try:
            self.server_socket.close()
        except:
            pass

    def start_in_thread(self):
        if not self.running:
            # Si el socket fue cerrado, re-crear
            self._init_server()
            self.running = True
            self.accept_thread = threading.Thread(target=self.start, args=(False,), daemon=True)
            self.accept_thread.start()

    def stop_server(self):
        self.running = False
        # Desbloquear el accept() con una conexión dummy
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
        except Exception:
            pass
        try:
            self.server_socket.close()
        except:
            pass
        self.accept_thread = None
        # Limpiar estado de clientes y partida
        with self.lock:
            for user, (sock, _) in list(self.clients.items()):
                try:
                    sock.close()
                except:
                    pass
            self.clients.clear()
            self.player_order.clear()
            self.player_colors.clear()
            self.current_turn_idx = 0
            self.last_dice_roll = None
            self.board = None
        print("Servidor detenido.")

    def get_connected_users(self):
        with self.lock:
            return list(self.clients.keys())

    def get_stats(self):
        with self.lock:
            stats = {
                'usuarios_registrados': len(self.users),
                'usuarios_conectados': len(self.clients),
                'partida_en_curso': self.board is not None,
                'jugadores_partida': list(self.player_order) if self.board else [],
            }
            return stats

    def accept_clients(self):
        while True:
            client_sock, addr = self.server_socket.accept()
            print(f"Nueva conexión de {addr}")
            threading.Thread(target=self.handle_client, args=(client_sock,), daemon=True).start()

    def handle_client(self, client_sock):
        username = None
        try:
            while True:
                msg = recv_json(client_sock)
                if not msg:
                    break
                command = msg.get('command')
                payload = msg.get('payload', {})
                if command == 'login':
                    username = payload.get('username')
                    password = payload.get('password')
                    if username in self.users and self.users[username]['password'] == password:
                        send_json(client_sock, {'status': 'success'})
                        with self.lock:
                            self.clients[username] = (client_sock, threading.current_thread())
                            if username not in self.player_order:
                                self.player_order.append(username)
                            # Limita a 4 jugadores únicos
                            self.player_order = [u for u in self.player_order if u in self.clients][:4]
                        print(f"Usuario {username} autenticado")
                        # Si hay 2-4 jugadores, iniciar partida
                        with self.lock:
                            print("DEBUG: player_order =", self.player_order)
                            print("DEBUG: board is None?", self.board is None)
                            if 2 <= len(self.player_order) <= 4 and self.board is None:
                                self.start_game()
                    else:
                        send_json(client_sock, {'status': 'error', 'message': 'Credenciales incorrectas'})
                elif command == 'register':
                    username = payload.get('username')
                    password = payload.get('password')
                    nombre = payload.get('nombre')
                    apellido = payload.get('apellido')
                    if username in self.users:
                        send_json(client_sock, {'status': 'error', 'message': 'Usuario ya existe'})
                    else:
                        self.users[username] = {'password': password, 'nombre': nombre, 'apellido': apellido}
                        save_users(self.users)
                        send_json(client_sock, {'status': 'success'})
                        print(f"Usuario {username} registrado")
                elif command == 'roll_dice':
                    with self.lock:
                        if self.player_order and username == self.player_order[self.current_turn_idx]:
                            self.last_dice_roll = random.randint(1, 6)
                            color = self.player_colors[username]
                            # Verifica si puede mover alguna ficha
                            can_move = any(self.board.can_move(piece, self.last_dice_roll) for piece in self.board.get_pieces_by_color(color))
                            self.send_game_update(f"{username} ha lanzado el dado: {self.last_dice_roll}")
                            if not can_move:
                                # Si no puede mover y no sacó 6, pasa turno
                                if self.last_dice_roll != 6:
                                    self.current_turn_idx = (self.current_turn_idx + 1) % len(self.player_order)
                                    self.last_dice_roll = None
                                    self.send_game_update(f"Turno de {self.player_order[self.current_turn_idx]}")
                                    self.send_your_turn(self.player_order[self.current_turn_idx])
                                else:
                                    # Sacó 6 pero no puede mover, repite turno
                                    self.send_your_turn(username)
                            else:
                                self.send_your_turn(username)
                        else:
                            send_json(client_sock, {'status': 'error', 'message': 'No es tu turno'})
                elif command == 'move_piece':
                    piece_id = payload.get('piece_id')
                    with self.lock:
                        if self.player_order and username == self.player_order[self.current_turn_idx]:
                            piece = self.board.get_piece(piece_id)
                            if piece and self.board.can_move(piece, self.last_dice_roll):
                                self.board.move_piece(piece, self.last_dice_roll)
                                self.send_game_update(f"{username} movió la ficha {piece_id}")
                                # Avanzar turno (lógica simple, sin repetir por 6 aún)
                                self.current_turn_idx = (self.current_turn_idx + 1) % len(self.player_order)
                                self.last_dice_roll = None
                                self.send_game_update(f"Turno de {self.player_order[self.current_turn_idx]}")
                                self.send_your_turn(self.player_order[self.current_turn_idx])
                            else:
                                send_json(client_sock, {'status': 'error', 'message': 'Movimiento no válido'})
                        else:
                            send_json(client_sock, {'status': 'error', 'message': 'No es tu turno'})
                else:
                    send_json(client_sock, {'status': 'error', 'message': 'Comando no soportado'})
        except Exception as e:
            print(f"Error con cliente {username}: {e}")
        finally:
            if username:
                with self.lock:
                    if username in self.clients:
                        del self.clients[username]
                    if username in self.player_order:
                        self.player_order.remove(username)
            client_sock.close()
            print(f"Cliente {username} desconectado")

    def start_game(self):
        print("Iniciando partida con jugadores:", self.player_order)
        random.shuffle(COLORS)
        self.player_colors = {user: COLORS[i] for i, user in enumerate(self.player_order)}
        print("Colores asignados:", self.player_colors)
        self.board = Board([self.player_colors[user] for user in self.player_order])
        self.current_turn_idx = 0
        self.last_dice_roll = None
        self.send_game_update("¡Partida iniciada!")
        self.send_your_turn(self.player_order[self.current_turn_idx])

    def send_game_update(self, message=""):
        board_state = self.board.get_board_state() if self.board else {}
        for user, (sock, _) in list(self.clients.items()):
            payload = {
                'board_state': board_state,
                'current_turn': self.player_order[self.current_turn_idx] if self.player_order else None,
                'last_dice_roll': self.last_dice_roll,
                'message': message,
                'your_color': self.player_colors.get(user)
            }
            try:
                send_json(sock, {'command': 'game_update', 'payload': payload})
            except:
                pass

    def send_your_turn(self, username):
        if username in self.clients:
            sock, _ = self.clients[username]
            try:
                send_json(sock, {'command': 'your_turn'})
            except:
                pass

if __name__ == "__main__":
    server = LudoServer()
    server.start()