import pygame
import sys
import random
import math
from enum import Enum
from typing import List, Tuple, Dict, Optional
import os

# Inicializar pygame
pygame.init()

# Constantes
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 900
FPS = 60
BOARD_SIZE = 700
BOARD_OFFSET_X = 100
BOARD_OFFSET_Y = 100

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (237, 28, 36)
GREEN = (34, 177, 76)
BLUE = (0, 162, 232)
YELLOW = (255, 242, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)

# Estados del juego
class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    ROLLING_DICE = "rolling_dice"
    MOVING_PIECE = "moving_piece"
    GAME_OVER = "game_over"
    PAUSED = "paused"

# Tamaño de las casillas del tablero
CELL_SIZE = 50

# Recorrido principal (52 casillas, sentido agujas del reloj)
MAIN_PATH = [
    # Desde la salida roja (abajo izquierda, sube)
    *[(BOARD_OFFSET_X + CELL_SIZE * 6, BOARD_OFFSET_Y + CELL_SIZE * (12 - i)) for i in range(6)],
    # Izquierda a derecha (arriba)
    *[(BOARD_OFFSET_X + CELL_SIZE * (6 - i), BOARD_OFFSET_Y + CELL_SIZE * 6) for i in range(1, 6)],
    # Sube a la entrada verde
    (BOARD_OFFSET_X, BOARD_OFFSET_Y + CELL_SIZE * 6),
    *[(BOARD_OFFSET_X, BOARD_OFFSET_Y + CELL_SIZE * (6 - i)) for i in range(1, 6)],
    # Derecha (izquierda a derecha, arriba)
    *[(BOARD_OFFSET_X + CELL_SIZE * i, BOARD_OFFSET_Y) for i in range(1, 6)],
    # Baja a la entrada amarilla
    (BOARD_OFFSET_X + CELL_SIZE * 6, BOARD_OFFSET_Y),
    *[(BOARD_OFFSET_X + CELL_SIZE * 6, BOARD_OFFSET_Y + CELL_SIZE * i) for i in range(1, 6)],
    # Derecha a izquierda (abajo)
    *[(BOARD_OFFSET_X + CELL_SIZE * (6 + i), BOARD_OFFSET_Y + CELL_SIZE * 6) for i in range(1, 6)],
    # Derecha (sube a la entrada azul)
    (BOARD_OFFSET_X + CELL_SIZE * 12, BOARD_OFFSET_Y + CELL_SIZE * 6),
    *[(BOARD_OFFSET_X + CELL_SIZE * 12, BOARD_OFFSET_Y + CELL_SIZE * (6 + i)) for i in range(1, 6)],
    # Izquierda a derecha (abajo)
    *[(BOARD_OFFSET_X + CELL_SIZE * (12 - i), BOARD_OFFSET_Y + CELL_SIZE * 12) for i in range(1, 6)],
    # Sube a la entrada roja
    (BOARD_OFFSET_X + CELL_SIZE * 6, BOARD_OFFSET_Y + CELL_SIZE * 12),
    *[(BOARD_OFFSET_X + CELL_SIZE * 6, BOARD_OFFSET_Y + CELL_SIZE * (12 - i)) for i in range(1, 6)],
]

# Caminos de entrada a meta para cada color (6 casillas)
HOME_PATHS = {
    'red':   [(BOARD_OFFSET_X + CELL_SIZE * (6 - i), BOARD_OFFSET_Y + CELL_SIZE * 7) for i in range(6)],
    'blue':  [(BOARD_OFFSET_X + CELL_SIZE * 7, BOARD_OFFSET_Y + CELL_SIZE * (6 + i)) for i in range(6)],
    'yellow':[(BOARD_OFFSET_X + CELL_SIZE * (6 + i), BOARD_OFFSET_Y + CELL_SIZE * 7) for i in range(6)],
    'green': [(BOARD_OFFSET_X + CELL_SIZE * 7, BOARD_OFFSET_Y + CELL_SIZE * (6 - i)) for i in range(6)]
}

# Posiciones de inicio (casas)
HOME_POSITIONS = {
    'red':   [(BOARD_OFFSET_X + CELL_SIZE * 1.5, BOARD_OFFSET_Y + CELL_SIZE * 1.5), (BOARD_OFFSET_X + CELL_SIZE * 3.5, BOARD_OFFSET_Y + CELL_SIZE * 1.5), (BOARD_OFFSET_X + CELL_SIZE * 1.5, BOARD_OFFSET_Y + CELL_SIZE * 3.5), (BOARD_OFFSET_X + CELL_SIZE * 3.5, BOARD_OFFSET_Y + CELL_SIZE * 3.5)],
    'blue':  [(BOARD_OFFSET_X + CELL_SIZE * 1.5, BOARD_OFFSET_Y + CELL_SIZE * 10.5), (BOARD_OFFSET_X + CELL_SIZE * 3.5, BOARD_OFFSET_Y + CELL_SIZE * 10.5), (BOARD_OFFSET_X + CELL_SIZE * 1.5, BOARD_OFFSET_Y + CELL_SIZE * 12.5), (BOARD_OFFSET_X + CELL_SIZE * 3.5, BOARD_OFFSET_Y + CELL_SIZE * 12.5)],
    'yellow':[(BOARD_OFFSET_X + CELL_SIZE * 10.5, BOARD_OFFSET_Y + CELL_SIZE * 10.5), (BOARD_OFFSET_X + CELL_SIZE * 12.5, BOARD_OFFSET_Y + CELL_SIZE * 10.5), (BOARD_OFFSET_X + CELL_SIZE * 10.5, BOARD_OFFSET_Y + CELL_SIZE * 12.5), (BOARD_OFFSET_X + CELL_SIZE * 12.5, BOARD_OFFSET_Y + CELL_SIZE * 12.5)],
    'green': [(BOARD_OFFSET_X + CELL_SIZE * 10.5, BOARD_OFFSET_Y + CELL_SIZE * 1.5), (BOARD_OFFSET_X + CELL_SIZE * 12.5, BOARD_OFFSET_Y + CELL_SIZE * 1.5), (BOARD_OFFSET_X + CELL_SIZE * 10.5, BOARD_OFFSET_Y + CELL_SIZE * 3.5), (BOARD_OFFSET_X + CELL_SIZE * 12.5, BOARD_OFFSET_Y + CELL_SIZE * 3.5)]
}

