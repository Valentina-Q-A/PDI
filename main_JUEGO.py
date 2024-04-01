#------------------------------------------------------------------------------
#---- PLANTILLA DE CÓDIGO -----------------------------------------------------
#---- Primer trabajo de PDI ---------------------------------------------------
#---- Por: Camilo Andrés Anacona Anacona  camilo.anacona@udea.edu.co ----------
#----      CC 1061822363                                                -------
#----      Maria Valentina Quiroga Alzate valentina.quiroga1@udea.edu.co ------
#----      CC 1000214456                                               --------
#----      Estudiantes de Ingeniería Electrónica  -----------------------------
#---- Materia: Procesamiento Digital de Imágenes ------------------------------
#---- Marzo de 2024 -----------------------------------------------------------
#------------------------------------------------------------------------------


#------------Declaración de librerías necesarias-------------------------------

import random # Importa el módulo random para generar números aleatorios.
import pygame # Importa la biblioteca pygame para crear el juego.
import cv2 # Importa la biblioteca OpenCV para trabajar con la cámara.
import numpy as np # Importa la biblioteca NumPy para operaciones numéricas.
import mediapipe as mp # Importa la biblioteca MediaPipe para detección de mano.

#------------------------------------------------------------------------------
#--1. Inicializo el sistema ---------------------------------------------------
#------------------------------------------------------------------------------


pygame.init() # Inicialización de PygameG

