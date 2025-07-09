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
BOARD_OFFSET_X = (WINDOW_WIDTH - BOARD_SIZE) // 2
BOARD_OFFSET_Y = (WINDOW_HEIGHT - BOARD_SIZE) // 2

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
CELL_SIZE = BOARD_SIZE // 15

# Posiciones de las casas de inicio (ajustadas al tablero real)
HOME_POSITIONS = {
    "red": [
        (BOARD_OFFSET_X + CELL_SIZE * 2.5, BOARD_OFFSET_Y + CELL_SIZE * 2.5),
        (BOARD_OFFSET_X + CELL_SIZE * 3.5, BOARD_OFFSET_Y + CELL_SIZE * 2.5),
        (BOARD_OFFSET_X + CELL_SIZE * 2.5, BOARD_OFFSET_Y + CELL_SIZE * 3.5),
        (BOARD_OFFSET_X + CELL_SIZE * 3.5, BOARD_OFFSET_Y + CELL_SIZE * 3.5)
    ],
    "green": [
        (BOARD_OFFSET_X + CELL_SIZE * 11.5, BOARD_OFFSET_Y + CELL_SIZE * 2.5),
        (BOARD_OFFSET_X + CELL_SIZE * 12.5, BOARD_OFFSET_Y + CELL_SIZE * 2.5),
        (BOARD_OFFSET_X + CELL_SIZE * 11.5, BOARD_OFFSET_Y + CELL_SIZE * 3.5),
        (BOARD_OFFSET_X + CELL_SIZE * 12.5, BOARD_OFFSET_Y + CELL_SIZE * 3.5)
    ],
    "yellow": [
        (BOARD_OFFSET_X + CELL_SIZE * 11.5, BOARD_OFFSET_Y + CELL_SIZE * 11.5),
        (BOARD_OFFSET_X + CELL_SIZE * 12.5, BOARD_OFFSET_Y + CELL_SIZE * 11.5),
        (BOARD_OFFSET_X + CELL_SIZE * 11.5, BOARD_OFFSET_Y + CELL_SIZE * 12.5),
        (BOARD_OFFSET_X + CELL_SIZE * 12.5, BOARD_OFFSET_Y + CELL_SIZE * 12.5)
    ],
    "blue": [
        (BOARD_OFFSET_X + CELL_SIZE * 2.5, BOARD_OFFSET_Y + CELL_SIZE * 11.5),
        (BOARD_OFFSET_X + CELL_SIZE * 3.5, BOARD_OFFSET_Y + CELL_SIZE * 11.5),
        (BOARD_OFFSET_X + CELL_SIZE * 2.5, BOARD_OFFSET_Y + CELL_SIZE * 12.5),
        (BOARD_OFFSET_X + CELL_SIZE * 3.5, BOARD_OFFSET_Y + CELL_SIZE * 12.5)
    ]
}

# Zonas seguras (casillas con estrella) - actualizadas según el tablero
SAFE_POSITIONS = [1, 9, 14, 22, 27, 35, 40, 48, 53, 61, 66, 68]  # Posiciones donde están las estrellas

# Posiciones de inicio en el camino principal (casillas de salida)
START_POSITIONS = {
    "yellow": 5,   # Sale por la casilla 5
    "blue": 22,    # Sale por la casilla 22
    "red": 39,     # Sale por la casilla 39
    "green": 56    # Sale por la casilla 56
}

# Posiciones de entrada a las columnas de color (un paso antes de entrar)
HOME_ENTRANCE_POSITIONS = {
    "yellow": 68,   # Entra a la columna amarilla después de la casilla 68
    "blue": 17,     # Entra a la columna azul después de la casilla 17
    "red": 34,      # Entra a la columna roja después de la casilla 34
    "green": 51     # Entra a la columna verde después de la casilla 51
}