# Posiciones de meta (centro)
CENTER_POSITIONS = {
    'red':   (BOARD_OFFSET_X + CELL_SIZE * 7, BOARD_OFFSET_Y + CELL_SIZE * 6),
    'blue':  (BOARD_OFFSET_X + CELL_SIZE * 6, BOARD_OFFSET_Y + CELL_SIZE * 7),
    'yellow':(BOARD_OFFSET_X + CELL_SIZE * 7, BOARD_OFFSET_Y + CELL_SIZE * 8),
    'green': (BOARD_OFFSET_X + CELL_SIZE * 8, BOARD_OFFSET_Y + CELL_SIZE * 7)
}

# Zonas seguras (casillas con estrella)
SAFE_POSITIONS = [0, 8, 13, 21, 26, 34, 39, 47]

def generate_board_path():
    """Genera el camino completo del tablero de Ludo"""
    path = []
    x = BOARD_OFFSET_X
    y = BOARD_OFFSET_Y
    
    # El tablero tiene 15x15 casillas, con las casas en las esquinas
    # El camino principal tiene 52 casillas
    # Centrar las fichas en las casillas
    offset = CELL_SIZE // 2
    
    # Empezando desde la casilla de salida roja (abajo de la casa roja)
    # Columna izquierda subiendo (6 casillas)
    for i in range(6):
        path.append((x + CELL_SIZE * 6 + offset, y + CELL_SIZE * (13 - i) + offset))
    
    # Columna izquierda del brazo superior (2 casillas)
    for i in range(2):
        path.append((x + CELL_SIZE * (5 - i) + offset, y + CELL_SIZE * 6 + offset))
    
    # Fila superior hacia la derecha (5 casillas)
    for i in range(5):
        path.append((x + CELL_SIZE * i + offset, y + CELL_SIZE * 7 + offset))
    
    # Giro a la columna derecha (2 casillas)
    for i in range(2):
        path.append((x + CELL_SIZE * 6 + offset, y + CELL_SIZE * (5 - i) + offset))
    
    # Columna central superior bajando a zona verde (5 casillas)
    for i in range(5):
        path.append((x + CELL_SIZE * 7 + offset, y + CELL_SIZE * i + offset))
    
    # Columna derecha del brazo derecho (2 casillas)
    for i in range(2):
        path.append((x + CELL_SIZE * 8 + offset, y + CELL_SIZE * (5 + i) + offset))
    
    # Fila central derecha (5 casillas)
    for i in range(5):
        path.append((x + CELL_SIZE * (9 + i) + offset, y + CELL_SIZE * 6 + offset))
    
    # Giro a la columna derecha bajando (2 casillas)
    for i in range(2):
        path.append((x + CELL_SIZE * 14 + offset, y + CELL_SIZE * (7 + i) + offset))
    
    # Columna derecha bajando (5 casillas)
    for i in range(5):
        path.append((x + CELL_SIZE * 14 + offset, y + CELL_SIZE * (9 + i) + offset))
    
    # Columna derecha del brazo inferior (2 casillas)
    for i in range(2):
        path.append((x + CELL_SIZE * (13 - i) + offset, y + CELL_SIZE * 8 + offset))
    
    # Fila inferior hacia la izquierda (5 casillas)
    for i in range(5):
        path.append((x + CELL_SIZE * (11 - i) + offset, y + CELL_SIZE * 7 + offset))
    
    # Giro a la columna izquierda (2 casillas)
    for i in range(2):
        path.append((x + CELL_SIZE * 8 + offset, y + CELL_SIZE * (9 + i) + offset))
    
    # Columna central inferior subiendo a zona azul (5 casillas)
    for i in range(5):
        path.append((x + CELL_SIZE * 7 + offset, y + CELL_SIZE * (14 - i) + offset))
    
    # Últimas casillas antes de completar el circuito (2 casillas)
    for i in range(2):
        path.append((x + CELL_SIZE * 6 + offset, y + CELL_SIZE * (9 - i) + offset))
    
    return path

# Posiciones de inicio en el camino principal
START_POSITIONS = {
    "red": 0,    # Empieza en la primera casilla del camino (columna izquierda abajo)
    "green": 13, # Empieza después de 13 casillas (columna superior derecha)
    "yellow": 26, # Empieza después de 26 casillas (columna derecha abajo)
    "blue": 39   # Empieza después de 39 casillas (columna inferior izquierda)
}