#----------Configuración de la pantalla del juego------------------------------
WIDTH = 1000 # Anchura de la pantalla del juego
HEIGHT = 600 # Altura de la pantalla del juego
screen = pygame.display.set_mode([WIDTH, HEIGHT]) # Crear la pantalla del juego con las dimensiones especificadas
surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # Crear una superficie transparente para realizar dibujos adicionales
pygame.display.set_caption('Jetpack Joyride Remake in Python!') # Establece el título de la ventana del juego
fps = 60 # Establece la cantidad de fotogramas por segundo
timer = pygame.time.Clock() # Inicializar un temporizador para controlar la velocidad
font = pygame.font.Font('freesansbold.ttf', 32)  # Carga una fuente para el texto del juego
bg_color = (128, 128, 128) # Color de fondo del juego
lines = [0, WIDTH // 4, 2 * WIDTH // 4, 3 * WIDTH // 4] # Lista de posiciones de las líneas en la pantalla
game_speed = 3 # Velocidad inicial del juego
init_y = HEIGHT - 130 # Posición inicial en el eje Y del jugador
player_y = init_y # Posición inicial en el eje Y del jugador
booster = False # Variable para controlar si el propulsor está activo o no
y_velocity = 0 # Velocidad inicial en el eje Y del jugador
gravity = 0.4 # Gravedad aplicada al jugador
new_laser = True # Variable para indicar si se debe generar un nuevo obstáculo láser
laser = [] # Lista para almacenar las coordenadas de los obstáculos láser
distance = 0  # Distancia recorrida por el jugador
restart_cmd = False # Variable para indicar si se debe reiniciar el juego
new_bg = 0 # Variable para almacenar la posición de fondo en el eje X
pause = False # Variable para indicar si el juego está en pausa

#----------Variables del cohete------------------------------------------------
rocket_counter = 0 # Contador para controlar la frecuencia de aparición del cohete
rocket_active = False # Variable para indicar si el cohete está activo
rocket_delay = 0 # Contador para controlar el retraso entre la aparición y el movimiento del cohete
rocket_coords = [] # Coordenadas del cohete en la pantalla

#----------Cargar información inicial del jugador------------------------------
try:
    file = open('player_info.txt', 'r') # Abre el archivo de información del jugador en modo lectura
    read = file.readlines() # Lee todas las líneas del archivo
    # Extraer el puntaje más alto y la cantidad de tiempo de vida desde las líneas leídas
    high_score = int(read[0]) # Convertir el puntaje más alto a entero
    lifetime = int(read[1]) # Convertir el tiempo de vida a entero
    file.close() # Cierra el archivo
except FileNotFoundError:
    high_score = 0 # Si el archivo no existe, establece el puntaje más alto en 0
    lifetime = 0 # Si el archivo no existe, establece el tiempo de vida en 0


#------------------------------------------------------------------------------
#--2. Detección de manos mediante MediaPipe -----------------------------------
#------------------------------------------------------------------------------

# Inicializar la cámara
cap = cv2.VideoCapture(0)

# Inicializar la detección de manos de MediaPipe
mp_hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

#----------Función para detectar gestos de mano--------------------------------
def detect_hand(frame):
    # Convertir la imagen a RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #formato BGR (Blue, Green, Red) a formato RGB (Red, Green, Blue) 
    
    # Procesar el frame con el modelo de detección de manos
    results = mp_hands.process(frame_rgb)

    # Si se detectan manos, determinar si la mano está abierta o cerrada
    if results.multi_hand_landmarks:
        
        #Extrae los puntos de referencia (landmarks) de la primera mano detectada. results.multi_hand_landmarks es una lista que contiene todos los puntos de referencia de las manos detectadas en el marco de la cámara.
        #results.multi_hand_landmarks[0] accede a los puntos de referencia de la primera mano detectada.
        landmarks = results.multi_hand_landmarks[0].landmark 
        #Extrae el punto de referencia correspondiente a la punta del pulgar. En la estructura de puntos de referencia de MediaPipe, el pulgar es el punto número 4.
        thumb_tip = landmarks[4]
        #Extrae el punto de referencia correspondiente a la punta del dedo índice. En la estructura de puntos de referencia de MediaPipe, el dedo índice es el punto número 8.
        index_tip = landmarks[8]
        #Extrae el punto de referencia correspondiente a la punta del dedo medio. En la estructura de puntos de referencia de MediaPipe, el dedo medio es el punto número 12.
        middle_tip = landmarks[12]
        #Extrae el punto de referencia correspondiente a la punta del dedo anular. En la estructura de puntos de referencia de MediaPipe, el dedo anular es el punto número 16.
        ring_tip = landmarks[16]
        #Extrae el punto de referencia correspondiente a la punta del dedo meñique. En la estructura de puntos de referencia de MediaPipe, el dedo meñique es el punto número 20.
        little_tip = landmarks[20]
        
        # Calcular la distancia entre el pulgar y los otros dedos
        thumb_to_index = np.linalg.norm(np.array([thumb_tip.x, thumb_tip.y]) - np.array([index_tip.x, index_tip.y]))
        # Calcular la distancia entre la punta del pulgar y la punta del dedo medio
        thumb_to_middle = np.linalg.norm(np.array([thumb_tip.x, thumb_tip.y]) - np.array([middle_tip.x, middle_tip.y]))
        # Calcular la distancia entre la punta del pulgar y la punta del dedo anular
        thumb_to_ring = np.linalg.norm(np.array([thumb_tip.x, thumb_tip.y]) - np.array([ring_tip.x, ring_tip.y]))
        # Calcular la distancia entre la punta del pulgar y la punta del dedo meñique
        thumb_to_little = np.linalg.norm(np.array([thumb_tip.x, thumb_tip.y]) - np.array([little_tip.x, little_tip.y]))
        
        # Determinar el gesto de la mano basado en las distancias de los dedos
        if thumb_to_index > 0.1 and thumb_to_middle > 0.1 and thumb_to_ring > 0.1 and thumb_to_little > 0.1: # verifica si la distancia entre la punta del pulgar y la punta de cada uno de los otros dedos es mayor a 0.1
            return "open"  # Se considera que la mano está abierta
        else:
            return "closed"  # Se considera que la mano está cerrada
    else:
        return "closed"  # Si no se detectan manos, se considera que la mano está cerrada

# Función para dibujar los puntos de referencia de la mano
#draw_hand_landmarks que toma dos argumentos: frame, que es el marco de la cámara en el que se dibujarán los puntos de referencia, y results, que son los resultados de la detección de manos obtenidos mediante MediaPipe.
def draw_hand_landmarks(frame, results):
    if results.multi_hand_landmarks: #Verifica si se detectaron múltiples puntos de referencia de manos en el marco de la cámara.
        for hand_landmarks in results.multi_hand_landmarks: #Itera sobre cada conjunto de puntos de referencia de mano detectados en el marco de la cámara.
            for id, landmark in enumerate(hand_landmarks.landmark):
                height, width, _ = frame.shape #Itera sobre cada punto de referencia individual de la mano.
                #Calcula las coordenadas (cx, cy) del punto de referencia actual en píxeles, convirtiendo las coordenadas normalizadas (valores entre 0 y 1) a píxeles multiplicando por el ancho y la altura del marco de la cámara, respectivamente.
                cx, cy = int(landmark.x * width), int(landmark.y * height)
                #Dibuja un círculo en el marco de la cámara en las coordenadas (cx, cy) con un radio de 5 píxeles. El círculo se rellena con color azul ((255, 0, 0)), que corresponde al formato de color BGR en OpenCV.
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), cv2.FILLED)