def generate_board_path():
    """Genera el camino completo del tablero de Ludo - 68 casillas"""
    path = []
    x = BOARD_OFFSET_X
    y = BOARD_OFFSET_Y
    offset = CELL_SIZE // 2
    
    # El tablero tiene 68 casillas numeradas del 1 al 68
    # Basándome en la imagen del tablero numerado
    
    # Casillas 1-6: Columna 6 hacia abajo
    for i in range(6):
        path.append((x + CELL_SIZE * 6 + offset, y + CELL_SIZE * (8 + i) + offset))
    
    # Casillas 7-8: Giro en la esquina inferior izquierda
    path.append((x + CELL_SIZE * 5 + offset, y + CELL_SIZE * 14 + offset))
    path.append((x + CELL_SIZE * 4 + offset, y + CELL_SIZE * 14 + offset))
    
    # Casillas 9-14: Fila inferior hacia la izquierda
    for i in range(6):
        path.append((x + CELL_SIZE * (3 - i) + offset, y + CELL_SIZE * 13 + offset))
    
    # Casillas 15-16: Giro hacia arriba
    path.append((x + CELL_SIZE * 0 + offset, y + CELL_SIZE * 12 + offset))
    path.append((x + CELL_SIZE * 0 + offset, y + CELL_SIZE * 11 + offset))
    
    # Casillas 17-22: Columna izquierda hacia arriba
    for i in range(6):
        path.append((x + CELL_SIZE * 1 + offset, y + CELL_SIZE * (10 - i) + offset))
    
    # Casillas 23-24: Giro en la esquina superior izquierda
    path.append((x + CELL_SIZE * 0 + offset, y + CELL_SIZE * 4 + offset))
    path.append((x + CELL_SIZE * 0 + offset, y + CELL_SIZE * 3 + offset))
    
    # Casillas 25-30: Fila superior hacia la derecha
    for i in range(6):
        path.append((x + CELL_SIZE * i + offset, y + CELL_SIZE * 1 + offset))
    
    # Casillas 31-32: Entrada a la zona superior
    path.append((x + CELL_SIZE * 6 + offset, y + CELL_SIZE * 0 + offset))
    path.append((x + CELL_SIZE * 7 + offset, y + CELL_SIZE * 0 + offset))
    
    # Casillas 33-34: Continuación zona superior
    path.append((x + CELL_SIZE * 8 + offset, y + CELL_SIZE * 0 + offset))
    path.append((x + CELL_SIZE * 8 + offset, y + CELL_SIZE * 1 + offset))
    
    # Casillas 35-40: Columna 8 hacia abajo
    for i in range(6):
        path.append((x + CELL_SIZE * 8 + offset, y + CELL_SIZE * (2 + i) + offset))
    
    # Casillas 41-42: Giro hacia la derecha
    path.append((x + CELL_SIZE * 8 + offset, y + CELL_SIZE * 8 + offset))
    path.append((x + CELL_SIZE * 9 + offset, y + CELL_SIZE * 8 + offset))
    
    # Casillas 43-48: Fila central hacia la derecha
    for i in range(6):
        path.append((x + CELL_SIZE * (9 + i) + offset, y + CELL_SIZE * 7 + offset))
    
    # Casillas 49-50: Giro en la esquina superior derecha
    path.append((x + CELL_SIZE * 14 + offset, y + CELL_SIZE * 2 + offset))
    path.append((x + CELL_SIZE * 14 + offset, y + CELL_SIZE * 3 + offset))
    
    # Casillas 51-56: Columna derecha hacia abajo
    for i in range(6):
        path.append((x + CELL_SIZE * 13 + offset, y + CELL_SIZE * (4 + i) + offset))
    
    # Casillas 57-58: Giro en la esquina inferior derecha
    path.append((x + CELL_SIZE * 14 + offset, y + CELL_SIZE * 10 + offset))
    path.append((x + CELL_SIZE * 14 + offset, y + CELL_SIZE * 11 + offset))
    
    # Casillas 59-64: Fila inferior hacia la izquierda
    for i in range(6):
        path.append((x + CELL_SIZE * (14 - i) + offset, y + CELL_SIZE * 13 + offset))
    
    # Casillas 65-66: Entrada a la zona inferior
    path.append((x + CELL_SIZE * 8 + offset, y + CELL_SIZE * 14 + offset))
    path.append((x + CELL_SIZE * 7 + offset, y + CELL_SIZE * 14 + offset))
    
    # Casillas 67-68: Columna 7 hacia arriba
    path.append((x + CELL_SIZE * 7 + offset, y + CELL_SIZE * 13 + offset))
    path.append((x + CELL_SIZE * 7 + offset, y + CELL_SIZE * 12 + offset))
    
    return path

