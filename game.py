import pygame
import sys
from PIL import Image

# ---------- FONCTION POUR CHARGER UN GIF ----------
def load_gif(path):
    frames = []
    durations = []

    gif = Image.open(path)

    for frame in range(gif.n_frames):
        gif.seek(frame)
        frame_image = gif.convert("RGBA")
        duration = gif.info.get("duration", 100)  # ms

        pygame_image = pygame.image.fromstring(
            frame_image.tobytes(),
            frame_image.size,
            frame_image.mode
        )

        frames.append(pygame_image)
        durations.append(duration)

    return frames, durations


# ---------- INITIALISATION ----------
pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("GIF animé avec Pygame")

clock = pygame.time.Clock()

# ---------- CHARGEMENT DU GIF ----------
frames, durations = load_gif("./images/001.gif")

current_frame = 0
time_accumulator = 0

# Centrage
rect = frames[0].get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

# ---------- BOUCLE PRINCIPALE ----------
running = True
while running:
    dt = clock.tick(60)  # temps écoulé en ms

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Gestion animation
    time_accumulator += dt
    if time_accumulator >= durations[current_frame]:
        time_accumulator = 0
        current_frame = (current_frame + 1) % len(frames)

    # Affichage
    screen.fill((30, 30, 30))
    screen.blit(frames[current_frame], rect)
    pygame.display.flip()

# ---------- FERMETURE ----------
pygame.quit()
sys.exit()