#------------------------------------------------------------------------------
#--3. Dibujar la pantalla del juego, crear obstáculos y detectar colisiones----
#------------------------------------------------------------------------------

# Función para dibujar la pantalla del juego
def draw_screen(line_list, lase):
    screen.fill('black')  # Rellena la pantalla con color negro
    pygame.draw.rect(surface, (bg_color[0], bg_color[1], bg_color[2], 50), [0, 0, WIDTH, HEIGHT])# Dibuja un rectángulo semitransparente en la superficie para crear un efecto de gradiente
    screen.blit(surface, (0, 0))# Copia la superficie en la pantalla para aplicar el efecto de gradiente al fondo
    top = pygame.draw.rect(screen, 'gray', [0, 0, WIDTH, 50]) # Dibuja un rectángulo gris en la parte superior de la pantalla para representar la plataforma superior
    bot = pygame.draw.rect(screen, 'gray', [0, HEIGHT - 50, WIDTH, 50]) # Dibuja un rectángulo gris en la parte inferior de la pantalla para representar la plataforma inferior
    for i in range(len(line_list)): # Itera sobre cada posición de las líneas divisorias en la lista line_list
        pygame.draw.line(screen, 'black', (line_list[i], 0), (line_list[i], 50), 3) # Dibuja una línea vertical negra en la parte superior de la pantalla en la posición line_list[i]
        pygame.draw.line(screen, 'black', (line_list[i], HEIGHT - 50), (line_list[i], HEIGHT), 3)  # Dibuja una línea vertical negra en la parte inferior de la pantalla en la posición line_list[i]
        
        # Actualiza la posición horizontal de cada línea y del obstáculo láser
        line_list[i] -= game_speed
        lase[0][0] -= game_speed
        lase[1][0] -= game_speed
        
        # Si una línea llega al borde izquierdo de la pantalla, la vuelve a colocar en el borde derecho
        if line_list[i] < 0:
            line_list[i] = WIDTH
            
    lase_line = pygame.draw.line(screen, 'yellow', (lase[0][0], lase[0][1]), (lase[1][0], lase[1][1]), 10)  # Dibuja una línea amarilla que representa el obstáculo láser en la pantalla
    
    # Dibuja círculos amarillos en los extremos del obstáculo láser para indicar su posición
    pygame.draw.circle(screen, 'yellow', (lase[0][0], lase[0][1]), 12)
    pygame.draw.circle(screen, 'yellow', (lase[1][0], lase[1][1]), 12)
    
    screen.blit(font.render(f'Distance: {int(distance)} m', True, 'white'), (10, 10)) # Muestra la distancia recorrida en la pantalla utilizando la fuente definida anteriormente
    screen.blit(font.render(f'High Score: {int(high_score)} m', True, 'white'), (10, 70)) # Muestra la puntuación más alta en la pantalla utilizando la misma fuente
    return line_list, top, bot, lase, lase_line # Devuelve la lista actualizada de posiciones de las líneas divisorias, los rectángulos que representan las plataformas superior e inferior, las coordenadas del obstáculo láser y la línea del obstáculo láser

