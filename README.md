# Ludo en Red - Proyecto Interactivo

Este proyecto implementa el juego de Ludo (Parchís) en red usando Python, con arquitectura cliente-servidor y control administrativo. Permite partidas de 2 a 4 jugadores, con reglas oficiales y una interfaz gráfica profesional.

---

## Arquitectura General y Archivos Principales

### 1. **admin_gui.py**
- Es la interfaz gráfica de administración del servidor.
- Permite al admin elegir IP y puerto, iniciar/detener el servidor, ver usuarios registrados, conectados y autenticados.
- Controla el inicio y fin de la partida.
- Se comunica directamente con `server.py` (importa y controla la clase `LudoServer`).
- Actualiza en tiempo real la lista de usuarios y el estado del juego.

### 2. **server.py**
- Contiene toda la lógica del servidor y del juego.
- Clases principales:
  - **LudoServer**: Maneja conexiones TCP, usuarios, turnos, y la lógica de red.
  - **Board, Piece, Player**: Representan el estado del tablero, fichas y jugadores.
  - **Funciones de red**: Envío y recepción de mensajes JSON por socket.
- El servidor solo inicia el socket cuando el admin lo decide desde la GUI.
- Gestiona la autenticación, el flujo de turnos, el movimiento de fichas, reglas de Ludo, y la comunicación con todos los clientes conectados.

### 3. **client.py**
- Es la aplicación gráfica para los jugadores.
- Permite login y registro, conexión al servidor, y muestra el tablero y fichas en tiempo real.
- Recibe actualizaciones del servidor y permite lanzar el dado y mover fichas solo cuando es el turno del jugador.
- Toda la lógica de validación de movimientos y reglas se centraliza en el servidor, el cliente solo envía comandos y muestra el estado.

### 4. **users.json**
- Base de datos persistente de usuarios registrados (login, clave, nombre, apellido).

### 5. **Icons/**
- Carpeta con imágenes de fichas, dados y tablero para la interfaz gráfica.

---

## Flujo de Corrida del Proyecto (de principio a fin)

### 1. **Arranque del servidor (admin)**
- El admin ejecuta `python admin_gui.py`.
- En la GUI, elige IP y puerto y presiona "Iniciar Servidor".
- El servidor (`LudoServer`) crea el socket y comienza a aceptar conexiones de clientes.
- El admin puede agregar usuarios o esperar a que los jugadores se registren desde el cliente.

### 2. **Conexión de los clientes**
- Cada jugador ejecuta `python client.py`.
- En la ventana de login, ingresa la IP y puerto del servidor, usuario y clave (o se registra).
- El cliente se conecta al servidor y, si las credenciales son correctas, queda autenticado y visible en la GUI del admin.

### 3. **Inicio de la partida**
- Cuando hay entre 2 y 4 jugadores autenticados, el admin presiona "Iniciar Partida".
- El servidor asigna colores, inicializa el tablero y notifica a todos los clientes el inicio.

### 4. **Desarrollo del juego**
- El servidor gestiona el turno de cada jugador y envía el estado actualizado a todos los clientes.
- Solo el jugador cuyo turno es puede lanzar el dado y mover fichas.
- El cliente envía comandos de lanzar dado o mover ficha, el servidor valida y actualiza el estado.
- Se aplican todas las reglas de Ludo: salidas con 6, bloqueos, casillas seguras, pasillos finales, tres 6 seguidos, etc.
- El tablero y las fichas se actualizan en tiempo real en todos los clientes.

### 5. **Fin de la partida**
- Cuando un jugador lleva todas sus fichas a la meta, el servidor notifica el final y el ganador a todos los clientes.
- El admin puede detener la partida o reiniciar el servidor para una nueva ronda.

---

## Diagrama de Flujo (texto)

```
[Admin abre admin_gui.py]
      |
      v
[Elige IP/puerto y presiona 'Iniciar Servidor']
      |
      v
[Servidor escucha conexiones]
      |
      v
[Jugadores abren client.py y se conectan]
      |
      v
[Login/Registro exitoso]
      |
      v
[Admin ve usuarios conectados]
      |
      v
[Admin presiona 'Iniciar Partida']
      |
      v
[Servidor asigna colores y notifica inicio]
      |
      v
[Turnos: cada jugador lanza dado y mueve]
      |
      v
[Servidor valida movimientos y actualiza estado]
      |
      v
[Se repite hasta que alguien gana]
      |
      v
[Servidor notifica ganador y fin de partida]
```

---

## Explicación Técnica Detallada

### **admin_gui.py**
- Usa Tkinter para la interfaz.
- Permite elegir IP/puerto y controlar el ciclo de vida del servidor.
- Llama a `LudoServer(host, port)` y a `start_in_thread()` solo cuando el admin lo decide.
- Actualiza en tiempo real la lista de usuarios conectados y autenticados.
- Permite agregar/borrar usuarios y ver estadísticas del servidor.

### **server.py**
- El servidor es multihilo: cada cliente se atiende en un hilo separado.
- El método `accept_clients` acepta conexiones y lanza un hilo por cliente.
- El método `handle_client` procesa los comandos de cada cliente (login, registro, lanzar dado, mover ficha).
- Toda la lógica de reglas de Ludo está centralizada aquí:
  - Validación de movimientos, bloqueos, capturas, casillas seguras, pasillos finales, tres 6 seguidos, etc.
  - El servidor mantiene el estado global del tablero y de los turnos.
  - Envía actualizaciones a todos los clientes tras cada acción.
- El servidor solo inicia el socket cuando el admin lo decide, evitando conflictos de puerto.

### **client.py**
- Usa Tkinter para la interfaz gráfica del jugador.
- Permite login y registro, y muestra el tablero y fichas en tiempo real.
- Solo permite lanzar el dado y mover fichas cuando es el turno del jugador.
- Recibe actualizaciones del servidor y actualiza la GUI automáticamente.
- El cliente es "tonto": toda la lógica de reglas y validación está en el servidor.

### **users.json**
- Archivo JSON que almacena los usuarios registrados de forma persistente.
- Se actualiza automáticamente al registrar o borrar usuarios.

### **Icons/**
- Carpeta con imágenes PNG para el tablero, fichas y dados.
- El cliente y el admin las usan para mostrar la interfaz gráfica.

---

## Consejos y solución de problemas

- **El cliente se queda esperando:**
  - Asegúrate de que el admin haya iniciado el servidor y que la IP/puerto coincidan.
  - Verifica que el firewall no bloquee Python.
- **No se ven imágenes:**
  - Verifica que la carpeta `Icons` esté en el mismo directorio y contenga todos los archivos.
- **Puerto ocupado:**
  - Cambia el puerto en la GUI del admin y en los clientes.

---

## Créditos

Desarrollado como proyecto de redes y programación en Python. Arquitectura y reglas adaptadas para cumplir con los requisitos académicos y de juego profesional.
