# Juego de Ludo Interactivo

Un juego de Ludo (Parchís) interactivo desarrollado en Python usando Pygame.

## Características

- **Multijugador local**: Soporta de 2 a 4 jugadores
- **Modo contra IA**: Juega contra oponentes controlados por computadora
- **Interfaz gráfica**: Interfaz intuitiva y fácil de usar con tablero programático mejorado
- **Animaciones**: Dado animado y efectos visuales
- **Reglas completas**: Implementa todas las reglas tradicionales del Ludo
- **Gráficos personalizados**: Usa las imágenes proporcionadas en la carpeta Icons
- **Sistema de pausas**: Presiona ESC para pausar en cualquier momento
- **Casillas seguras**: Marcadas con estrellas donde las fichas no pueden ser capturadas
- **Indicadores visuales**: Las fichas que pueden moverse se resaltan con animación
- **Mensajes informativos**: Notificaciones en pantalla sobre eventos del juego

## Requisitos

- Python 3.6 o superior
- Pygame 2.5.2

## Instalación

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Cómo jugar

1. Ejecuta el juego (recomendado usar la versión mejorada):
```bash
python ludo_game_improved.py
```

O si prefieres la versión básica:
```bash
python ludo_game.py
```

2. En el menú principal, selecciona el número de jugadores (2-4)

3. **Reglas del juego**:
   - Cada jugador tiene 4 fichas que deben llegar desde su casa hasta el centro del tablero
   - Para sacar una ficha de casa, debes sacar un 6 en el dado
   - Si sacas un 6, puedes tirar el dado nuevamente
   - Puedes capturar las fichas de otros jugadores si caes en la misma casilla
   - Las casillas con estrellas son zonas seguras donde no puedes ser capturado
   - El primer jugador en llevar todas sus fichas al centro gana

4. **Controles**:
   - Click en el botón "Tirar Dado" o presiona Espacio para lanzar el dado
   - Click en una ficha resaltada para moverla
   - Presiona ESC para pausar el juego

## Estructura del proyecto

```
Redes/
├── ludo_game.py           # Versión básica del juego
├── ludo_game_improved.py  # Versión mejorada con tablero programático
├── requirements.txt       # Dependencias del proyecto
├── README.md             # Este archivo
└── Icons/                # Carpeta con los recursos gráficos
    ├── Ludo_board.svg.png
    ├── Ficha Roja.png
    ├── Ficha Verde.png
    ├── Ficha Azul.png
    ├── Ficha Amarilla.png
    ├── dado-uno.png
    ├── dados-dos.png
    ├── dados-tres.png
    ├── dados-cuatro.png
    ├── dado.png
    └── dados-seis.png
```

## Versiones del juego

### ludo_game.py
- Versión básica del juego
- Usa la imagen del tablero proporcionada
- Todo feo
- Nada tiene sentido

### ludo_game_improved.py
- Versión mejorada con tablero generado programáticamente
- Mejor alineación de fichas con las casillas
- Incluye modo contra IA
- Efectos visuales mejorados
- Sistema de pausas
- Animaciones más fluidas


## Solución de problemas

Si el juego no muestra las imágenes correctamente:
1. Asegúrate de que la carpeta `Icons` esté en el mismo directorio que `ludo_game.py`
2. Verifica que todos los archivos de imagen estén presentes
3. El juego creará gráficos alternativos si no puede cargar las imágenes

## Por Hacer
1. Por donde sale la ficha y donde se mueve
2. Todo lo que tiene que ver con redes
3. Sistema de comer, puntos y paranoias
4. Basicamente todo el proyecto
5. Mas cosas


## Créditos

Desarrollado como un juego educativo de Ludo usando Python y Pygame. 
Empezado por Daniel Castellanos (mentira)