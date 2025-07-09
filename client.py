import socket
import json
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox
import random

COLORS = ['red', 'green', 'yellow', 'blue']
COLOR_MAP = {
    'red': '#e74c3c',
    'green': '#27ae60',
    'yellow': '#f1c40f',
    'blue': '#2980b9'
}
COLOR_ABBR = {'red': 'R', 'green': 'G', 'yellow': 'Y', 'blue': 'B'}

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

class Board:
    def __init__(self, canvas, cell_size=40):
        self.canvas = canvas
        self.cell_size = cell_size
        self.grid = self._create_grid()
        self.main_path = self._define_main_path()
        self.home_paths = self._define_home_paths()
        self.base_coords = self._define_base_coords()
        self.start_offsets = {
            'red': 0,    # (6,1)
            'green': 13, # (1,8)
            'yellow': 26,# (8,13)
            'blue': 39   # (13,6)
        }

    def _create_grid(self):
        # Matriz fija según la estructura exacta del tablero
        board_ids = [
            ["base_red", "base_red", "base_red", "base_red", "base_red", "base_red", "path",      "path",      "path",      "base_green","base_green","base_green","base_green","base_green","base_green"],
            ["base_red", "base_red", "base_red", "base_red", "base_red", "base_red", "path",      "home_green","path",      "base_green","base_green","base_green","base_green","base_green","base_green"],
            ["base_red", "base_red", "base_red", "base_red", "base_red", "base_red", "path",      "home_green","path",      "base_green","base_green","base_green","base_green","base_green","base_green"],
            ["base_red", "base_red", "base_red", "base_red", "base_red", "base_red", "path",      "home_green","path",      "base_green","base_green","base_green","base_green","base_green","base_green"],
            ["base_red", "base_red", "base_red", "base_red", "base_red", "base_red", "path",      "home_green","path",      "base_green","base_green","base_green","base_green","base_green","base_green"],
            ["base_red", "base_red", "base_red", "base_red", "base_red", "base_red", "path",      "home_green","path",      "base_green","base_green","base_green","base_green","base_green","base_green"],
            ["path",     "start_red", "path",      "path",      "path",      "path",      "meta_tri",  "meta_tri",  "meta_tri",  "path",      "path",      "path",      "path",      "path",      "path"      ],
            ["path",     "home_red",  "home_red",  "home_red",  "home_red",  "home_red",  "meta_tri",  "meta",      "meta_tri",  "home_yellow","home_yellow","home_yellow","home_yellow","home_yellow","path"      ],
            ["path",     "path",      "path",      "path",      "path",      "path",      "meta_tri",  "meta_tri",  "meta_tri",  "path",      "path",      "path",      "path",      "start_yellow","path"    ],
            ["base_blue","base_blue","base_blue","base_blue","base_blue","base_blue","path",      "home_blue", "path",      "base_yellow","base_yellow","base_yellow","base_yellow","base_yellow","base_yellow"],
            ["base_blue","base_blue","base_blue","base_blue","base_blue","base_blue","path",      "home_blue", "path",      "base_yellow","base_yellow","base_yellow","base_yellow","base_yellow","base_yellow"],
            ["base_blue","base_blue","base_blue","base_blue","base_blue","base_blue","path",      "home_blue", "path",      "base_yellow","base_yellow","base_yellow","base_yellow","base_yellow","base_yellow"],
            ["base_blue","base_blue","base_blue","base_blue","base_blue","base_blue","path",      "home_blue", "path",      "base_yellow","base_yellow","base_yellow","base_yellow","base_yellow","base_yellow"],
            ["base_blue","base_blue","base_blue","base_blue","base_blue","base_blue","start_blue","home_blue", "path",      "base_yellow","base_yellow","base_yellow","base_yellow","base_yellow","base_yellow"],
            ["base_blue","base_blue","base_blue","base_blue","base_blue","base_blue","path",      "path",      "path",      "base_yellow","base_yellow","base_yellow","base_yellow","base_yellow","base_yellow"]
        ]
        return board_ids

    def _define_main_path(self):
        # Camino blanco, sentido horario, iniciando en la salida de rojo (6,1)
        path = []
        # 1. Rojo sube
        for i in range(6, 0, -1): path.append((i, 6))         # (6,6) a (1,6)
        # 2. Rojo a la derecha
        for i in range(6, 13): path.append((0, i))            # (0,6) a (0,12)
        # 3. Verde baja
        for i in range(1, 6): path.append((i, 12))            # (1,12) a (5,12)
        # 4. Verde a la derecha
        for i in range(12, 8, -1): path.append((6, i))        # (6,12) a (6,9)
        # 5. Amarillo baja
        for i in range(7, 13): path.append((i, 8))            # (7,8) a (12,8)
        # 6. Amarillo a la izquierda
        for i in range(9, 0, -1): path.append((13, i))        # (13,9) a (13,1)
        # 7. Azul sube
        for i in range(12, 6, -1): path.append((i, 0))        # (12,0) a (7,0)
        # 8. Azul a la derecha
        for i in range(1, 6): path.append((6, i))             # (6,1) a (6,5)
        return path[:52]

    def _define_home_paths(self):
        return {
            'red':   [(7,i) for i in range(1,7)],
            'green': [(i,7) for i in range(1,7)],
            'yellow':[(7,i) for i in range(13,7,-1)],
            'blue':  [(i,7) for i in range(13,7,-1)]
        }

    def _define_base_coords(self):
        return {
            'red':   [(1,1), (1,4), (4,1), (4,4)],
            'green': [(1,10), (1,13), (4,10), (4,13)],
            'yellow':[(10,10), (10,13), (13,10), (13,13)],
            'blue':  [(10,1), (10,4), (13,1), (13,4)]
        }

    def is_walkable(self, row, col):
        """Devuelve True si la casilla es transitable para fichas (solo 'path')."""
        tipo = self.grid[row][col]
        return tipo == "path"

    def draw_board(self):
        c = self.canvas
        cell = self.cell_size
        c.delete("board")
        for row in range(15):
            for col in range(15):
                tipo = self.grid[row][col]
                if tipo == "base_red":
                    color = "#e74c3c"
                elif tipo == "base_green":
                    color = "#27ae60"
                elif tipo == "base_yellow":
                    color = "#f1c40f"
                elif tipo == "base_blue":
                    color = "#2980b9"
                elif tipo == "path":
                    color = "white"
                elif tipo == "home_red":
                    color = "#e74c3c"
                elif tipo == "home_green":
                    color = "#27ae60"
                elif tipo == "home_yellow":
                    color = "#f1c40f"
                elif tipo == "home_blue":
                    color = "#2980b9"
                elif tipo == "start_red":
                    color = "#888"
                elif tipo == "start_green":
                    color = "#888"
                elif tipo == "start_yellow":
                    color = "#888"
                elif tipo == "start_blue":
                    color = "#888"
                elif tipo == "meta":
                    color = "#f8f8f8"
                elif tipo == "meta_tri":
                    color = "#cccccc"
                else:
                    color = "white"
                c.create_rectangle(col*cell, row*cell, (col+1)*cell, (row+1)*cell, fill=color, outline="black", width=1, tags="board")
        # Centro: círculo blanco
        c.create_oval(6*cell,6*cell,9*cell,9*cell, fill="#f8f8f8", outline="black", width=2, tags="board")
        # Centro: triángulos de colores
        cx, cy = 7.5*cell, 7.5*cell
        r = 1.5*cell
        # Triángulo rojo (abajo izquierda)
        c.create_polygon(cx, cy, 6*cell, 9*cell, 6*cell, 6*cell, fill=COLOR_MAP['red'], outline="black", tags="board")
        # Triángulo verde (arriba izquierda)
        c.create_polygon(cx, cy, 6*cell, 6*cell, 9*cell, 6*cell, fill=COLOR_MAP['green'], outline="black", tags="board")
        # Triángulo amarillo (arriba derecha)
        c.create_polygon(cx, cy, 9*cell, 6*cell, 9*cell, 9*cell, fill=COLOR_MAP['yellow'], outline="black", tags="board")
        # Triángulo azul (abajo derecha)
        c.create_polygon(cx, cy, 9*cell, 9*cell, 6*cell, 9*cell, fill=COLOR_MAP['blue'], outline="black", tags="board")

    def get_canvas_coords_from_grid(self, row, col):
        cell = self.cell_size
        return (col*cell + cell/2, row*cell + cell/2)

    def get_piece_canvas_coords(self, piece_id, position):
        # 1. Color de la ficha
        color = None
        idx = 0
        for c, abbr in COLOR_ABBR.items():
            if piece_id.startswith(abbr):
                color = c
                idx = int(piece_id[1]) - 1
                break
        if color is None:
            return (7.5*self.cell_size, 7.5*self.cell_size)
        # 2. En base
        if position == -1:
            row, col = self.base_coords[color][idx]
            return self.get_canvas_coords_from_grid(row, col)
        # 2.5. Primera salida: posición 0 (de la base a start_color)
        if position == 0:
            # Buscar la casilla 'start_color' en la cuadrícula
            for row in range(15):
                for col in range(15):
                    if self.grid[row][col] == f"start_{color}":
                        return self.get_canvas_coords_from_grid(row, col)
        # 3. En pasillo final
        if 101 <= position <= 106:
            home_idx = position - 101
            if 0 <= home_idx < 6:
                row, col = self.home_paths[color][home_idx]
                return self.get_canvas_coords_from_grid(row, col)
            else:
                return (7.5*self.cell_size, 7.5*self.cell_size)
        # 4. Camino principal
        if 0 < position <= 51:
            abs_index = (position + self.start_offsets[color]) % 52
            row, col = self.main_path[abs_index]
            return self.get_canvas_coords_from_grid(row, col)
        # 5. Meta
        return (7.5*self.cell_size, 7.5*self.cell_size)

    def can_move_to(self, position):
        """Devuelve True si la posición lógica corresponde a una casilla 'path' blanca."""
        if 0 <= position < len(self.main_path):
            row, col = self.main_path[position]
            return self.grid[row][col] == "path"
        return False

    # Ejemplo de uso en la lógica de movimiento (ajusta donde corresponda):
    # if self.can_move_to(nueva_posicion):
    #     # Permitir movimiento
    # else:
    #     # No permitir movimiento

