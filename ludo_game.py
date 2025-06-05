import pygame
import sys
import random
import math
from enum import Enum
from typing import List, Tuple, Dict, Optional

# Inicializar pygame
pygame.init()

# Constantes
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
FPS = 60

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

# Estados del juego
class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    ROLLING_DICE = "rolling_dice"
    MOVING_PIECE = "moving_piece"
    GAME_OVER = "game_over"

# Posiciones del tablero (simplificado para las 4 casas de inicio)
STARTING_POSITIONS = {
    "red": [(100, 100), (150, 100), (100, 150), (150, 150)],
    "green": [(550, 100), (600, 100), (550, 150), (600, 150)],
    "yellow": [(550, 550), (600, 550), (550, 600), (600, 600)],
    "blue": [(100, 550), (150, 550), (100, 600), (150, 600)]
}

# Camino principal del juego (52 casillas)
# Estas son las coordenadas simplificadas del camino principal
MAIN_PATH = []

# Generar el camino principal (ejemplo simplificado)
def generate_main_path():
    path = []
    # Este es un ejemplo simplificado - en un juego real necesitarías 
    # las coordenadas exactas de cada casilla del tablero
    
    # Lado superior
    for i in range(6):
        path.append((250 + i * 50, 50))
    
    # Bajada derecha
    for i in range(6):
        path.append((500, 100 + i * 50))
    
    # Centro derecha
    path.append((550, 350))
    
    # Entrada derecha
    for i in range(6):
        path.append((500, 400 + i * 50))
    
    # Lado inferior
    for i in range(6):
        path.append((450 - i * 50, 650))
    
    # Subida izquierda
    for i in range(6):
        path.append((200, 600 - i * 50))
    
    # Centro izquierda
    path.append((150, 350))
    
    # Entrada izquierda
    for i in range(6):
        path.append((200, 300 - i * 50))
    
    return path

class Piece:
    """Representa una ficha del juego"""
    def __init__(self, color: str, index: int):
        self.color = color
        self.index = index
        self.position = -1  # -1 significa en casa
        self.is_home = True
        self.is_safe = True
        self.has_finished = False
        self.path_position = 0
        
        # Cargar imagen de la ficha
        try:
            image_path = f"Icons/Ficha {self._get_spanish_color()}.png"
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (30, 30))
        except:
            # Si no se puede cargar la imagen, usar un círculo
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self._get_pygame_color(), (15, 15), 15)
        
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
            pos = STARTING_POSITIONS[self.color][self.index]
            self.rect.center = pos
        elif not self.has_finished:
            # Posición en el tablero
            if 0 <= self.path_position < len(MAIN_PATH):
                self.rect.center = MAIN_PATH[self.path_position]
    
    def can_move(self, steps: int) -> bool:
        """Verifica si la ficha puede moverse"""
        if self.has_finished:
            return False
        
        if self.is_home:
            return steps == 6  # Solo puede salir con un 6
        
        # Verificar si el movimiento es válido
        new_position = self.path_position + steps
        return new_position < len(MAIN_PATH) + 6  # +6 para la zona de llegada
    
    def move(self, steps: int):
        """Mueve la ficha"""
        if self.is_home and steps == 6:
            self.is_home = False
            self.is_safe = False
            self.path_position = self._get_starting_position()
        elif not self.is_home:
            self.path_position += steps
            
            # Verificar si llegó a la meta
            if self.path_position >= len(MAIN_PATH):
                self.has_finished = True
        
        self.update_position()
    
    def _get_starting_position(self) -> int:
        """Obtiene la posición inicial en el camino según el color"""
        start_positions = {
            "red": 0,
            "green": 13,
            "yellow": 26,
            "blue": 39
        }
        return start_positions.get(self.color, 0)
    
    def draw(self, screen: pygame.Surface):
        """Dibuja la ficha"""
        screen.blit(self.image, self.rect)

