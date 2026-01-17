import pygame
import sys
from PIL import Image, ImageDraw
from pokedex import dico_pokemon, type_colors

# ---------- FONCTIONS COULEURS ----------
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def mix_colors(colors):
    n = len(colors)
    r = sum(c[0] for c in colors) // n
    g = sum(c[1] for c in colors) // n
    b = sum(c[2] for c in colors) // n
    return (r, g, b)

# ---------- GRILLAGE TRANSPARENT ----------
def create_grid_overlay(width, height, spacing=20, alpha=40):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    line_color = (0, 0, 0, alpha)

    for x in range(0, width, spacing):
        draw.line([(x, 0), (x, height)], fill=line_color)
    for y in range(0, height, spacing):
        draw.line([(0, y), (width, y)], fill=line_color)
    return img

# ---------- CHARGEMENT GIF ----------
def load_gif(path):
    frames = []
    durations = []

    gif = Image.open(path)
    for frame in range(gif.n_frames):
        gif.seek(frame)
        frame_image = gif.convert("RGBA")
        duration = gif.info.get("duration", 100)
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
pygame.font.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pokédex animé")

clock = pygame.time.Clock()

# ---------- POLICE ----------
font = pygame.font.Font("fonts/pokemon-b-w.ttf", 24)

# ---------- DONNÉES POKÉMON ----------
pokemon = dico_pokemon['001']
description = pokemon['description'].upper()
types = pokemon['types']

# ---------- COULEUR UNIQUE ----------
colors = [hex_to_rgb(type_colors[t]) for t in types]
background_color = mix_colors(colors)

# ---------- GRILLAGE ----------
GRID_WIDTH = WINDOW_WIDTH * 2
grid_pil = create_grid_overlay(GRID_WIDTH, WINDOW_HEIGHT, spacing=25, alpha=35)
grid_surface = pygame.image.fromstring(grid_pil.tobytes(), grid_pil.size, grid_pil.mode)
grid_offset_x = 0
grid_speed = 0.3

# ---------- SPRITE ----------
frames, durations = load_gif("./images/001.gif")
current_frame = 0
time_accumulator = 0
rect = frames[0].get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))

# ---------- TEXTE ----------
def draw_text(surface, text, font, color, x, y):
    surface.blit(font.render(text, True, color), (x, y))

# ---------- BOUCLE PRINCIPALE ----------
running = True
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Animation GIF
    time_accumulator += dt
    if time_accumulator >= durations[current_frame]:
        time_accumulator = 0
        current_frame = (current_frame + 1) % len(frames)

    # Animation grillage
    grid_offset_x -= grid_speed
    if grid_offset_x <= -WINDOW_WIDTH:
        grid_offset_x = 0

    # ---------- AFFICHAGE ----------
    screen.fill(background_color)
    screen.blit(grid_surface, (grid_offset_x, 0))
    screen.blit(grid_surface, (grid_offset_x + WINDOW_WIDTH, 0))
    screen.blit(frames[current_frame], rect)
    draw_text(screen, description, font, (0,0,0), 40, 40)

    pygame.display.flip()

pygame.quit()
sys.exit()