# Función para dibujar al jugador
def draw_player():
    play = pygame.rect.Rect((120, player_y + 10), (25, 60)) # Define el rectángulo que representa al jugador en la pantalla
    if player_y < init_y:  # Si el jugador está volando hacia arriba (activó el propulsor)
        if booster: # Si el propulsor está activado, dibuja una llama de colores en la parte trasera del jugador
            pygame.draw.ellipse(screen, 'red', [100, player_y + 50, 20, 30])
            pygame.draw.ellipse(screen, 'orange', [105, player_y + 50, 10, 30])
            pygame.draw.ellipse(screen, 'yellow', [110, player_y + 50, 5, 30])
            
        # Dibuja las piernas del jugador cuando está en vuelo ascendente
        pygame.draw.rect(screen, 'yellow', [128, player_y + 60, 10, 20], 0, 3)
        pygame.draw.rect(screen, 'orange', [130, player_y + 60, 10, 20], 0, 3)
        
    else: # Si el jugador está en caída o en el suelo, dibuja las piernas de manera estándar
        pygame.draw.rect(screen, 'yellow', [128, player_y + 60, 10, 20], 0, 3)
        pygame.draw.rect(screen, 'orange', [130, player_y + 60, 10, 20], 0, 3)
        
    pygame.draw.rect(screen, 'white', [100, player_y + 20, 20, 30], 0, 5)# Dibuja el cuerpo del jugador
    pygame.draw.ellipse(screen, 'orange', [120, player_y + 20, 30, 50]) # Dibuja la cabeza del jugador
    pygame.draw.circle(screen, 'orange', (135, player_y + 15), 10) # Dibuja el ojo del jugador
    pygame.draw.circle(screen, 'black', (138, player_y + 12), 3) # Dibuja la pupila del jugador
    return play # Devuelve el rectángulo que representa al jugador

# Función para verificar colisiones
def check_colliding():
    coll = [False, False]  # Inicializa una lista para registrar las colisiones con las plataformas superior e inferior
    rstrt = False  # Inicializa una variable para indicar si se debe reiniciar el juego debido a una colisión
    # Verifica si hay colisión entre el jugador y la plataforma inferior
    if player.colliderect(bot_plat):
        coll[0] = True
    # Si no hay colisión con la plataforma inferior, verifica si hay colisión con la plataforma superior
    elif player.colliderect(top_plat):
        coll[1] = True
    # Verifica si hay colisión entre el jugador y el láser
    if laser_line.colliderect(player):
        rstrt = True
    # Si hay un cohete activo, verifica si hay colisión entre el jugador y el cohete
    if rocket_active:
        if rocket.colliderect(player):
            rstrt = True
    # Devuelve una lista de colisiones y un indicador para reiniciar el juego
    return coll, rstrt


# Función para generar obstáculos de láser
def generate_laser():
    # Elige aleatoriamente el tipo de láser (horizontal o vertical)
    laser_type = random.randint(0, 1)
    # Genera un valor aleatorio para el desplazamiento horizontal del láser
    offset = random.randint(10, 300)
    # Si el tipo de láser es horizontal
    if laser_type == 0:
        # Genera aleatoriamente el ancho del láser y la posición vertical
        laser_width = random.randint(100, 300)
        laser_y = random.randint(100, HEIGHT - 100)
        # Crea las coordenadas del nuevo láser horizontal
        new_lase = [[WIDTH + offset, laser_y], [WIDTH + offset + laser_width, laser_y]]
    else:  # Si el tipo de láser es vertical
        # Genera aleatoriamente la altura del láser y la posición horizontal
        laser_height = random.randint(100, 300)
        laser_y = random.randint(100, HEIGHT - 400)
        # Crea las coordenadas del nuevo láser vertical
        new_lase = [[WIDTH + offset, laser_y], [WIDTH + offset, laser_y + laser_height]]
    # Devuelve las coordenadas del nuevo láser
    return new_lase

# Función para dibujar cohetes
def draw_rocket(coords, mode):
    # Si el modo es 0, dibuja un cohete vertical ascendente
    if mode == 0:
        # Dibuja el cohete con una cola de llamas y el signo de exclamación
        rock = pygame.draw.rect(screen, 'dark red', [coords[0] - 60, coords[1] - 25, 50, 50], 0, 5)
        screen.blit(font.render('!', True, 'black'), (coords[0] - 40, coords[1] - 20))
        # Mueve el cohete hacia arriba o abajo según la posición del jugador
        if not pause:
            if coords[1] > player_y + 10:
                coords[1] -= 3
            else:
                coords[1] += 3
    else:  # Si el modo es 1, dibuja un cohete horizontal
        # Dibuja el cohete con una cola de fuego y el cuerpo del cohete
        rock = pygame.draw.rect(screen, 'red', [coords[0], coords[1] - 10, 50, 20], 0, 5)
        pygame.draw.ellipse(screen, 'orange', [coords[0] + 50, coords[1] - 10, 50, 20], 7)
        # Mueve el cohete hacia la izquierda con la velocidad del juego
        if not pause:
            coords[0] -= 10 + game_speed

    # Devuelve las nuevas coordenadas del cohete y su representación gráfica
    return coords, rock


