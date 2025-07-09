import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import threading
from server import LudoServer

USERS_FILE = 'users.json'

class AdminGUI:
    def __init__(self, master):
        self.master = master
        master.title("Administrador Ludo - Servidor")
        self.server = LudoServer()
        self.server.start_in_thread()
        self.users = self.server.users
        self.build_gui()
        self.update_connected_users()
        self.update_stats()

    def build_gui(self):
        self.tab_control = ttk.Notebook(self.master)
        self.tab_users = ttk.Frame(self.tab_control)
        self.tab_game = ttk.Frame(self.tab_control)
        self.tab_stats = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_users, text='Usuarios')
        self.tab_control.add(self.tab_game, text='Partida')
        self.tab_control.add(self.tab_stats, text='Estadísticas')
        self.tab_control.pack(expand=1, fill='both')
        self.build_users_tab()
        self.build_game_tab()
        self.build_stats_tab()

    def build_users_tab(self):
        frame = self.tab_users
        self.users_listbox = tk.Listbox(frame, width=40)
        self.users_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.refresh_users_list()
        btn_frame = tk.Frame(frame)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        btn_add = tk.Button(btn_frame, text="Agregar Usuario", command=self.add_user)
        btn_add.pack(fill=tk.X, pady=5)
        btn_del = tk.Button(btn_frame, text="Borrar Usuario", command=self.delete_user)
        btn_del.pack(fill=tk.X, pady=5)

    def build_game_tab(self):
        frame = self.tab_game
        self.lbl_status = tk.Label(frame, text="Estado: Esperando jugadores", font=("Arial", 12))
        self.lbl_status.pack(pady=10)
        btn_start = tk.Button(frame, text="Iniciar Partida", command=self.start_game)
        btn_start.pack(pady=5)
        btn_stop = tk.Button(frame, text="Detener Partida", command=self.stop_game)
        btn_stop.pack(pady=5)
        self.connected_users_label = tk.Label(frame, text="Usuarios conectados: 0")
        self.connected_users_label.pack(pady=10)
        self.connected_users_listbox = tk.Listbox(frame, width=30)
        self.connected_users_listbox.pack(pady=5)
        self.lbl_ready = tk.Label(frame, text="Jugadores listos (autenticados):")
        self.lbl_ready.pack(pady=5)
        self.ready_users_listbox = tk.Listbox(frame, width=30)
        self.ready_users_listbox.pack(pady=5)

    def build_stats_tab(self):
        frame = self.tab_stats
        self.stats_text = tk.Text(frame, height=15, width=60)
        self.stats_text.pack(padx=10, pady=10)
        self.stats_text.insert(tk.END, "Estadísticas del servidor aparecerán aquí...\n")
        self.stats_text.config(state=tk.DISABLED)

    def refresh_users_list(self):
        self.users_listbox.delete(0, tk.END)
        for user, data in self.server.users.items():
            self.users_listbox.insert(tk.END, f"{user} - {data.get('nombre','')} {data.get('apellido','')}")

    def add_user(self):
        popup = tk.Toplevel(self.master)
        popup.title("Agregar Usuario")
        tk.Label(popup, text="Login:").grid(row=0, column=0)
        entry_login = tk.Entry(popup)
        entry_login.grid(row=0, column=1)
        tk.Label(popup, text="Clave:").grid(row=1, column=0)
        entry_pass = tk.Entry(popup, show="*")
        entry_pass.grid(row=1, column=1)
        tk.Label(popup, text="Nombre:").grid(row=2, column=0)
        entry_nombre = tk.Entry(popup)
        entry_nombre.grid(row=2, column=1)
        tk.Label(popup, text="Apellido:").grid(row=3, column=0)
        entry_apellido = tk.Entry(popup)
        entry_apellido.grid(row=3, column=1)
        def do_add():
            login = entry_login.get().strip()
            pw = entry_pass.get().strip()
            nombre = entry_nombre.get().strip()
            apellido = entry_apellido.get().strip()
            if not login or not pw or not nombre or not apellido:
                messagebox.showerror("Error", "Todos los campos son requeridos")
                return
            if login in self.server.users:
                messagebox.showerror("Error", "El usuario ya existe")
                return
            self.server.users[login] = {"password": pw, "nombre": nombre, "apellido": apellido}
            with open(USERS_FILE, 'w') as f:
                json.dump(self.server.users, f, indent=2)
            self.refresh_users_list()
            popup.destroy()
        btn_ok = tk.Button(popup, text="Agregar", command=do_add)
        btn_ok.grid(row=4, column=0, columnspan=2, pady=10)

    def delete_user(self):
        sel = self.users_listbox.curselection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un usuario para borrar")
            return
        user_line = self.users_listbox.get(sel[0])
        login = user_line.split(' - ')[0]
        if messagebox.askyesno("Confirmar", f"¿Borrar usuario {login}?"):
            if login in self.server.users:
                del self.server.users[login]
                with open(USERS_FILE, 'w') as f:
                    json.dump(self.server.users, f, indent=2)
                self.refresh_users_list()

    def start_game(self):
        player_order = self.server.player_order
        if len(player_order) < 2 or len(player_order) > 4:
            messagebox.showwarning("No se puede iniciar", "Debe haber entre 2 y 4 jugadores conectados y autenticados para iniciar la partida.")
            return
        self.server.start_game()
        self.lbl_status.config(text="Estado: Partida iniciada")

    def stop_game(self):
        self.server.stop_server()
        self.lbl_status.config(text="Estado: Partida detenida")

    def update_connected_users(self):
        users = self.server.get_connected_users()
        self.connected_users_label.config(text=f"Usuarios conectados: {len(users)}")
        self.connected_users_listbox.delete(0, tk.END)
        for u in users:
            self.connected_users_listbox.insert(tk.END, u)

        # Actualiza la lista de jugadores listos
        self.ready_users_listbox.delete(0, tk.END)
        for u in self.server.player_order:
            self.ready_users_listbox.insert(tk.END, u)
        self.master.after(2000, self.update_connected_users)

    def update_stats(self):
        stats = self.server.get_stats()
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, f"Usuarios registrados: {stats['usuarios_registrados']}\n")
        self.stats_text.insert(tk.END, f"Usuarios conectados: {stats['usuarios_conectados']}\n")
        self.stats_text.insert(tk.END, f"Partida en curso: {'Sí' if stats['partida_en_curso'] else 'No'}\n")
        self.stats_text.insert(tk.END, f"Jugadores en partida: {', '.join(stats['jugadores_partida'])}\n")
        self.stats_text.config(state=tk.DISABLED)
        self.master.after(3000, self.update_stats)

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminGUI(root)
    root.mainloop() 