# Caminos de entrada a casa para cada color
def generate_home_paths():
    """Genera los caminos de entrada a casa para cada color - 8 casillas incluida la meta"""
    x = BOARD_OFFSET_X
    y = BOARD_OFFSET_Y
    offset = CELL_SIZE // 2
    
    home_paths = {
        # Camino rojo: columna central izquierda hacia arriba (8 casillas)
        "red": [(x + CELL_SIZE * 6 + offset, y + CELL_SIZE * (7 - i) + offset) for i in range(8)],
        # Camino verde: fila central superior hacia la derecha (8 casillas)
        "green": [(x + CELL_SIZE * (7 + i) + offset, y + CELL_SIZE * 6 + offset) for i in range(8)],
        # Camino amarillo: columna central derecha hacia abajo (8 casillas)
        "yellow": [(x + CELL_SIZE * 8 + offset, y + CELL_SIZE * (7 + i) + offset) for i in range(8)],
        # Camino azul: fila central inferior hacia la izquierda (8 casillas)
        "blue": [(x + CELL_SIZE * (7 - i) + offset, y + CELL_SIZE * 8 + offset) for i in range(8)]
    }
    
    return home_paths

class Piece:
    """Representa una ficha del juego"""
    def __init__(self, color: str, index: int):
        self.color = color
        self.index = index
        self.position = -1  # -1 significa en casa
        self.is_home = True
        self.is_safe = False
        self.has_finished = False
        self.path_position = 0
        self.home_path_position = -1
        self.on_home_path = False
        self.animation_offset = (0, 0)
        self.is_animating = False
        
        # Cargar imagen de la ficha
        piece_size = int(CELL_SIZE * 0.6)  # Las fichas son 60% del tamaño de la casilla
        try:
            image_path = f"Icons/Ficha {self._get_spanish_color()}.png"
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (piece_size, piece_size))
        except:
            # Si no se puede cargar la imagen, usar un círculo
            self.image = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA)
            radius = piece_size // 2
            pygame.draw.circle(self.image, self._get_pygame_color(), (radius, radius), radius - 2)
            pygame.draw.circle(self.image, BLACK, (radius, radius), radius - 2, 2)
        
        self.rect = self.image.get_rect()
        self.update_position()
    
    def _get_spanish_color(self):
        """Convierte el color a español para cargar las imágenes"""
        colors = {
            "red": "Roja",
            "green": "Verde",
            "blue": "Azul",
            "yellow": "Amarilla"
        }
        return colors.get(self.color, "Roja")
    
    def _get_pygame_color(self):
        """Obtiene el color para pygame"""
        colors = {
            "red": RED,
            "green": GREEN,
            "blue": BLUE,
            "yellow": YELLOW
        }
        return colors.get(self.color, RED)
    
    def update_position(self):
        """Actualiza la posición visual de la ficha"""
        if self.is_home:
            # Posición en casa
            pos = HOME_POSITIONS[self.color][self.index]
            self.rect.center = pos
        elif self.has_finished:
            # En el centro (meta)
            center_x = BOARD_OFFSET_X + BOARD_SIZE // 2
            center_y = BOARD_OFFSET_Y + BOARD_SIZE // 2
            offset = 20
            if self.color == "red":
                self.rect.center = (center_x - offset, center_y - offset)
            elif self.color == "green":
                self.rect.center = (center_x + offset, center_y - offset)
            elif self.color == "yellow":
                self.rect.center = (center_x + offset, center_y + offset)
            else:  # blue
                self.rect.center = (center_x - offset, center_y + offset)
        elif self.on_home_path:
            # En el camino de casa
            if 0 <= self.home_path_position < len(HOME_PATHS[self.color]):
                self.rect.center = HOME_PATHS[self.color][self.home_path_position]
        else:
            # En el camino principal
            if 0 <= self.path_position < len(MAIN_PATH):
                self.rect.center = MAIN_PATH[self.path_position]
        
        # Aplicar offset de animación si está animando
        if self.is_animating:
            self.rect.x += self.animation_offset[0]
            self.rect.y += self.animation_offset[1]
    
    def can_move(self, steps: int) -> bool:
        """Verifica si la ficha puede moverse"""
        if self.has_finished:
            return False
        
        if self.is_home:
            return steps == 6  # Solo puede salir con un 6
        
        if self.on_home_path:
            # Verificar si puede moverse en el camino de casa
            new_position = self.home_path_position + steps
            return new_position <= 7  # Las columnas de color tienen 8 casillas (0-7)
        else:
            # En el camino principal
            current_position = self.path_position
            
            # Verificar si llegará a la entrada de su columna de color
            home_entrance = HOME_ENTRANCE_POSITIONS[self.color]
            
            # Calcular nueva posición considerando el ciclo de 68 casillas
            new_position = current_position + steps
            
            # Verificar si pasará por la entrada a casa
            if current_position < home_entrance:
                if new_position >= home_entrance:
                    # Entrará al camino de casa
                    steps_to_entrance = home_entrance - current_position
                    remaining_steps = steps - steps_to_entrance
                    return remaining_steps <= 8  # No puede pasarse de las 8 casillas
            elif current_position > home_entrance:
                # Si está después de la entrada, verificar si dará la vuelta y llegará
                if new_position > 68:
                    wrapped_position = new_position - 68
                    if wrapped_position >= home_entrance:
                        # Dará la vuelta y pasará por la entrada
                        steps_to_68 = 68 - current_position
                        steps_from_1 = wrapped_position
                        if steps_from_1 >= home_entrance:
                            steps_to_entrance = steps_to_68 + home_entrance
                            remaining_steps = steps - steps_to_entrance
                            return remaining_steps <= 8
            
            return True
    
    def move(self, steps: int):
        """Mueve la ficha"""
        if self.is_home and steps == 6:
            # Salir de casa
            self.is_home = False
            self.path_position = START_POSITIONS[self.color] - 1  # -1 porque el array empieza en 0
            self.is_safe = (self.path_position + 1) in SAFE_POSITIONS
        elif not self.is_home and not self.has_finished:
            if self.on_home_path:
                # Mover en el camino de casa
                self.home_path_position += steps
                if self.home_path_position >= 7:  # Llegó a la flecha (posición 7)
                    self.has_finished = True
                    self.home_path_position = 7
            else:
                # Mover en el camino principal
                current_position = self.path_position
                home_entrance = HOME_ENTRANCE_POSITIONS[self.color]
                new_position = current_position + steps
                
                # Verificar si entrará al camino de casa
                should_enter_home = False
                steps_to_entrance = 0
                
                if current_position < home_entrance:
                    if new_position >= home_entrance:
                        should_enter_home = True
                        steps_to_entrance = home_entrance - current_position
                elif current_position > home_entrance:
                    # Verificar si dará la vuelta y entrará
                    if new_position > 68:
                        wrapped_position = new_position - 68
                        if wrapped_position >= home_entrance:
                            should_enter_home = True
                            steps_to_entrance = (68 - current_position) + home_entrance
                
                if should_enter_home:
                    # Entrar al camino de casa
                    remaining_steps = steps - steps_to_entrance
                    self.on_home_path = True
                    self.home_path_position = remaining_steps - 1
                    if self.home_path_position >= 7:
                        self.has_finished = True
                        self.home_path_position = 7
                else:
                    # Movimiento normal en el camino principal
                    if new_position > 68:
                        self.path_position = new_position - 68
                    else:
                        self.path_position = new_position
                    
                    # Actualizar si está en posición segura
                    self.is_safe = (self.path_position + 1) in SAFE_POSITIONS
        
        self.update_position()
    
    def send_home(self):
        """Envía la ficha de vuelta a casa"""
        self.is_home = True
        self.path_position = 0
        self.home_path_position = -1
        self.on_home_path = False
        self.is_safe = True
        self.update_position()
    
    def draw(self, screen: pygame.Surface):
        """Dibuja la ficha"""
        screen.blit(self.image, self.rect)
        
        # Dibujar un pequeño círculo si está en una posición segura
        if self.is_safe and not self.is_home and not self.has_finished:
            pygame.draw.circle(screen, WHITE, self.rect.center, 8)
            pygame.draw.circle(screen, BLACK, self.rect.center, 8, 2)

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
    
    def get_movable_pieces(self, dice_value: int) -> List[Piece]:
        """Obtiene las fichas que pueden moverse"""
        movable = []
        for piece in self.pieces:
            if piece.can_move(dice_value):
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
    
    def ai_select_piece(self, movable_pieces: List[Piece], all_players: List['Player'], dice_value: int) -> Optional[Piece]:
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
                # Calcular distancia a la meta considerando entrada a casa
                home_entrance = HOME_ENTRANCE_POSITIONS[self.color]
                if piece.path_position <= home_entrance:
                    distance_to_home = home_entrance - piece.path_position
                else:
                    distance_to_home = (68 - piece.path_position) + home_entrance
                score += (68 - distance_to_home)
            
            # Bonus por capturar oponentes
            future_position = piece.path_position + dice_value
            if future_position > 68:
                future_position = future_position - 68
            for player in all_players:
                if player.color != self.color:
                    for enemy_piece in player.pieces:
                        if (not enemy_piece.is_home and not enemy_piece.has_finished and 
                            not enemy_piece.on_home_path and enemy_piece.path_position == future_position and
                            not enemy_piece.is_safe):
                            score += 100  # Gran bonus por capturar
            
            # Penalización por estar en peligro
            if not piece.is_safe:
                for player in all_players:
                    if player.color != self.color:
                        for enemy_piece in player.pieces:
                            if not enemy_piece.is_home and not enemy_piece.has_finished:
                                distance = enemy_piece.path_position - piece.path_position
                                if 0 < distance <= 6:
                                    score -= 20  # Penalización por estar en peligro
            
            if score > best_score:
                best_score = score
                best_piece = piece
        
        return best_piece