# Función para dibujar la pantalla de pausa
def draw_pause():
    # Dibuja un rectángulo semitransparente sobre toda la pantalla
    pygame.draw.rect(surface, (128, 128, 128, 150), [0, 0, WIDTH, HEIGHT])
    # Dibuja un rectángulo oscuro para el panel de pausa
    pygame.draw.rect(surface, 'dark gray', [200, 150, 600, 50], 0, 10)
    # Muestra el mensaje "Juego en Pausa" en el panel de pausa
    surface.blit(font.render('Game Paused', True, 'black'), (380, 160))
    # Crea un botón para reiniciar el juego
    restart_btn = pygame.draw.rect(surface, 'white', [200, 220, 280, 50], 0, 10)
    # Muestra el texto "Reiniciar" en el botón de reiniciar
    surface.blit(font.render('Restart', True, 'black'), (220, 230))
    # Crea un botón para salir del juego
    quit_btn = pygame.draw.rect(surface, 'white', [520, 220, 280, 50], 0, 10)
    # Muestra el texto "Salir" en el botón de salir
    surface.blit(font.render('Quit', True, 'black'), (540, 230))
    # Dibuja la superficie en la pantalla del juego
    screen.blit(surface, (0, 0))
    # Devuelve los botones de reiniciar y salir
    return restart_btn, quit_btn


# Función para modificar la información del jugador
def modify_player_info():
    global high_score, lifetime
    # Actualiza el puntaje más alto si la distancia recorrida es mayor que el puntaje anterior
    if distance > high_score:
        high_score = distance
    # Incrementa el tiempo de vida del jugador
    lifetime += distance
    # Abre el archivo de información del jugador en modo escritura
    file = open('player_info.txt', 'w')
    # Escribe el nuevo puntaje más alto en el archivo
    file.write(str(int(high_score)) + '\n')
    # Escribe el nuevo tiempo de vida en el archivo
    file.write(str(int(lifetime)))
    # Cierra el archivo
    file.close()

    
def mostrar_camara():
    # Crea un objeto VideoCapture para capturar el video de la cámara
    cap = cv2.VideoCapture(0)

    # Verifica si la cámara está abierta
    if not cap.isOpened():
        print("Error: No se puede abrir la cámara.")
        return

#------------------------------------------------------------------------------
#--4.-------------Bucle principal del juego -----------------------------------
#------------------------------------------------------------------------------
            
