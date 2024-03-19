import random
import pygame
import cv2
import numpy as np
import mediapipe as mp
import sys

# Inicialización de Pygame
pygame.init()

# Configuración de la pantalla del juego
WIDTH = 1000
HEIGHT = 600
screen = pygame.display.set_mode([WIDTH, HEIGHT])
surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption('Jetpack Joyride Remake in Python!')
fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 32)
bg_color = (128, 128, 128)
lines = [0, WIDTH // 4, 2 * WIDTH // 4, 3 * WIDTH // 4]
game_speed = 3
init_y = HEIGHT - 130
player_y = init_y
booster = False
y_velocity = 0
gravity = 0.4
new_laser = True
laser = []
distance = 0
restart_cmd = False
new_bg = 0
pause = False

# Rocket variables
rocket_counter = 0
rocket_active = False
rocket_delay = 0
rocket_coords = []

# Load player info at the beginning
try:
    file = open('player_info.txt', 'r')
    read = file.readlines()
    high_score = int(read[0])
    lifetime = int(read[1])
    file.close()
except FileNotFoundError:
    high_score = 0
    lifetime = 0

# Initialize the camera
cap = cv2.VideoCapture(0)

# Initialize MediaPipe hands detection
mp_hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

# Function to detect hand gesture
def detect_hand(frame):
    # Convertir la imagen a RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Procesar el frame con el modelo de detección de manos
    results = mp_hands.process(frame_rgb)

    # If hands are detected, determine if hand is open or closed
    if results.multi_hand_landmarks:
        landmarks = results.multi_hand_landmarks[0].landmark
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        little_tip = landmarks[20]
        
        # Calculate distance between thumb and other fingers
        thumb_to_index = np.linalg.norm(np.array([thumb_tip.x, thumb_tip.y]) - np.array([index_tip.x, index_tip.y]))
        thumb_to_middle = np.linalg.norm(np.array([thumb_tip.x, thumb_tip.y]) - np.array([middle_tip.x, middle_tip.y]))
        thumb_to_ring = np.linalg.norm(np.array([thumb_tip.x, thumb_tip.y]) - np.array([ring_tip.x, ring_tip.y]))
        thumb_to_little = np.linalg.norm(np.array([thumb_tip.x, thumb_tip.y]) - np.array([little_tip.x, little_tip.y]))
        
        # Determine hand gesture based on finger distances
        if thumb_to_index > 0.1 and thumb_to_middle > 0.1 and thumb_to_ring > 0.1 and thumb_to_little > 0.1:
            return "open"  # Hand is considered open
        else:
            return "closed"  # Hand is considered closed
    else:
        return "closed"  # If no hands are detected, consider hand closed

# Function to draw the hand landmarks
def draw_hand_landmarks(frame, results):
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            for id, landmark in enumerate(hand_landmarks.landmark):
                height, width, _ = frame.shape
                cx, cy = int(landmark.x * width), int(landmark.y * height)
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

# Function to draw the game screen
def draw_screen(line_list, lase):
    screen.fill('black')
    pygame.draw.rect(surface, (bg_color[0], bg_color[1], bg_color[2], 50), [0, 0, WIDTH, HEIGHT])
    screen.blit(surface, (0, 0))
    top = pygame.draw.rect(screen, 'gray', [0, 0, WIDTH, 50])
    bot = pygame.draw.rect(screen, 'gray', [0, HEIGHT - 50, WIDTH, 50])
    for i in range(len(line_list)):
        pygame.draw.line(screen, 'black', (line_list[i], 0), (line_list[i], 50), 3)
        pygame.draw.line(screen, 'black', (line_list[i], HEIGHT - 50), (line_list[i], HEIGHT), 3)
        line_list[i] -= game_speed
        lase[0][0] -= game_speed
        lase[1][0] -= game_speed
        if line_list[i] < 0:
            line_list[i] = WIDTH
    lase_line = pygame.draw.line(screen, 'yellow', (lase[0][0], lase[0][1]), (lase[1][0], lase[1][1]), 10)
    pygame.draw.circle(screen, 'yellow', (lase[0][0], lase[0][1]), 12)
    pygame.draw.circle(screen, 'yellow', (lase[1][0], lase[1][1]), 12)
    screen.blit(font.render(f'Distance: {int(distance)} m', True, 'white'), (10, 10))
    screen.blit(font.render(f'High Score: {int(high_score)} m', True, 'white'), (10, 70))
    return line_list, top, bot, lase, lase_line

# Function to draw the player
def draw_player():
    play = pygame.rect.Rect((120, player_y + 10), (25, 60))
    if player_y < init_y:
        if booster:
            pygame.draw.ellipse(screen, 'red', [100, player_y + 50, 20, 30])
            pygame.draw.ellipse(screen, 'orange', [105, player_y + 50, 10, 30])
            pygame.draw.ellipse(screen, 'yellow', [110, player_y + 50, 5, 30])
        pygame.draw.rect(screen, 'yellow', [128, player_y + 60, 10, 20], 0, 3)
        pygame.draw.rect(screen, 'orange', [130, player_y + 60, 10, 20], 0, 3)
    else:
        pygame.draw.rect(screen, 'yellow', [128, player_y + 60, 10, 20], 0, 3)
        pygame.draw.rect(screen, 'orange', [130, player_y + 60, 10, 20], 0, 3)
    pygame.draw.rect(screen, 'white', [100, player_y + 20, 20, 30], 0, 5)
    pygame.draw.ellipse(screen, 'orange', [120, player_y + 20, 30, 50])
    pygame.draw.circle(screen, 'orange', (135, player_y + 15), 10)
    pygame.draw.circle(screen, 'black', (138, player_y + 12), 3)
    return play

# Function to check collisions
def check_colliding():
    coll = [False, False]
    rstrt = False
    if player.colliderect(bot_plat):
        coll[0] = True
    elif player.colliderect(top_plat):
        coll[1] = True
    if laser_line.colliderect(player):
        rstrt = True
    if rocket_active:
        if rocket.colliderect(player):
            rstrt = True
    return coll, rstrt

# Function to generate laser obstacles
def generate_laser():
    laser_type = random.randint(0, 1)
    offset = random.randint(10, 300)
    if laser_type == 0:
        laser_width = random.randint(100, 300)
        laser_y = random.randint(100, HEIGHT - 100)
        new_lase = [[WIDTH + offset, laser_y], [WIDTH + offset + laser_width, laser_y]]
    else:
        laser_height = random.randint(100, 300)
        laser_y = random.randint(100, HEIGHT - 400)
        new_lase = [[WIDTH + offset, laser_y], [WIDTH + offset, laser_y + laser_height]]
    return new_lase

# Function to draw rockets
def draw_rocket(coords, mode):
    if mode == 0:
        rock = pygame.draw.rect(screen, 'dark red', [coords[0] - 60, coords[1] - 25, 50, 50], 0, 5)
        screen.blit(font.render('!', True, 'black'), (coords[0] - 40, coords[1] - 20))
        if not pause:
            if coords[1] > player_y + 10:
                coords[1] -= 3
            else:
                coords[1] += 3
    else:
        rock = pygame.draw.rect(screen, 'red', [coords[0], coords[1] - 10, 50, 20], 0, 5)
        pygame.draw.ellipse(screen, 'orange', [coords[0] + 50, coords[1] - 10, 50, 20], 7)
        if not pause:
            coords[0] -= 10 + game_speed

    return coords, rock

# Function to draw the pause screen
def draw_pause():
    pygame.draw.rect(surface, (128, 128, 128, 150), [0, 0, WIDTH, HEIGHT])
    pygame.draw.rect(surface, 'dark gray', [200, 150, 600, 50], 0, 10)
    surface.blit(font.render('Game Paused', True, 'black'), (380, 160))
    restart_btn = pygame.draw.rect(surface, 'white', [200, 220, 280, 50], 0, 10)
    surface.blit(font.render('Restart', True, 'black'), (220, 230))
    quit_btn = pygame.draw.rect(surface, 'white', [520, 220, 280, 50], 0, 10)
    surface.blit(font.render('Quit', True, 'black'), (540, 230))
    #pygame.draw.rect(surface, 'dark gray', [200, 300, 600, 50], 0, 10)
    #surface.blit(font.render(f'Lifetime Distance Ran: {int(lifetime)}', True, 'black'), (220, 310))
    screen.blit(surface, (0, 0))
    return restart_btn, quit_btn

# Function to modify player info
def modify_player_info():
    global high_score, lifetime
    if distance > high_score:
        high_score = distance
    lifetime += distance
    file = open('player_info.txt', 'w')
    file.write(str(int(high_score)) + '\n')
    file.write(str(int(lifetime)))
    file.close()
    

        

# Main game loop            
run = True
while run:
    timer.tick(fps)
    if new_laser:
        laser = generate_laser()
        new_laser = False
    lines, top_plat, bot_plat, laser, laser_line = draw_screen(lines, laser)
    
    if pause:
        restart, quits = draw_pause()
    
    
    if not rocket_active and not pause:
        rocket_counter += 1
    if rocket_counter > 180:
        rocket_counter = 0
        rocket_active = True
        rocket_delay = 0
        rocket_coords = [WIDTH, HEIGHT/2]
    if rocket_active:
        if rocket_delay < 90:
            if not pause:
                rocket_delay += 1
            rocket_coords, rocket = draw_rocket(rocket_coords, 0)
        else:
            rocket_coords, rocket = draw_rocket(rocket_coords, 1)
        if rocket_coords[0] < -50:
            rocket_active = False
    
    
    

    # Capture frame from webcam
    ret, frame = cap.read()
    
    if ret:
        # Detect hand gesture
        hand_gesture = detect_hand(frame)
        
        # Adjust game based on hand gesture
        if hand_gesture == "open":
            booster = True
        else:
            booster = False

        # Draw hand landmarks on frame
        draw_hand_landmarks(frame, mp_hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))

        # Show the frame with hand landmarks
        cv2.imshow('Hand Landmarks', frame)

    player = draw_player()
    colliding, restart_cmd = check_colliding()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            modify_player_info()
            run = False
            
            #---------------------CORRECCIÓN-------------------
            cv2.waitKey(1) 
            cv2.destroyAllWindows() 
            #---------------------CORRECCIÓN-------------------
            
        if event.type == pygame.KEYDOWN:
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
                
        if event.type == pygame.MOUSEBUTTONDOWN and pause:
            if restart.collidepoint(event.pos):
                restart_cmd = True
            if quits.collidepoint(event.pos):
                modify_player_info()
                run = False

                

    if not pause:
        distance += game_speed
        if booster:
            y_velocity -= gravity+1
        else:
            y_velocity += gravity+3
        if (colliding[0] and y_velocity > 0) or (colliding[1] and y_velocity < 0):
            y_velocity = 0
        player_y += y_velocity

    # Progressive speed increases
    if distance < 50000:
        game_speed = 5 + (distance // 500) / 10
    else:
        game_speed = 5

    if laser[0][0] < 0 and laser[1][0] < 0:
        new_laser = True

    if distance - new_bg > 500:
        new_bg = distance
        bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

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

    if distance > high_score:
        high_score = int(distance)

    pygame.display.flip()

# Liberar recursos
cap.release()
pygame.quit()