class Piece:
    """Ficha de Ludo con lógica de movimiento idéntica a ludo_pupu.py"""
    def __init__(self, color: str, index: int):
        self.color = color
        self.index = index
        self.position = -1  # -1: en casa, 0-51: recorrido, 100-106: home
        self.has_finished = False
        self.image = None
        piece_size = int(CELL_SIZE * 0.6)
        try:
            image_path = f"Icons/Ficha {self._get_spanish_color()}.png"
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (piece_size, piece_size))
        except:
            self.image = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA)
            radius = piece_size // 2
            pygame.draw.circle(self.image, self._get_pygame_color(), (radius, radius), radius - 2)
            pygame.draw.circle(self.image, BLACK, (radius, radius), radius - 2, 2)
        self.rect = self.image.get_rect()
        self.update_position()

    def _get_spanish_color(self):
        colors = {'red': 'Roja', 'green': 'Verde', 'blue': 'Azul', 'yellow': 'Amarilla'}
        return colors.get(self.color, 'Roja')

    def _get_pygame_color(self):
        colors = {'red': RED, 'green': GREEN, 'blue': BLUE, 'yellow': YELLOW}
        return colors.get(self.color, RED)

    def update_position(self):
        # Posiciones de inicio (casas)
        if self.position == -1:
            pos = HOME_POSITIONS[self.color][self.index]
            self.rect.center = pos
        elif self.position >= 100:
            # Camino a meta
            home_idx = self.position - 100
            if 0 <= home_idx < 6:
                self.rect.center = HOME_PATHS[self.color][home_idx]
            else:
                self.rect.center = CENTER_POSITIONS[self.color]
        else:
            # Recorrido principal
            path_idx = (START_POSITIONS[self.color] + self.position) % 52
            self.rect.center = MAIN_PATH[path_idx]

    def can_move(self, steps: int, all_pieces=None) -> bool:
        if self.has_finished:
            return False
        if self.position == -1:
            return steps == 6
        # Llegada exacta a meta
        if self.position >= 100:
            return self.position + steps <= 106
        # Bloqueo: no puedes mover si tu destino tiene 2+ fichas propias
        if all_pieces is not None:
            dest = self.position + steps
            if dest < 52:
                count = sum(1 for p in all_pieces if p.color == self.color and p.position == dest and not p.has_finished)
                if count >= 2:
                    return False
            elif dest >= 100:
                home_idx = dest - 100
                count = sum(1 for p in all_pieces if p.color == self.color and p.position == dest and not p.has_finished)
                if count >= 2:
                    return False
        return True

    def move(self, steps: int, all_pieces=None, animate_cb=None, screen=None, clock=None):
        # Movimiento animado paso a paso
        if self.position == -1 and steps == 6:
            self.position = 0
            self.update_position()
            if animate_cb: animate_cb()
            return
        elif self.position >= 0 and self.position < 52:
            for _ in range(steps):
                if self.position == self._entry_to_home():
                    self.position = 100
                    self.update_position()
                    if animate_cb: animate_cb()
                    if screen and clock:
                        self._draw_and_wait(screen, clock)
                    break
                else:
                    self.position += 1
                    if self.position == 52:
                        self.position = 0
                    self.update_position()
                    if animate_cb: animate_cb()
                    if screen and clock:
                        self._draw_and_wait(screen, clock)
        elif self.position >= 100 and self.position < 106:
            for _ in range(steps):
                if self.position < 106:
                    self.position += 1
                    self.update_position()
                    if animate_cb: animate_cb()
                    if screen and clock:
                        self._draw_and_wait(screen, clock)
            if self.position == 106:
                self.has_finished = True
        self.update_position()

    def _draw_and_wait(self, screen, clock):
        # Dibuja la ficha y espera un poco para animación
        pygame.event.pump()
        screen.fill((240, 240, 240))
        # Redibuja tablero y fichas (llama a draw_game externo)
        # Esto se debe pasar como callback desde LudoGame
        pygame.display.flip()
        clock.tick(10)

    def _entry_to_home(self):
        # Casilla de entrada a home para cada color
        return { 'red': 51, 'green': 12, 'yellow': 25, 'blue': 38 }[self.color ]

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