class Dice:
    """Representa el dado del juego"""
    def __init__(self):
        self.value = 1
        self.rolling = False
        self.roll_timer = 0
        self.images = {}
        
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
                self.images[num] = pygame.transform.scale(self.images[num], (80, 80))
            except:
                # Si no se puede cargar, crear una imagen simple
                self.images[num] = self._create_dice_image(num)
        
        self.rect = pygame.Rect(360, 360, 80, 80)
    
    def _create_dice_image(self, number: int) -> pygame.Surface:
        """Crea una imagen simple del dado si no se puede cargar"""
        surface = pygame.Surface((80, 80))
        surface.fill(WHITE)
        pygame.draw.rect(surface, BLACK, surface.get_rect(), 2)
        
        font = pygame.font.Font(None, 48)
        text = font.render(str(number), True, BLACK)
        text_rect = text.get_rect(center=(40, 40))
        surface.blit(text, text_rect)
        
        return surface
    
    def roll(self):
        """Inicia la animación de tirar el dado"""
        self.rolling = True
        self.roll_timer = 30  # 30 frames de animación
    
    def update(self):
        """Actualiza la animación del dado"""
        if self.rolling:
            if self.roll_timer > 0:
                self.value = random.randint(1, 6)
                self.roll_timer -= 1
            else:
                self.rolling = False
                return True  # Indica que terminó de rodar
        return False
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el dado"""
        if self.value in self.images:
            screen.blit(self.images[self.value], self.rect)

class Player:
    """Representa un jugador"""
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color
        self.pieces = [Piece(color, i) for i in range(4)]
        self.finished_pieces = 0
        self.can_roll = True
        self.has_moved = False
    
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
    
    def draw_info(self, screen: pygame.Surface, position: Tuple[int, int]):
        """Dibuja la información del jugador"""
        font = pygame.font.Font(None, 24)
        text = font.render(f"{self.name}: {self.finished_pieces}/4", True, BLACK)
        screen.blit(text, position)

class Board:
    """Representa el tablero del juego"""
    def __init__(self):
        # Cargar imagen del tablero
        try:
            self.image = pygame.image.load("Icons/Ludo_board.svg.png")
            self.image = pygame.transform.scale(self.image, (700, 700))
        except:
            # Si no se puede cargar, crear un tablero simple
            self.image = self._create_simple_board()
        
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    
    def _create_simple_board(self) -> pygame.Surface:
        """Crea un tablero simple si no se puede cargar la imagen"""
        surface = pygame.Surface((700, 700))
        surface.fill(WHITE)
        
        # Dibujar las casas de colores
        pygame.draw.rect(surface, RED, (0, 0, 280, 280))
        pygame.draw.rect(surface, GREEN, (420, 0, 280, 280))
        pygame.draw.rect(surface, BLUE, (0, 420, 280, 280))
        pygame.draw.rect(surface, YELLOW, (420, 420, 280, 280))
        
        # Dibujar el centro
        pygame.draw.rect(surface, GRAY, (280, 280, 140, 140))
        
        return surface
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el tablero"""
        screen.blit(self.image, self.rect)

