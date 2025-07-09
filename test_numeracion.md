# Prueba del Sistema de Numeración del Tablero de Ludo

## Cambios Implementados

Se ha agregado un sistema de numeración visual al tablero de Ludo para facilitar el seguimiento del movimiento de las fichas:

### 1. **Numeración del Recorrido Principal**
- Los números grises pequeños (1-52) en la parte inferior de cada casilla muestran la posición absoluta en el recorrido principal
- Estos números son fijos y ayudan a entender la estructura del tablero

### 2. **Numeración Relativa del Jugador**
- Números azules más grandes que muestran el recorrido desde la perspectiva del jugador actual
- El número "1" aparece en la casilla de salida del jugador (marcada con un círculo del color del jugador)
- Los números van del 1 al 52 siguiendo el recorrido que debe hacer cada ficha

### 3. **Marcadores Especiales**
- **Estrella dorada (★)**: Marca las casillas de salida de cada color
- **Pasillos finales**: Marcados con letras y números (R1-R6 para rojo, G1-G6 para verde, etc.)

## Cómo Probar

1. **Iniciar el servidor**:
   ```
   python server.py
   ```
   O usar la interfaz administrativa:
   ```
   python admin_gui.py
   ```

2. **Conectar clientes**:
   ```
   python client.py
   ```
   - Necesitas al menos 2 jugadores para iniciar una partida
   - Usa las credenciales registradas o crea nuevos usuarios

3. **Observar la numeración**:
   - Cada jugador verá los números desde su perspectiva
   - La casilla "1" será su casilla de salida
   - Los números seguirán el recorrido en sentido horario

## Reglas del Movimiento (según el código actual)

- Las fichas salen de la base solo con un 6
- Avanzan el número de casillas indicado por el dado
- Al llegar cerca de su pasillo final (después de dar la vuelta completa), pueden entrar si el dado lo permite
- Los pasillos finales están numerados como R1-R6, G1-G6, Y1-Y6, B1-B6

## Beneficios de la Numeración

1. **Claridad Visual**: Es fácil ver cuántas casillas debe avanzar una ficha
2. **Perspectiva del Jugador**: Cada jugador ve los números desde su punto de partida
3. **Debugging**: Facilita verificar que el movimiento de las fichas sea correcto
4. **Aprendizaje**: Ayuda a nuevos jugadores a entender el recorrido del juego 