run = True # Variable de control del bucle principal del juego
while run:
    timer.tick(fps) # Limita la velocidad de fotogramas del juego a fotogramas por segundo
    if new_laser: # Verifica si se debe generar un nuevo obstáculo láser
        laser = generate_laser()  # Genera un nuevo obstáculo láser
        new_laser = False # Marca que ya se generó un nuevo obstáculo láser

    # Dibuja la pantalla del juego y obtiene la posición de los elementos en la pantalla
    lines, top_plat, bot_plat, laser, laser_line = draw_screen(lines, laser)

    # Si el juego está en pausa, dibuja la pantalla de pausa y obtiene los botones de reinicio y salida
    if pause:
        restart, quits = draw_pause()
    
   # Actualiza el contador del cohete si no está activo y el juego no está en pausa 
    if not rocket_active and not pause:
        rocket_counter += 1
    if rocket_counter > 180: # Si el contador del cohete supera el límite, activa el cohete y establece sus parámetros iniciales
        rocket_counter = 0
        rocket_active = True
        rocket_delay = 0
        rocket_coords = [WIDTH, HEIGHT/2]
        
    # Si el cohete está activo, lo mueve y lo dibuja en la pantalla
    if rocket_active:
        if rocket_delay < 90: # Si el retraso del cohete es menor que 90 (para el movimiento inicial ascendente)
            if not pause:
                rocket_delay += 1 # Incrementa el contador de retraso del cohete
            rocket_coords, rocket = draw_rocket(rocket_coords, 0) # Dibuja el cohete en su estado ascendente y actualiza sus coordenadas
        else:
            rocket_coords, rocket = draw_rocket(rocket_coords, 1) # Dibuja el cohete en su estado descendente y actualiza sus coordenadas

        # Si el cohete se sale de la pantalla, lo desactiva
        if rocket_coords[0] < -50:
            rocket_active = False
    
    
    

    # Capturar el marco de la cámara
    ret, frame = cap.read()
    
    if ret:
        # Detectar gesto de mano
        hand_gesture = detect_hand(frame)
        
        # Ajustar el juego basado en el gesto de mano
        if hand_gesture == "open":
            booster = True # Activa el propulsor del jugador cuando se detecta un gesto de mano abierta
        else:
            booster = False # Desactiva el propulsor del jugador cuando se detecta un gesto de mano abierto

        # Dibujar los puntos de referencia de la mano en el marco
        draw_hand_landmarks(frame, mp_hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))

        # Mostrar los puntos de referencia
        cv2.imshow('Hand Landmarks', frame)

    player = draw_player() # Dibuja al jugador en la pantalla y obtiene su rectángulo delimitador
    colliding, restart_cmd = check_colliding() # Verifica si hay colisiones entre el jugador y los obstáculos, y determina si se debe reiniciar el juego o no

    #Control de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            modify_player_info()
            run = False
            
            cv2.waitKey(1)  # Liberar recursos de OpenCV
            cv2.destroyAllWindows() # Cerrar todas las ventanas de OpenCV
            
        if event.type == pygame.KEYDOWN:
            # Verifica si la tecla presionada es la tecla de escape
            if event.key == pygame.K_ESCAPE:
                #pause = not pause  # Toggle pause
                
                if pause:
                    pause = False
                else:
                    pause = True

                
            if event.key == pygame.K_SPACE and not pause:
                booster = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                booster = False
        # Verifica si se ha presionado el botón del ratón y el juego está en pausa        
        if event.type == pygame.MOUSEBUTTONDOWN and pause:
            if restart.collidepoint(event.pos):
                restart_cmd = True # Establece el comando de reinicio como verdadero
            # Verifica si se hizo clic en el botón de salir
            if quits.collidepoint(event.pos):
                modify_player_info() # Modifica la información del jugador
                run = False # Termina el bucle principal del juego

                
    # Actualiza la distancia recorrida si el juego no está en pausa
    if not pause:
        distance += game_speed
        
        # Calcula la velocidad vertical del jugador teniendo en cuenta el propulsor y la gravedad
        if booster:
            y_velocity -= gravity+1
        else:
            y_velocity += gravity+3
        # Verifica si el jugador está colisionando y ajusta la velocidad vertical si es necesario
        if (colliding[0] and y_velocity > 0) or (colliding[1] and y_velocity < 0):
            y_velocity = 0
        player_y += y_velocity # Actualiza la posición vertical del jugador basada en la velocidad vertical

    # Incremento progresivo de la velocidad
    if distance < 50000:
        game_speed = 5 + (distance // 500) / 10
    else:
        game_speed = 5

    # Verifica si ambos extremos del láser están fuera de la pantalla y establece la generación de un nuevo láser
    if laser[0][0] < 0 and laser[1][0] < 0:
        new_laser = True

    # Actualiza el color de fondo y la posición de fondo cuando la distancia recorrida excede los 500
    if distance - new_bg > 500:
        new_bg = distance
        bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # Si se ha activado el reinicio del juego, realiza las acciones necesarias y restablece las variables
    if restart_cmd:
        modify_player_info()
        distance = 0
        rocket_active = False
        rocket_counter = 0
        pause = False
        player_y = init_y
        y_velocity = 0
        restart_cmd = 0
        new_laser = True

    # Actualiza el puntaje más alto si la distancia recorrida supera el puntaje maximo
    if distance > high_score:
        high_score = int(distance)

    pygame.display.flip() # Actualiza la pantalla del juego

# Liberar recursos
cap.release()
pygame.quit()

#------------------------------------------------------------------------------
#---------------------------  FIN DEL PROGRAMA --------------------------------
#------------------------------------------------------------------------------