class Board:
    """Representa el tablero del juego"""
    def __init__(self):
        # Siempre crear el tablero programáticamente
        self.image = self._create_detailed_board()
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    
    def _create_detailed_board(self) -> pygame.Surface:
        """Crea un tablero detallado de Ludo"""
        global MAIN_PATH
        surface = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
        surface.fill((250, 248, 240))  # Fondo beige claro
        
        # Configuración
        house_size = CELL_SIZE * 6
        
        # Dibujar todas las casillas del tablero primero
        for i in range(15):
            for j in range(15):
                rect = pygame.Rect(i * CELL_SIZE, j * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, BLACK, rect, 1)
        
        # Dibujar las zonas de casa
        # Casa roja (arriba izquierda)
        pygame.draw.rect(surface, RED, (0, 0, house_size, house_size))
        pygame.draw.rect(surface, WHITE, (CELL_SIZE, CELL_SIZE, house_size - CELL_SIZE * 2, house_size - CELL_SIZE * 2))
        
        # Casa verde (arriba derecha)  
        pygame.draw.rect(surface, GREEN, (CELL_SIZE * 9, 0, house_size, house_size))
        pygame.draw.rect(surface, WHITE, (CELL_SIZE * 10, CELL_SIZE, house_size - CELL_SIZE * 2, house_size - CELL_SIZE * 2))
        
        # Casa azul (abajo izquierda)
        pygame.draw.rect(surface, BLUE, (0, CELL_SIZE * 9, house_size, house_size))
        pygame.draw.rect(surface, WHITE, (CELL_SIZE, CELL_SIZE * 10, house_size - CELL_SIZE * 2, house_size - CELL_SIZE * 2))
        
        # Casa amarilla (abajo derecha)
        pygame.draw.rect(surface, YELLOW, (CELL_SIZE * 9, CELL_SIZE * 9, house_size, house_size))
        pygame.draw.rect(surface, WHITE, (CELL_SIZE * 10, CELL_SIZE * 10, house_size - CELL_SIZE * 2, house_size - CELL_SIZE * 2))
        
        # Dibujar círculos en las posiciones de inicio dentro de las casas
        for color, positions in HOME_POSITIONS.items():
            for pos in positions:
                x, y = pos[0] - BOARD_OFFSET_X, pos[1] - BOARD_OFFSET_Y
                pygame.draw.circle(surface, GRAY, (int(x), int(y)), CELL_SIZE // 3)
                pygame.draw.circle(surface, BLACK, (int(x), int(y)), CELL_SIZE // 3, 2)
        
        # Dibujar los caminos de casa (las zonas coloreadas centrales)
        # Camino rojo (columna central hacia arriba)
        for i in range(6):
            rect = pygame.Rect(CELL_SIZE * 7, CELL_SIZE * (1 + i), CELL_SIZE, CELL_SIZE)
            color = RED if i < 5 else WHITE  # La última es blanca (meta)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 2)
        
        # Camino verde (fila central hacia la derecha)
        for i in range(6):
            rect = pygame.Rect(CELL_SIZE * (8 + i), CELL_SIZE * 7, CELL_SIZE, CELL_SIZE)
            color = GREEN if i < 5 else WHITE
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 2)
        
        # Camino amarillo (columna central hacia abajo)
        for i in range(6):
            rect = pygame.Rect(CELL_SIZE * 7, CELL_SIZE * (8 + i), CELL_SIZE, CELL_SIZE)
            color = YELLOW if i < 5 else WHITE
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 2)
        
        # Camino azul (fila central hacia la izquierda)
        for i in range(6):
            rect = pygame.Rect(CELL_SIZE * (6 - i), CELL_SIZE * 7, CELL_SIZE, CELL_SIZE)
            color = BLUE if i < 5 else WHITE
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 2)
        
        # Dibujar el centro (meta)
        center_rect = pygame.Rect(CELL_SIZE * 6, CELL_SIZE * 6, CELL_SIZE * 3, CELL_SIZE * 3)
        pygame.draw.rect(surface, BLACK, center_rect, 3)
        
        # Triángulos en el centro
        center = BOARD_SIZE // 2
        
        # Triángulo rojo
        points = [(center - CELL_SIZE, center), (center, center - CELL_SIZE), (center, center)]
        pygame.draw.polygon(surface, RED, points)
        pygame.draw.polygon(surface, BLACK, points, 2)
        
        # Triángulo verde
        points = [(center, center - CELL_SIZE), (center + CELL_SIZE, center), (center, center)]
        pygame.draw.polygon(surface, GREEN, points)
        pygame.draw.polygon(surface, BLACK, points, 2)
        
        # Triángulo amarillo
        points = [(center + CELL_SIZE, center), (center, center + CELL_SIZE), (center, center)]
        pygame.draw.polygon(surface, YELLOW, points)
        pygame.draw.polygon(surface, BLACK, points, 2)
        
        # Triángulo azul
        points = [(center, center + CELL_SIZE), (center - CELL_SIZE, center), (center, center)]
        pygame.draw.polygon(surface, BLUE, points)
        pygame.draw.polygon(surface, BLACK, points, 2)
        
        # Marcar las casillas de inicio con flechas según las posiciones reales
        # Las posiciones están basadas en el array MAIN_PATH generado
        if MAIN_PATH:
            # Inicio amarillo (casilla 5)
            if 4 < len(MAIN_PATH):
                x, y = MAIN_PATH[4]  # Índice 4 = casilla 5
                x -= BOARD_OFFSET_X
                y -= BOARD_OFFSET_Y
                start_rect = pygame.Rect(x - CELL_SIZE // 2, y - CELL_SIZE // 2, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, YELLOW, start_rect)
                pygame.draw.rect(surface, BLACK, start_rect, 3)
                self._draw_arrow(surface, x, y, "down", WHITE)
            
            # Inicio azul (casilla 22)
            if 21 < len(MAIN_PATH):
                x, y = MAIN_PATH[21]  # Índice 21 = casilla 22
                x -= BOARD_OFFSET_X
                y -= BOARD_OFFSET_Y
                start_rect = pygame.Rect(x - CELL_SIZE // 2, y - CELL_SIZE // 2, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, BLUE, start_rect)
                pygame.draw.rect(surface, BLACK, start_rect, 3)
                self._draw_arrow(surface, x, y, "right", WHITE)
            
            # Inicio rojo (casilla 39)
            if 38 < len(MAIN_PATH):
                x, y = MAIN_PATH[38]  # Índice 38 = casilla 39
                x -= BOARD_OFFSET_X
                y -= BOARD_OFFSET_Y
                start_rect = pygame.Rect(x - CELL_SIZE // 2, y - CELL_SIZE // 2, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, RED, start_rect)
                pygame.draw.rect(surface, BLACK, start_rect, 3)
                self._draw_arrow(surface, x, y, "up", WHITE)
            
            # Inicio verde (casilla 56)
            if 55 < len(MAIN_PATH):
                x, y = MAIN_PATH[55]  # Índice 55 = casilla 56
                x -= BOARD_OFFSET_X
                y -= BOARD_OFFSET_Y
                start_rect = pygame.Rect(x - CELL_SIZE // 2, y - CELL_SIZE // 2, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, GREEN, start_rect)
                pygame.draw.rect(surface, BLACK, start_rect, 3)
                self._draw_arrow(surface, x, y, "down", WHITE)
        
        # Marcar las casillas seguras con estrellas
        # Estas deben coincidir con las posiciones del camino
        if MAIN_PATH:  # Solo si el camino ya ha sido generado
            for i, pos in enumerate(SAFE_POSITIONS):
                if pos <= len(MAIN_PATH):
                    x, y = MAIN_PATH[pos - 1]  # -1 porque SAFE_POSITIONS usa numeración 1-68
                    x -= BOARD_OFFSET_X
                    y -= BOARD_OFFSET_Y
                    # Dibujar estrella en la casilla
                    pygame.draw.rect(surface, (255, 255, 200), (x - CELL_SIZE // 2, y - CELL_SIZE // 2, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(surface, BLACK, (x - CELL_SIZE // 2, y - CELL_SIZE // 2, CELL_SIZE, CELL_SIZE), 1)
                    self._draw_star(surface, x, y, 15, GRAY)
        
        # Dibujar números en las casillas del camino principal
        if MAIN_PATH:
            number_font = pygame.font.Font(None, 16)
            for i, pos in enumerate(MAIN_PATH):
                x, y = pos
                x -= BOARD_OFFSET_X
                y -= BOARD_OFFSET_Y
                
                # Dibujar el número de la casilla (1-68)
                number_text = number_font.render(str(i + 1), True, BLACK)
                number_rect = number_text.get_rect(center=(x, y))
                surface.blit(number_text, number_rect)
        
        return surface
    
    def _draw_star(self, surface, x, y, size, color):
        """Dibuja una estrella en la superficie"""
        angle = -math.pi / 2
        points = []
        for i in range(10):
            r = size if i % 2 == 0 else size // 2
            px = x + r * math.cos(angle)
            py = y + r * math.sin(angle)
            points.append((px, py))
            angle += math.pi / 5
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, BLACK, points, 1)
    
    def _draw_arrow(self, surface, x, y, direction, color):
        """Dibuja una flecha en la dirección especificada"""
        arrow_size = CELL_SIZE // 3
        
        if direction == "up":
            points = [
                (x, y - arrow_size),
                (x - arrow_size // 2, y + arrow_size // 2),
                (x + arrow_size // 2, y + arrow_size // 2)
            ]
        elif direction == "down":
            points = [
                (x, y + arrow_size),
                (x - arrow_size // 2, y - arrow_size // 2),
                (x + arrow_size // 2, y - arrow_size // 2)
            ]
        elif direction == "left":
            points = [
                (x - arrow_size, y),
                (x + arrow_size // 2, y - arrow_size // 2),
                (x + arrow_size // 2, y + arrow_size // 2)
            ]
        elif direction == "right":
            points = [
                (x + arrow_size, y),
                (x - arrow_size // 2, y - arrow_size // 2),
                (x - arrow_size // 2, y + arrow_size // 2)
            ]
        
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, BLACK, points, 2)
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el tablero"""
        screen.blit(self.image, self.rect)

class LudoGame:
    """Clase principal del juego"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Ludo - Juego Interactivo")
        pygame.display.set_icon(pygame.Surface((32, 32)))  # Icono vacío por ahora
        self.clock = pygame.time.Clock()
        
        # Generar los caminos del tablero
        global MAIN_PATH, HOME_PATHS
        MAIN_PATH = generate_board_path()
        HOME_PATHS = generate_home_paths()
        
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
        """Verifica si una ficha captura a otra"""
        if piece.is_safe or piece.on_home_path:
            return
        
        for player in self.players:
            if player.color != piece.color:
                for enemy_piece in player.pieces:
                    if (not enemy_piece.is_home and not enemy_piece.has_finished and 
                        not enemy_piece.on_home_path and not enemy_piece.is_safe and
                        enemy_piece.path_position == piece.path_position):
                        enemy_piece.send_home()
                        self.add_message(f"¡{piece.color} captura a {enemy_piece.color}!", 2000)
    
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
            movable_pieces = current_player.get_movable_pieces(self.dice.value)
            
            for piece in movable_pieces:
                if piece.rect.collidepoint(pos):
                    old_position = piece.path_position
                    piece.move(self.dice.value)
                    current_player.has_moved = True
                    
                    # Verificar capturas
                    self.check_captures(piece)
                    
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
                                # Tres 6 seguidos, pierde el turno
                                self.add_message("¡Tres 6 seguidos! Pierdes el turno", 2000)
                                self.next_turn()
                            else:
                                # Puede tirar de nuevo
                                current_player.can_roll = True
                                current_player.has_moved = False
                                self.add_message("¡Sacaste un 6! Tira de nuevo", 1500)
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
            selected_piece = current_player.ai_select_piece(movable_pieces, self.players, self.dice.value)
            
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