class LudoGame:
    """Clase principal del juego"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Ludo - Juego Interactivo")
        self.clock = pygame.time.Clock()
        
        # Generar el camino principal
        global MAIN_PATH
        MAIN_PATH = generate_main_path()
        
        # Componentes del juego
        self.board = Board()
        self.dice = Dice()
        self.players = []
        self.current_player_index = 0
        self.state = GameState.MENU
        
        # Fuentes
        self.title_font = pygame.font.Font(None, 48)
        self.menu_font = pygame.font.Font(None, 32)
        self.info_font = pygame.font.Font(None, 24)
        
        # Botones del menú
        self.menu_buttons = {
            "2_players": pygame.Rect(300, 300, 200, 50),
            "3_players": pygame.Rect(300, 370, 200, 50),
            "4_players": pygame.Rect(300, 440, 200, 50)
        }
        
        # Botón para tirar el dado
        self.roll_button = pygame.Rect(350, 720, 100, 40)
        
        self.winner = None
        self.selected_piece = None
    
    def start_game(self, num_players: int):
        """Inicia una nueva partida"""
        colors = ["red", "green", "yellow", "blue"]
        names = ["Jugador 1", "Jugador 2", "Jugador 3", "Jugador 4"]
        
        self.players = []
        for i in range(num_players):
            self.players.append(Player(names[i], colors[i]))
        
        self.current_player_index = 0
        self.state = GameState.PLAYING
    
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
    
    def handle_game_click(self, pos: Tuple[int, int]):
        """Maneja los clicks durante el juego"""
        current_player = self.players[self.current_player_index]
        
        # Click en el botón de tirar dado
        if self.roll_button.collidepoint(pos) and current_player.can_roll and not self.dice.rolling:
            self.dice.roll()
            self.state = GameState.ROLLING_DICE
            current_player.can_roll = False
            return
        
        # Click en una ficha
        if not current_player.can_roll and not current_player.has_moved:
            movable_pieces = current_player.get_movable_pieces(self.dice.value)
            
            for piece in movable_pieces:
                if piece.rect.collidepoint(pos):
                    piece.move(self.dice.value)
                    current_player.has_moved = True
                    
                    # Verificar si ganó
                    if current_player.check_winner():
                        self.winner = current_player
                        self.state = GameState.GAME_OVER
                    else:
                        # Siguiente turno
                        if self.dice.value != 6:
                            self.next_turn()
                        else:
                            # Si sacó 6, puede tirar de nuevo
                            current_player.can_roll = True
                            current_player.has_moved = False
                    break
    
    def next_turn(self):
        """Pasa al siguiente turno"""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        current_player = self.players[self.current_player_index]
        current_player.can_roll = True
        current_player.has_moved = False
    
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
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.MENU
        
        return True
    
    def update(self):
        """Actualiza la lógica del juego"""
        if self.state == GameState.ROLLING_DICE:
            if self.dice.update():
                self.state = GameState.PLAYING
                
                # Si no hay fichas que mover, pasar turno
                current_player = self.players[self.current_player_index]
                if not current_player.get_movable_pieces(self.dice.value):
                    if self.dice.value != 6:
                        self.next_turn()
                    else:
                        current_player.can_roll = True
    
    def draw_menu(self):
        """Dibuja el menú principal"""
        self.screen.fill(WHITE)
        
        # Título
        title = self.title_font.render("LUDO", True, BLACK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Subtítulo
        subtitle = self.menu_font.render("Selecciona número de jugadores", True, BLACK)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Botones
        for button_name, rect in self.menu_buttons.items():
            pygame.draw.rect(self.screen, GRAY, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            
            if button_name == "2_players":
                text = "2 Jugadores"
            elif button_name == "3_players":
                text = "3 Jugadores"
            else:
                text = "4 Jugadores"
            
            text_surface = self.menu_font.render(text, True, BLACK)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def draw_game(self):
        """Dibuja el juego"""
        self.screen.fill(WHITE)
        
        # Dibujar tablero
        self.board.draw(self.screen)
        
        # Dibujar fichas
        for player in self.players:
            for piece in player.pieces:
                piece.draw(self.screen)
        
        # Dibujar dado
        self.dice.draw(self.screen)
        
        # Dibujar botón de tirar dado
        current_player = self.players[self.current_player_index]
        if current_player.can_roll and not self.dice.rolling:
            pygame.draw.rect(self.screen, GREEN, self.roll_button)
            pygame.draw.rect(self.screen, BLACK, self.roll_button, 2)
            
            text = self.info_font.render("Tirar Dado", True, BLACK)
            text_rect = text.get_rect(center=self.roll_button.center)
            self.screen.blit(text, text_rect)
        
        # Información de los jugadores
        y_pos = 10
        for i, player in enumerate(self.players):
            color = BLACK
            if i == self.current_player_index:
                color = player._get_pygame_color() if hasattr(player, '_get_pygame_color') else BLACK
            
            text = self.info_font.render(f"{player.name}", True, color)
            self.screen.blit(text, (10, y_pos))
            y_pos += 30
        
        # Mostrar de quién es el turno
        turn_text = self.menu_font.render(f"Turno: {current_player.name}", True, BLACK)
        self.screen.blit(turn_text, (WINDOW_WIDTH - 200, 10))
        
        # Mostrar valor del dado
        if not self.dice.rolling:
            dice_text = self.info_font.render(f"Dado: {self.dice.value}", True, BLACK)
            self.screen.blit(dice_text, (360, 450))
        
        # Instrucciones
        if current_player.can_roll:
            inst_text = self.info_font.render("Presiona el botón para tirar el dado", True, GRAY)
        elif not current_player.has_moved:
            movable = current_player.get_movable_pieces(self.dice.value)
            if movable:
                inst_text = self.info_font.render("Haz clic en una ficha para moverla", True, GRAY)
            else:
                inst_text = self.info_font.render("No puedes mover ninguna ficha", True, GRAY)
        else:
            inst_text = self.info_font.render("", True, GRAY)
        
        inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        self.screen.blit(inst_text, inst_rect)
    
    def draw_game_over(self):
        """Dibuja la pantalla de fin de juego"""
        self.screen.fill(WHITE)
        
        # Mensaje de victoria
        win_text = self.title_font.render(f"¡{self.winner.name} ha ganado!", True, BLACK)
        win_rect = win_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(win_text, win_rect)
        
        # Instrucción para continuar
        cont_text = self.menu_font.render("Haz clic para volver al menú", True, GRAY)
        cont_rect = cont_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(cont_text, cont_rect)
    
    def draw(self):
        """Dibuja la pantalla según el estado del juego"""
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state in [GameState.PLAYING, GameState.ROLLING_DICE, GameState.MOVING_PIECE]:
            self.draw_game()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        
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