class Dice:
    """Representa el dado del juego"""
    def __init__(self):
        self.value = 1
        self.rolling = False
        self.roll_timer = 0
        self.images = {}
        self.roll_sound = None
        
        # Cargar sonido si está disponible
        try:
            pygame.mixer.init()
            # Aquí podrías cargar un sonido de dado si lo tienes
            # self.roll_sound = pygame.mixer.Sound("sounds/dice_roll.wav")
        except:
            pass
        
        # Cargar imágenes del dado
        dice_names = {
            1: "dado-uno",
            2: "dados-dos", 
            3: "dados-tres",
            4: "dados-cuatro",
            5: "dado",  # Asumiendo que dado.png es el 5
            6: "dados-seis"
        }
        
        for num, name in dice_names.items():
            try:
                self.images[num] = pygame.image.load(f"Icons/{name}.png")
                self.images[num] = pygame.transform.scale(self.images[num], (100, 100))
            except:
                # Si no se puede cargar, crear una imagen simple
                self.images[num] = self._create_dice_image(num)
        
        self.rect = pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 50, 100, 100)
    
    def _create_dice_image(self, number: int) -> pygame.Surface:
        """Crea una imagen simple del dado si no se puede cargar"""
        surface = pygame.Surface((100, 100))
        surface.fill(WHITE)
        pygame.draw.rect(surface, BLACK, surface.get_rect(), 3)
        pygame.draw.rect(surface, LIGHT_GRAY, surface.get_rect().inflate(-6, -6))
        
        # Dibujar los puntos del dado
        dot_positions = {
            1: [(50, 50)],
            2: [(30, 30), (70, 70)],
            3: [(30, 30), (50, 50), (70, 70)],
            4: [(30, 30), (70, 30), (30, 70), (70, 70)],
            5: [(30, 30), (70, 30), (50, 50), (30, 70), (70, 70)],
            6: [(30, 25), (30, 50), (30, 75), (70, 25), (70, 50), (70, 75)]
        }
        
        for pos in dot_positions[number]:
            pygame.draw.circle(surface, BLACK, pos, 8)
        
        return surface
    
    def roll(self):
        """Inicia la animación de tirar el dado"""
        self.rolling = True
        self.roll_timer = 30  # 30 frames de animación
        
        if self.roll_sound:
            self.roll_sound.play()
    
    def update(self):
        """Actualiza la animación del dado"""
        if self.rolling:
            if self.roll_timer > 0:
                self.value = random.randint(1, 6)
                self.roll_timer -= 1
                
                # Efecto de rotación
                if self.roll_timer % 2 == 0:
                    self.rect.x += random.randint(-2, 2)
                    self.rect.y += random.randint(-2, 2)
            else:
                self.rolling = False
                # Centrar el dado
                self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
                return True  # Indica que terminó de rodar
        return False
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el dado"""
        if self.value in self.images:
            # Sombra
            shadow_rect = self.rect.copy()
            shadow_rect.x += 5
            shadow_rect.y += 5
            pygame.draw.rect(screen, DARK_GRAY, shadow_rect, border_radius=10)
            
            # Dado
            screen.blit(self.images[self.value], self.rect)

class Player:
    """Representa un jugador"""
    def __init__(self, name: str, color: str, is_ai: bool = False):
        self.name = name
        self.color = color
        self.pieces = [Piece(color, i) for i in range(4)]
        self.finished_pieces = 0
        self.can_roll = True
        self.has_moved = False
        self.is_ai = is_ai
        self.consecutive_sixes = 0
    
    def update_finished_pieces(self):
        """Actualiza el contador de fichas terminadas"""
        self.finished_pieces = sum(1 for piece in self.pieces if piece.has_finished)
    
    def get_movable_pieces(self, dice_value: int, all_pieces=None) -> List[Piece]:
        """Obtiene las fichas que pueden moverse, considerando bloqueos"""
        movable = []
        for piece in self.pieces:
            if piece.can_move(dice_value, all_pieces):
                movable.append(piece)
        return movable
    
    def check_winner(self) -> bool:
        """Verifica si el jugador ganó"""
        return all(piece.has_finished for piece in self.pieces)
    
    def get_pieces_at_position(self, position: int, on_home_path: bool = False) -> List[Piece]:
        """Obtiene las fichas en una posición específica"""
        pieces = []
        for piece in self.pieces:
            if not piece.is_home and not piece.has_finished:
                if on_home_path and piece.on_home_path and piece.home_path_position == position:
                    pieces.append(piece)
                elif not on_home_path and not piece.on_home_path and piece.path_position == position:
                    pieces.append(piece)
        return pieces
    
    def ai_select_piece(self, movable_pieces: List[Piece], all_players: List['Player']) -> Optional[Piece]:
        """IA para seleccionar qué ficha mover"""
        if not movable_pieces:
            return None
        
        # Prioridades de la IA:
        # 1. Sacar una ficha nueva si es posible
        # 2. Mover una ficha que pueda capturar a un oponente
        # 3. Mover la ficha más cercana a la meta
        # 4. Mover una ficha que esté en peligro
        
        # Prioridad 1: Sacar una ficha nueva
        for piece in movable_pieces:
            if piece.is_home:
                return piece
        
        # Evaluar cada pieza movible
        best_piece = None
        best_score = -1000
        
        for piece in movable_pieces:
            score = 0
            
            # Bonus por estar cerca de la meta
            if piece.on_home_path:
                score += 50 + piece.home_path_position * 10
            else:
                # Calcular distancia a la meta
                distance_to_home = 50 - piece.position
                if distance_to_home < 0:
                    distance_to_home += 52
                score += (52 - distance_to_home)
            
            # Bonus por capturar oponentes
            future_position = (piece.position + 6) % 52
            for player in all_players:
                if player.color != self.color:
                    for enemy_piece in player.pieces:
                        if (not enemy_piece.is_home and not enemy_piece.has_finished and 
                            not enemy_piece.on_home_path and enemy_piece.position == future_position and
                            not enemy_piece.is_safe):
                            score += 100  # Gran bonus por capturar
            
            # Penalización por estar en peligro
            if not piece.is_safe:
                for player in all_players:
                    if player.color != self.color:
                        for enemy_piece in player.pieces:
                            if not enemy_piece.is_home and not enemy_piece.has_finished:
                                distance = enemy_piece.position - piece.position
                                if 0 < distance <= 6:
                                    score -= 20  # Penalización por estar en peligro
            
            if score > best_score:
                best_score = score
                best_piece = piece
        
        return best_piece

class Board:
    """Representa el tablero del juego"""
    def __init__(self):
        self.image = self._create_detailed_board()
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    
    def _create_detailed_board(self) -> pygame.Surface:
        surface = pygame.Surface((CELL_SIZE * 15, CELL_SIZE * 15))
        surface.fill((0, 150, 0))  # Fondo verde clásico
        # --- Casas de colores (esquinas) ---
        pygame.draw.rect(surface, RED, (0, 0, CELL_SIZE * 6, CELL_SIZE * 6))
        pygame.draw.rect(surface, GREEN, (CELL_SIZE * 9, 0, CELL_SIZE * 6, CELL_SIZE * 6))
        pygame.draw.rect(surface, YELLOW, (CELL_SIZE * 9, CELL_SIZE * 9, CELL_SIZE * 6, CELL_SIZE * 6))
        pygame.draw.rect(surface, BLUE, (0, CELL_SIZE * 9, CELL_SIZE * 6, CELL_SIZE * 6))
        # --- Caminos principales (blancos) ---
        for i in range(6):
            pygame.draw.rect(surface, WHITE, (CELL_SIZE * 6, CELL_SIZE * i, CELL_SIZE, CELL_SIZE))  # Arriba
            pygame.draw.rect(surface, WHITE, (CELL_SIZE * (i + 9), CELL_SIZE * 6, CELL_SIZE, CELL_SIZE))  # Derecha
            pygame.draw.rect(surface, WHITE, (CELL_SIZE * 8, CELL_SIZE * (i + 9), CELL_SIZE, CELL_SIZE))  # Abajo
            pygame.draw.rect(surface, WHITE, (CELL_SIZE * i, CELL_SIZE * 8, CELL_SIZE, CELL_SIZE))  # Izquierda
        for i in range(1, 6):
            pygame.draw.rect(surface, WHITE, (CELL_SIZE * (6 - i), CELL_SIZE * 6, CELL_SIZE, CELL_SIZE))  # Arriba izq
            pygame.draw.rect(surface, WHITE, (CELL_SIZE * 8, CELL_SIZE * (6 - i), CELL_SIZE, CELL_SIZE))  # Derecha arriba
            pygame.draw.rect(surface, WHITE, (CELL_SIZE * (14 - i), CELL_SIZE * 8, CELL_SIZE, CELL_SIZE))  # Abajo der
            pygame.draw.rect(surface, WHITE, (CELL_SIZE * 6, CELL_SIZE * (14 - i), CELL_SIZE, CELL_SIZE))  # Izq abajo
        # --- Caminos de entrada a meta (color) ---
        for i in range(1, 6):
            pygame.draw.rect(surface, RED, (CELL_SIZE * (6 + i), CELL_SIZE * 7, CELL_SIZE, CELL_SIZE))  # Rojo
            pygame.draw.rect(surface, GREEN, (CELL_SIZE * 7, CELL_SIZE * (6 - i), CELL_SIZE, CELL_SIZE))  # Verde
            pygame.draw.rect(surface, YELLOW, (CELL_SIZE * (8 - i), CELL_SIZE * 7, CELL_SIZE, CELL_SIZE))  # Amarillo
            pygame.draw.rect(surface, BLUE, (CELL_SIZE * 7, CELL_SIZE * (8 + i), CELL_SIZE, CELL_SIZE))  # Azul
        # --- Centro (4 triángulos de colores) ---
        center = (CELL_SIZE * 7.5, CELL_SIZE * 7.5)
        pygame.draw.polygon(surface, RED, [center, (CELL_SIZE * 6, CELL_SIZE * 6), (CELL_SIZE * 9, CELL_SIZE * 6)])
        pygame.draw.polygon(surface, GREEN, [center, (CELL_SIZE * 9, CELL_SIZE * 6), (CELL_SIZE * 9, CELL_SIZE * 9)])
        pygame.draw.polygon(surface, YELLOW, [center, (CELL_SIZE * 9, CELL_SIZE * 9), (CELL_SIZE * 6, CELL_SIZE * 9)])
        pygame.draw.polygon(surface, BLUE, [center, (CELL_SIZE * 6, CELL_SIZE * 9), (CELL_SIZE * 6, CELL_SIZE * 6)])
        pygame.draw.circle(surface, WHITE, (int(center[0]), int(center[1])), int(CELL_SIZE * 1.2))
        # --- Zonas seguras (estrellas) ---
        safe_coords = [  # Coordenadas aproximadas de las estrellas
            (CELL_SIZE * 6, CELL_SIZE * 2), (CELL_SIZE * 8, CELL_SIZE * 6), (CELL_SIZE * 12, CELL_SIZE * 6),
            (CELL_SIZE * 8, CELL_SIZE * 8), (CELL_SIZE * 6, CELL_SIZE * 12), (CELL_SIZE * 2, CELL_SIZE * 8),
            (CELL_SIZE * 6, CELL_SIZE * 8), (CELL_SIZE * 8, CELL_SIZE * 2)
        ]
        for coord in safe_coords:
            pygame.draw.circle(surface, (255, 215, 0), (int(coord[0] + CELL_SIZE // 2), int(coord[1] + CELL_SIZE // 2)), 12)
            pygame.draw.circle(surface, BLACK, (int(coord[0] + CELL_SIZE // 2), int(coord[1] + CELL_SIZE // 2)), 12, 2)
        # --- Casas de inicio (círculos grandes en las esquinas) ---
        home_coords = [
            (CELL_SIZE * 1.5, CELL_SIZE * 1.5, RED),
            (CELL_SIZE * 13.5, CELL_SIZE * 1.5, GREEN),
            (CELL_SIZE * 13.5, CELL_SIZE * 13.5, YELLOW),
            (CELL_SIZE * 1.5, CELL_SIZE * 13.5, BLUE)
        ]
        for x, y, color in home_coords:
            pygame.draw.circle(surface, color, (int(x), int(y)), int(CELL_SIZE * 2.2))
            pygame.draw.circle(surface, WHITE, (int(x), int(y)), int(CELL_SIZE * 2.2), 4)
        # --- Líneas de cuadrícula ---
        for i in range(16):
            pygame.draw.line(surface, BLACK, (0, CELL_SIZE * i), (CELL_SIZE * 15, CELL_SIZE * i), 2)
            pygame.draw.line(surface, BLACK, (CELL_SIZE * i, 0), (CELL_SIZE * i, CELL_SIZE * 15), 2)
        return surface
    
    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, (BOARD_OFFSET_X, BOARD_OFFSET_Y))

class LudoGame:
    """Clase principal del juego"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Ludo - Juego Interactivo")
        pygame.display.set_icon(pygame.Surface((32, 32)))  # Icono vacío por ahora
        self.clock = pygame.time.Clock()
        
        # Componentes del juego
        self.board = Board()
        self.dice = Dice()
        self.players = []
        self.current_player_index = 0
        self.state = GameState.MENU
        
        # Fuentes
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 36)
        self.info_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Botones del menú
        self.menu_buttons = {
            "2_players": pygame.Rect(350, 300, 200, 60),
            "3_players": pygame.Rect(350, 380, 200, 60),
            "4_players": pygame.Rect(350, 460, 200, 60),
            "vs_ai": pygame.Rect(350, 540, 200, 60)
        }
        
        # Botón para tirar el dado
        self.roll_button = pygame.Rect(WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT - 100, 160, 50)
        
        # Botón de pausa
        self.pause_button = pygame.Rect(WINDOW_WIDTH - 110, 10, 100, 40)
        
        self.winner = None
        self.selected_piece = None
        self.game_history = []
        self.turn_count = 0
        
        # Variables para animaciones
        self.animations = []
        self.messages = []
    
    def add_message(self, text: str, duration: int = 2000):
        """Agrega un mensaje temporal a la pantalla"""
        self.messages.append({
            'text': text,
            'time': pygame.time.get_ticks(),
            'duration': duration
        })
    
    def start_game(self, num_players: int, vs_ai: bool = False):
        """Inicia una nueva partida"""
        colors = ["red", "green", "yellow", "blue"]
        names = ["Jugador 1", "Jugador 2", "Jugador 3", "Jugador 4"]
        
        self.players = []
        
        if vs_ai:
            # Jugador humano siempre es rojo
            self.players.append(Player("Jugador", colors[0], is_ai=False))
            # Los demás son IA
            for i in range(1, num_players):
                self.players.append(Player(f"IA {i}", colors[i], is_ai=True))
        else:
            for i in range(num_players):
                self.players.append(Player(names[i], colors[i], is_ai=False))
        
        self.current_player_index = 0
        self.state = GameState.PLAYING
        self.turn_count = 0
        self.game_history = []
        self.add_message(f"¡Comienza {self.players[0].name}!", 2000)
    
    def handle_menu_click(self, pos: Tuple[int, int]):
        """Maneja los clicks en el menú"""
        for button_name, rect in self.menu_buttons.items():
            if rect.collidepoint(pos):
                if button_name == "2_players":
                    self.start_game(2)
                elif button_name == "3_players":
                    self.start_game(3)
                elif button_name == "4_players":
                    self.start_game(4)
                elif button_name == "vs_ai":
                    self.start_game(4, vs_ai=True)
    
    def check_captures(self, piece: Piece):
        """Verifica si una ficha captura a otra y permite volver a tirar si captura"""
        if piece.position in SAFE_POSITIONS:
            return False
        captured = False
        for player in self.players:
            if player.color != piece.color:
                for enemy_piece in player.pieces:
                    if (enemy_piece.position == piece.position and not enemy_piece.has_finished and enemy_piece.position >= 0 and enemy_piece.position < 106):
                        # Bloqueo: no capturas si hay 2+ fichas enemigas
                        count = sum(1 for p in player.pieces if p.position == piece.position and not p.has_finished)
                        if count == 1:
                            enemy_piece.position = -1
                            enemy_piece.has_finished = False
                            enemy_piece.update_position()
                            self.add_message(f"¡{piece.color} captura a {enemy_piece.color}!", 2000)
                            captured = True
        return captured
    
    def handle_game_click(self, pos: Tuple[int, int]):
        """Maneja los clicks durante el juego"""
        current_player = self.players[self.current_player_index]
        
        # Click en el botón de pausa
        if self.pause_button.collidepoint(pos):
            self.state = GameState.PAUSED
            return
        
        # Click en el botón de tirar dado
        if self.roll_button.collidepoint(pos) and current_player.can_roll and not self.dice.rolling:
            self.dice.roll()
            self.state = GameState.ROLLING_DICE
            current_player.can_roll = False
            return
        
        # Click en una ficha
        if not current_player.can_roll and not current_player.has_moved and not current_player.is_ai:
            all_pieces = [p for pl in self.players for p in pl.pieces]
            movable_pieces = current_player.get_movable_pieces(self.dice.value, all_pieces)
            for piece in movable_pieces:
                if piece.rect.collidepoint(pos):
                    old_position = piece.position
                    # Movimiento animado paso a paso
                    piece.move(self.dice.value, all_pieces, animate_cb=self.draw, screen=self.screen, clock=self.clock)
                    current_player.has_moved = True
                    captured = self.check_captures(piece)
                    current_player.update_finished_pieces()
                    if current_player.check_winner():
                        self.winner = current_player
                        self.state = GameState.GAME_OVER
                        self.add_message(f"¡{current_player.name} ha ganado!", 5000)
                    else:
                        if captured or self.dice.value == 6:
                            current_player.consecutive_sixes += 1
                            if current_player.consecutive_sixes >= 3:
                                self.add_message("¡Tres 6 seguidos! Pierdes el turno", 2000)
                                self.next_turn()
                            else:
                                current_player.can_roll = True
                                current_player.has_moved = False
                                self.add_message("¡Tira de nuevo!", 1500)
                        else:
                            current_player.consecutive_sixes = 0
                            self.next_turn()
                    break
    
    def next_turn(self):
        """Pasa al siguiente turno"""
        self.turn_count += 1
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        current_player = self.players[self.current_player_index]
        current_player.can_roll = True
        current_player.has_moved = False
        current_player.consecutive_sixes = 0
        self.add_message(f"Turno de {current_player.name}", 1500)
        
        # Si es IA, programar su turno
        if current_player.is_ai:
            pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # Esperar 1 segundo antes de que juegue la IA
    
    def ai_turn(self):
        """Ejecuta el turno de la IA"""
        current_player = self.players[self.current_player_index]
        
        if not current_player.is_ai:
            return
        
        if current_player.can_roll and not self.dice.rolling:
            # Tirar el dado
            self.dice.roll()
            self.state = GameState.ROLLING_DICE
            current_player.can_roll = False
        elif not current_player.can_roll and not current_player.has_moved:
            # Seleccionar y mover ficha
            movable_pieces = current_player.get_movable_pieces(self.dice.value)
            selected_piece = current_player.ai_select_piece(movable_pieces, self.players)
            
            if selected_piece:
                selected_piece.move(self.dice.value)
                current_player.has_moved = True
                
                # Verificar capturas
                self.check_captures(selected_piece)
                
                # Actualizar fichas terminadas
                current_player.update_finished_pieces()
                
                # Verificar si ganó
                if current_player.check_winner():
                    self.winner = current_player
                    self.state = GameState.GAME_OVER
                    self.add_message(f"¡{current_player.name} ha ganado!", 5000)
                else:
                    # Siguiente turno
                    if self.dice.value == 6:
                        current_player.consecutive_sixes += 1
                        if current_player.consecutive_sixes >= 3:
                            self.add_message("¡Tres 6 seguidos! Pierde el turno", 2000)
                            self.next_turn()
                        else:
                            current_player.can_roll = True
                            current_player.has_moved = False
                            pygame.time.set_timer(pygame.USEREVENT + 1, 1500)  # Programar siguiente tirada
                    else:
                        current_player.consecutive_sixes = 0
                        self.next_turn()
            else:
                # No puede mover ninguna ficha
                if self.dice.value != 6:
                    self.next_turn()
                else:
                    current_player.can_roll = True
                    pygame.time.set_timer(pygame.USEREVENT + 1, 1500)
    
    def handle_events(self):
        """Maneja los eventos del juego"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == GameState.MENU:
                    self.handle_menu_click(event.pos)
                elif self.state == GameState.PLAYING:
                    self.handle_game_click(event.pos)
                elif self.state == GameState.GAME_OVER:
                    # Volver al menú
                    self.state = GameState.MENU
                elif self.state == GameState.PAUSED:
                    # Click para resumir
                    self.state = GameState.PLAYING
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                    else:
                        self.state = GameState.MENU
                elif event.key == pygame.K_SPACE and self.state == GameState.PLAYING:
                    # Atajo para tirar el dado
                    current_player = self.players[self.current_player_index]
                    if current_player.can_roll and not self.dice.rolling and not current_player.is_ai:
                        self.dice.roll()
                        self.state = GameState.ROLLING_DICE
                        current_player.can_roll = False
            
            elif event.type == pygame.USEREVENT + 1:
                # Evento para la IA
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Detener el timer
                if self.state == GameState.PLAYING:
                    self.ai_turn()
        
        return True
    
    def update(self):
        """Actualiza la lógica del juego"""
        if self.state == GameState.ROLLING_DICE:
            if self.dice.update():
                self.state = GameState.PLAYING
                
                # Si no hay fichas que mover, manejar el turno
                current_player = self.players[self.current_player_index]
                movable_pieces = current_player.get_movable_pieces(self.dice.value)
                
                if not movable_pieces:
                    self.add_message("No puedes mover ninguna ficha", 1500)
                    if self.dice.value != 6:
                        self.next_turn()
                    else:
                        current_player.can_roll = True
                        if current_player.is_ai:
                            pygame.time.set_timer(pygame.USEREVENT + 1, 1500)
                elif current_player.is_ai:
                    # Si es IA, programar su movimiento
                    pygame.time.set_timer(pygame.USEREVENT + 1, 1000)
        
        # Actualizar mensajes
        current_time = pygame.time.get_ticks()
        self.messages = [msg for msg in self.messages 
                        if current_time - msg['time'] < msg['duration']]
    
    def draw_menu(self):
        """Dibuja el menú principal"""
        self.screen.fill(WHITE)
        
        # Fondo con gradiente
        for i in range(WINDOW_HEIGHT):
            color = (
                255 - i * 50 // WINDOW_HEIGHT,
                255 - i * 30 // WINDOW_HEIGHT,
                255
            )
            pygame.draw.line(self.screen, color, (0, i), (WINDOW_WIDTH, i))
        
        # Título con sombra
        shadow = self.title_font.render("LUDO", True, GRAY)
        shadow_rect = shadow.get_rect(center=(WINDOW_WIDTH // 2 + 5, 100 + 5))
        self.screen.blit(shadow, shadow_rect)
        
        title = self.title_font.render("LUDO", True, BLACK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Subtítulo
        subtitle = self.menu_font.render("Juego Interactivo", True, DARK_GRAY)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 170))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Botones con efecto hover
        mouse_pos = pygame.mouse.get_pos()
        
        for button_name, rect in self.menu_buttons.items():
            # Determinar si el mouse está sobre el botón
            is_hover = rect.collidepoint(mouse_pos)
            
            # Sombra del botón
            shadow_rect = rect.copy()
            shadow_rect.x += 5
            shadow_rect.y += 5
            pygame.draw.rect(self.screen, DARK_GRAY, shadow_rect, border_radius=10)
            
            # Color del botón
            button_color = LIGHT_GRAY if is_hover else WHITE
            pygame.draw.rect(self.screen, button_color, rect, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, rect, 3, border_radius=10)
            
            # Texto del botón
            if button_name == "2_players":
                text = "2 Jugadores"
            elif button_name == "3_players":
                text = "3 Jugadores"
            elif button_name == "4_players":
                text = "4 Jugadores"
            else:
                text = "Contra IA"
            
            text_surface = self.menu_font.render(text, True, BLACK)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
        
        # Instrucciones
        instructions = [
            "Reglas del juego:",
            "• Saca un 6 para sacar una ficha",
            "• Si sacas un 6, tiras de nuevo",
            "• Captura las fichas enemigas",
            "• Las estrellas son zonas seguras",
            "• Gana llevando todas tus fichas al centro"
        ]
        
        y_pos = WINDOW_HEIGHT - 200
        for instruction in instructions:
            text = self.small_font.render(instruction, True, DARK_GRAY)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_pos))
            self.screen.blit(text, text_rect)
            y_pos += 25
    
    def draw_game(self):
        """Dibuja el juego"""
        # Fondo
        self.screen.fill((240, 240, 240))
        
        # Dibujar tablero
        self.board.draw(self.screen)
        
        # Dibujar fichas
        for player in self.players:
            for piece in player.pieces:
                piece.draw(self.screen)
        
        # Dibujar dado si no está rodando o si está en el centro
        if not self.dice.rolling or self.state == GameState.ROLLING_DICE:
            self.dice.draw(self.screen)
        
        # Panel de información
        info_panel = pygame.Surface((200, 300))
        info_panel.fill(WHITE)
        info_panel.set_alpha(230)
        self.screen.blit(info_panel, (10, 10))
        
        # Información de los jugadores
        y_pos = 20
        for i, player in enumerate(self.players):
            # Indicador de turno actual
            if i == self.current_player_index:
                pygame.draw.circle(self.screen, player._get_pygame_color() if hasattr(player, '_get_pygame_color') else BLACK, 
                                 (25, y_pos + 10), 8)
            
            # Nombre del jugador
            text = self.info_font.render(f"{player.name}", True, BLACK)
            self.screen.blit(text, (40, y_pos))
            
            # Fichas terminadas
            finished_text = self.small_font.render(f"Fichas en meta: {player.finished_pieces}/4", True, GRAY)
            self.screen.blit(finished_text, (40, y_pos + 20))
            
            y_pos += 60
        
        # Información del turno
        turn_info = pygame.Surface((300, 80))
        turn_info.fill(WHITE)
        turn_info.set_alpha(230)
        self.screen.blit(turn_info, (WINDOW_WIDTH - 310, 10))
        
        current_player = self.players[self.current_player_index]
        turn_text = self.menu_font.render(f"Turno: {current_player.name}", True, current_player._get_pygame_color() if hasattr(current_player, '_get_pygame_color') else BLACK)
        self.screen.blit(turn_text, (WINDOW_WIDTH - 300, 20))
        
        # Número de turno
        turn_count_text = self.small_font.render(f"Turno #{self.turn_count + 1}", True, GRAY)
        self.screen.blit(turn_count_text, (WINDOW_WIDTH - 300, 55))
        
        # Dibujar botón de tirar dado
        if current_player.can_roll and not self.dice.rolling and not current_player.is_ai:
            mouse_pos = pygame.mouse.get_pos()
            is_hover = self.roll_button.collidepoint(mouse_pos)
            
            # Sombra
            shadow_rect = self.roll_button.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(self.screen, DARK_GRAY, shadow_rect, border_radius=25)
            
            # Botón
            button_color = (0, 200, 0) if is_hover else GREEN
            pygame.draw.rect(self.screen, button_color, self.roll_button, border_radius=25)
            pygame.draw.rect(self.screen, BLACK, self.roll_button, 3, border_radius=25)
            
            text = self.menu_font.render("Tirar Dado", True, WHITE)
            text_rect = text.get_rect(center=self.roll_button.center)
            self.screen.blit(text, text_rect)
            
            # Texto de atajo
            shortcut_text = self.small_font.render("(Espacio)", True, GRAY)
            shortcut_rect = shortcut_text.get_rect(center=(self.roll_button.centerx, self.roll_button.bottom + 15))
            self.screen.blit(shortcut_text, shortcut_rect)
        
        # Botón de pausa
        pygame.draw.rect(self.screen, WHITE, self.pause_button, border_radius=5)
        pygame.draw.rect(self.screen, BLACK, self.pause_button, 2, border_radius=5)
        pause_text = self.info_font.render("Pausa", True, BLACK)
        pause_rect = pause_text.get_rect(center=self.pause_button.center)
        self.screen.blit(pause_text, pause_rect)
        
        # Mostrar valor del dado
        if not self.dice.rolling:
            dice_text = self.menu_font.render(f"Dado: {self.dice.value}", True, BLACK)
            dice_rect = dice_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80))
            self.screen.blit(dice_text, dice_rect)
        
        # Resaltar fichas movibles
        if not current_player.can_roll and not current_player.has_moved and not current_player.is_ai:
            movable_pieces = current_player.get_movable_pieces(self.dice.value)
            for piece in movable_pieces:
                # Dibujar un círculo pulsante alrededor de las fichas movibles
                radius = 25 + math.sin(pygame.time.get_ticks() * 0.005) * 5
                pygame.draw.circle(self.screen, current_player._get_pygame_color() if hasattr(current_player, '_get_pygame_color') else BLACK, 
                                 piece.rect.center, int(radius), 3)
        
        # Mostrar mensajes
        y_pos = WINDOW_HEIGHT // 2 - 150
        for msg in self.messages:
            alpha = 255
            elapsed = pygame.time.get_ticks() - msg['time']
            if elapsed > msg['duration'] - 500:
                # Desvanecer en los últimos 500ms
                alpha = 255 * (msg['duration'] - elapsed) // 500
            
            text_surface = self.menu_font.render(msg['text'], True, BLACK)
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, y_pos))
            
            # Fondo del mensaje
            bg_surface = pygame.Surface((text_rect.width + 40, text_rect.height + 20))
            bg_surface.fill(WHITE)
            bg_surface.set_alpha(alpha * 0.8)
            bg_rect = bg_surface.get_rect(center=(WINDOW_WIDTH // 2, y_pos))
            self.screen.blit(bg_surface, bg_rect)
            
            self.screen.blit(text_surface, text_rect)
            y_pos += 60
        
        # Si es turno de la IA, mostrar indicador
        if current_player.is_ai:
            ai_text = self.info_font.render("IA pensando...", True, GRAY)
            ai_rect = ai_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 80))
            self.screen.blit(ai_text, ai_rect)
    
    def draw_game_over(self):
        """Dibuja la pantalla de fin de juego"""
        # Fondo semitransparente sobre el juego
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Panel de victoria
        panel_width = 600
        panel_height = 400
        panel = pygame.Surface((panel_width, panel_height))
        panel.fill(WHITE)
        panel_rect = panel.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        
        # Borde del panel
        pygame.draw.rect(panel, self.winner._get_pygame_color() if hasattr(self.winner, '_get_pygame_color') else BLACK, 
                        panel.get_rect(), 10)
        
        self.screen.blit(panel, panel_rect)
        
        # Mensaje de victoria
        win_text = self.title_font.render("¡Victoria!", True, self.winner._get_pygame_color() if hasattr(self.winner, '_get_pygame_color') else BLACK)
        win_rect = win_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        self.screen.blit(win_text, win_rect)
        
        # Nombre del ganador
        winner_text = self.menu_font.render(f"{self.winner.name} ha ganado", True, BLACK)
        winner_rect = winner_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(winner_text, winner_rect)
        
        # Estadísticas
        stats_text = self.info_font.render(f"Turnos jugados: {self.turn_count}", True, GRAY)
        stats_rect = stats_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(stats_text, stats_rect)
        
        # Instrucción para continuar
        cont_text = self.menu_font.render("Haz clic para volver al menú", True, GRAY)
        cont_rect = cont_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 120))
        self.screen.blit(cont_text, cont_rect)
    
    def draw_paused(self):
        """Dibuja la pantalla de pausa"""
        # Fondo semitransparente
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Mensaje de pausa
        pause_text = self.title_font.render("PAUSA", True, WHITE)
        pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        # Instrucciones
        resume_text = self.menu_font.render("Presiona ESC o haz clic para continuar", True, WHITE)
        resume_rect = resume_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(resume_text, resume_rect)
    
    def draw(self):
        """Dibuja la pantalla según el estado del juego"""
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state in [GameState.PLAYING, GameState.ROLLING_DICE, GameState.MOVING_PIECE]:
            self.draw_game()
        elif self.state == GameState.GAME_OVER:
            self.draw_game()
            self.draw_game_over()
        elif self.state == GameState.PAUSED:
            self.draw_game()
            self.draw_paused()
        
        pygame.display.flip()
    
    def run(self):
        """Bucle principal del juego"""
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = LudoGame()
    game.run() 