class GameWindow:
    def __init__(self, root, username, sock):
        self.root = root
        self.username = username
        self.sock = sock
        self.root.title(f"Ludo - Jugador: {username}")
        self.board_state = {}  # {piece_id: position}
        self.current_turn = None
        self.last_dice_roll = None
        self.message = ""
        self.listening = True
        self.my_color = None
        self.build_gui()
        threading.Thread(target=self.listen_server, daemon=True).start()

    def build_gui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=10, pady=10)
        self.canvas = tk.Canvas(main_frame, width=600, height=600, bg='white')
        self.canvas.grid(row=0, column=0, rowspan=4)
        self.board = Board(self.canvas, cell_size=40)
        self.board.draw_board()
        self.draw_all_pieces()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Panel de estado
        self.status_label = tk.Label(main_frame, text="Esperando jugadores...", font=("Arial", 14))
        self.status_label.grid(row=0, column=1, padx=20, pady=10, sticky="w")

        # Valor del dado
        self.dice_label = tk.Label(main_frame, text="Dado: -", font=("Arial", 18, "bold"))
        self.dice_label.grid(row=1, column=1, padx=20, pady=10, sticky="w")

        # Botón lanzar dado
        self.btn_dice = tk.Button(main_frame, text="Lanzar Dado", font=("Arial", 14), state=tk.DISABLED, command=self.roll_dice)
        self.btn_dice.grid(row=2, column=1, padx=20, pady=10, sticky="w")

    def draw_board(self):
        self.board.draw_board()

    def draw_all_pieces(self):
        self.canvas.delete("piece")
        cell = self.board.cell_size
        r = cell * 0.8
        for piece_id, pos in self.board_state.items():
            cx, cy = self.board.get_piece_canvas_coords(piece_id, pos)
            color = None
            for c, abbr in COLOR_ABBR.items():
                if piece_id.startswith(abbr):
                    color = c
                    break
            fill_color = COLOR_MAP[color] if color else 'gray'
            self.canvas.create_oval(cx - r/2, cy - r/2, cx + r/2, cy + r/2, fill=fill_color, outline="black", width=2, tags="piece")
            self.canvas.create_text(cx, cy, text=piece_id, font=("Arial", 12, "bold"), fill="white", tags="piece")
        if not self.board_state:
            for color in COLORS:
                for i in range(4):
                    cx, cy = self.board.get_piece_canvas_coords(f"{COLOR_ABBR[color]}{i+1}", -1)
                    self.canvas.create_oval(cx - r/2, cy - r/2, cx + r/2, cy + r/2, fill=COLOR_MAP[color], outline="black", width=2, tags="piece")
                    self.canvas.create_text(cx, cy, text=f"{COLOR_ABBR[color]}{i+1}", font=("Arial", 12, "bold"), fill="white", tags="piece")

    def roll_dice(self):
        try:
            send_json(self.sock, {"command": "roll_dice"})
            self.btn_dice.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo lanzar el dado: {e}")

    def on_canvas_click(self, event):
        # Solo permitir si es mi turno y hay valor de dado
        if self.current_turn != self.username or not self.last_dice_roll:
            return
        # Detectar ficha clickeada
        clicked_piece = self.get_clicked_piece(event.x, event.y)
        if clicked_piece and self.is_piece_movable(clicked_piece):
            try:
                send_json(self.sock, {"command": "move_piece", "payload": {"piece_id": clicked_piece}})
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo mover la ficha: {e}")

    def get_clicked_piece(self, x, y):
        cell = self.board.cell_size
        r = cell * 0.8
        for piece_id, pos in self.board_state.items():
            cx, cy = self.board.get_piece_canvas_coords(piece_id, pos)
            if (x - cx) ** 2 + (y - cy) ** 2 <= (r/2) ** 2:
                return piece_id
        return None

    def is_piece_movable(self, piece_id):
        if self.current_turn != self.username or not self.my_color:
            return False
        return piece_id.startswith(COLOR_ABBR[self.my_color])

    def get_player_color(self):
        # Deducción simple: busca la primera ficha del usuario
        for piece_id in self.board_state:
            if self.username and piece_id.startswith(self.username[0].upper()):
                for c, abbr in COLOR_ABBR.items():
                    if piece_id.startswith(abbr):
                        return c
        return None

    def listen_server(self):
        while self.listening:
            try:
                msg = self.recv_json()
                if not msg:
                    break
                command = msg.get('command')
                payload = msg.get('payload', {})
                if command == 'game_update':
                    self.board_state = payload.get('board_state', {})
                    self.current_turn = payload.get('current_turn')
                    self.last_dice_roll = payload.get('last_dice_roll')
                    self.message = payload.get('message', '')
                    self.my_color = payload.get('your_color', None)
                    self.update_gui()
                elif command == 'your_turn':
                    self.btn_dice.config(state=tk.NORMAL)
                    self.status_label.config(text="¡Es tu turno!")
                elif command == 'game_over':
                    winner = msg.get('winner', 'Desconocido')
                    messagebox.showinfo("Fin del juego", f"Ganador: {winner}")
                    self.listening = False
                    self.root.quit()
                elif command == 'error':
                    messagebox.showerror("Error", payload.get('message', 'Error desconocido'))
            except Exception as e:
                print(f"Error en listen_server: {e}")
                break

    def update_gui(self):
        # Actualiza el tablero y los textos
        self.draw_all_pieces()
        self.dice_label.config(text=f"Dado: {self.last_dice_roll if self.last_dice_roll is not None else '-'}")
        self.status_label.config(text=self.message)
        # Habilita/deshabilita el botón de dado según el turno
        if self.current_turn == self.username:
            self.btn_dice.config(state=tk.NORMAL)
        else:
            self.btn_dice.config(state=tk.DISABLED)

    def recv_json(self):
        buffer = ""
        while True:
            chunk = self.sock.recv(4096).decode()
            if not chunk:
                return None
            buffer += chunk
            if "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                return json.loads(line)

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Ludo - Login")
        self.sock = None
        self.build_gui()

    def build_gui(self):
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack()

        tk.Label(frame, text="IP del servidor:").grid(row=0, column=0, sticky="e")
        self.entry_ip = tk.Entry(frame)
        self.entry_ip.insert(0, "localhost")
        self.entry_ip.grid(row=0, column=1)

        tk.Label(frame, text="Puerto:").grid(row=1, column=0, sticky="e")
        self.entry_port = tk.Entry(frame)
        self.entry_port.insert(0, "9999")
        self.entry_port.grid(row=1, column=1)

        tk.Label(frame, text="Usuario:").grid(row=2, column=0, sticky="e")
        self.entry_user = tk.Entry(frame)
        self.entry_user.grid(row=2, column=1)

        tk.Label(frame, text="Clave:").grid(row=3, column=0, sticky="e")
        self.entry_pass = tk.Entry(frame, show="*")
        self.entry_pass.grid(row=3, column=1)

        self.btn_login = tk.Button(frame, text="Conectar", command=self.try_login)
        self.btn_login.grid(row=4, column=0, pady=10)

        self.btn_register = tk.Button(frame, text="Registrar", command=self.open_register_popup)
        self.btn_register.grid(row=4, column=1, pady=10)

    def try_login(self):
        ip = self.entry_ip.get().strip()
        port = int(self.entry_port.get().strip())
        user = self.entry_user.get().strip()
        pw = self.entry_pass.get().strip()
        if not user or not pw:
            messagebox.showerror("Error", "Usuario y clave requeridos")
            return
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((ip, port))
        except Exception as e:
            messagebox.showerror("Error de conexión", str(e))
            return
        # Enviar login
        msg = json.dumps({
            "command": "login",
            "payload": {"username": user, "password": pw}
        }) + "\n"
        try:
            self.sock.sendall(msg.encode())
            response = self.recv_json()
            if response.get('status') == 'success':
                messagebox.showinfo("Éxito", "Login correcto!")
                self.root.destroy()
                root2 = tk.Tk()
                GameWindow(root2, user, self.sock)
                root2.mainloop()
            else:
                messagebox.showerror("Login fallido", response.get('message', 'Error desconocido'))
                self.sock.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.sock.close()

    def open_register_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Registrar nuevo usuario")
        popup.transient(self.root)
        popup.grab_set()
        frame = tk.Frame(popup, padx=20, pady=20)
        frame.pack()

        tk.Label(frame, text="IP del servidor:").grid(row=0, column=0, sticky="e")
        entry_ip = tk.Entry(frame)
        entry_ip.insert(0, self.entry_ip.get())
        entry_ip.grid(row=0, column=1)

        tk.Label(frame, text="Puerto:").grid(row=1, column=0, sticky="e")
        entry_port = tk.Entry(frame)
        entry_port.insert(0, self.entry_port.get())
        entry_port.grid(row=1, column=1)

        tk.Label(frame, text="Usuario:").grid(row=2, column=0, sticky="e")
        entry_user = tk.Entry(frame)
        entry_user.grid(row=2, column=1)

        tk.Label(frame, text="Clave:").grid(row=3, column=0, sticky="e")
        entry_pass = tk.Entry(frame, show="*")
        entry_pass.grid(row=3, column=1)

        tk.Label(frame, text="Nombre:").grid(row=4, column=0, sticky="e")
        entry_nombre = tk.Entry(frame)
        entry_nombre.grid(row=4, column=1)

        tk.Label(frame, text="Apellido:").grid(row=5, column=0, sticky="e")
        entry_apellido = tk.Entry(frame)
        entry_apellido.grid(row=5, column=1)

        def do_register():
            ip = entry_ip.get().strip()
            port = int(entry_port.get().strip())
            user = entry_user.get().strip()
            pw = entry_pass.get().strip()
            nombre = entry_nombre.get().strip()
            apellido = entry_apellido.get().strip()
            if not user or not pw or not nombre or not apellido:
                messagebox.showerror("Error", "Todos los campos son requeridos")
                return
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((ip, port))
            except Exception as e:
                messagebox.showerror("Error de conexión", str(e))
                return
            msg = json.dumps({
                "command": "register",
                "payload": {
                    "username": user,
                    "password": pw,
                    "nombre": nombre,
                    "apellido": apellido
                }
            }) + "\n"
            try:
                sock.sendall(msg.encode())
                buffer = ""
                while True:
                    chunk = sock.recv(4096).decode()
                    if not chunk:
                        break
                    buffer += chunk
                    if "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        response = json.loads(line)
                        break
                if response.get('status') == 'success':
                    messagebox.showinfo("Éxito", "Usuario registrado correctamente")
                    popup.destroy()
                else:
                    messagebox.showerror("Registro fallido", response.get('message', 'Error desconocido'))
                sock.close()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                sock.close()

        btn_reg = tk.Button(frame, text="Registrar", command=do_register)
        btn_reg.grid(row=6, column=0, columnspan=2, pady=10)

    def recv_json(self):
        buffer = ""
        while True:
            chunk = self.sock.recv(4096).decode()
            if not chunk:
                return None
            buffer += chunk
            if "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                return json.loads(line)

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()