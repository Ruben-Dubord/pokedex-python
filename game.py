import pygame
import sys
from PIL import Image, ImageDraw
from pokedex import dico_pokemon, type_colors

# ---------- FONCTIONS UTILITAIRES ----------
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def mix_colors(colors):
    n = len(colors)
    r = sum(c[0] for c in colors) // n
    g = sum(c[1] for c in colors) // n
    b = sum(c[2] for c in colors) // n
    return (r, g, b)

def create_grid_overlay(width, height, spacing=20, alpha=40):
    img = Image.new("RGBA", (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    line_color = (0,0,0,alpha)
    for x in range(0, width, spacing):
        draw.line([(x,0),(x,height)], fill=line_color)
    for y in range(0, height, spacing):
        draw.line([(0,y),(width,y)], fill=line_color)
    return img

def load_gif(path):
    frames = []
    durations = []
    gif = Image.open(path)
    for frame in range(gif.n_frames):
        gif.seek(frame)
        frame_image = gif.convert("RGBA")
        duration = gif.info.get("duration",100)
        pygame_image = pygame.image.fromstring(frame_image.tobytes(), frame_image.size, frame_image.mode)
        frames.append(pygame_image)
        durations.append(duration)
    return frames, durations

# ---------- FONCTIONS TEXTE ----------
def draw_multiline_text(surface, text, font, color, x, y, max_width, line_spacing=5):
    words = text.split(' ')
    line = ''
    line_y = y
    for word in words:
        test_line = line + word + ' '
        line_width, _ = font.size(test_line)
        if line_width > max_width:
            rendered_line = font.render(line, True, color)
            surface.blit(rendered_line, (x, line_y))
            line = word + ' '
            line_y += rendered_line.get_height() + line_spacing
        else:
            line = test_line
    if line:
        rendered_line = font.render(line, True, color)
        surface.blit(rendered_line, (x, line_y))

def draw_text(surface, text, font, color, x, y):
    rendered_text = font.render(text, True, color)
    surface.blit(rendered_text, (x, y))

# ---------- INITIALISATION ----------
pygame.init()
pygame.font.init()

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pokédex Ruben DUBORD BUT3 INF Makémaké")

clock = pygame.time.Clock()
font = pygame.font.Font("fonts/pokemon-dppt.ttf", 28)
small_font = pygame.font.Font("fonts/pokemon-dppt.ttf", 18)

# ---------- DONNÉES POKÉMON ----------
pokemon_id = '001'  # ID actuel
pokemon = dico_pokemon[pokemon_id]

number = pokemon_id
name = pokemon['name']
description = pokemon['description']
types = pokemon['types']
size = pokemon['size']
weight = pokemon['weight']
species = pokemon['species']

# Sprite
frames, durations = load_gif(pokemon['sprite_path'])
current_frame = 0
time_accumulator = 0
sprite_scale = 3
scaled_frames = []
for f in frames:
    scaled_frames.append(pygame.transform.scale(f, (f.get_width()*sprite_scale, f.get_height()*sprite_scale)))
frames = scaled_frames

# Empreinte
footprint_image = pygame.image.load(pokemon['footprint_path']).convert_alpha()
footprint_scale = 3
footprint_image = pygame.transform.scale(
    footprint_image,
    (footprint_image.get_width()*footprint_scale, footprint_image.get_height()*footprint_scale)
)
footprint_rect = footprint_image.get_rect()

# Fond couleur unique
colors = [hex_to_rgb(type_colors[t]) for t in types]
background_color = mix_colors(colors)

# Grillage animé
GRID_WIDTH = WINDOW_WIDTH * 2
grid_pil = create_grid_overlay(GRID_WIDTH, WINDOW_HEIGHT, spacing=25, alpha=35)
grid_surface = pygame.image.fromstring(grid_pil.tobytes(), grid_pil.size, grid_pil.mode)
grid_offset_x = 0
grid_speed = 0.3

# Liste triée des IDs pour navigation
pokemon_ids_sorted = sorted(dico_pokemon.keys())
current_index = pokemon_ids_sorted.index(pokemon_id)

# ... ton code reste inchangé jusqu'à la boucle principale ...

# ---------- BOUCLE PRINCIPALE ----------
running = True
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Navigation avec flèches gauche/droite
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                current_index = (current_index + 1) % len(pokemon_ids_sorted)
            elif event.key == pygame.K_LEFT:
                current_index = (current_index - 1) % len(pokemon_ids_sorted)

            # Mise à jour du Pokémon courant
            pokemon_id = pokemon_ids_sorted[current_index]
            pokemon = dico_pokemon[pokemon_id]
            number = pokemon_id
            name = pokemon['name']
            description = pokemon['description']
            types = pokemon['types']
            size = pokemon['size']
            weight = pokemon['weight']
            species = pokemon['species']

            # Recharger les sprites
            frames, durations = load_gif(pokemon['sprite_path'])
            scaled_frames = []
            for f in frames:
                scaled_frames.append(pygame.transform.scale(f, (f.get_width()*sprite_scale, f.get_height()*sprite_scale)))
            frames = scaled_frames
            current_frame = 0
            time_accumulator = 0

            # Recharger empreinte
            footprint_image = pygame.image.load(pokemon['footprint_path']).convert_alpha()
            footprint_image = pygame.transform.scale(
                footprint_image,
                (footprint_image.get_width()*footprint_scale, footprint_image.get_height()*footprint_scale)
            )
            footprint_rect = footprint_image.get_rect()

            # Mettre à jour la couleur de fond
            colors = [hex_to_rgb(type_colors[t]) for t in types]
            background_color = mix_colors(colors)

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

    # ---- Bande du haut : Pokémon précédent / suivant ----
    previous_next_band_height = 60
    previous_next_band_y = 0
    previous_next_band_x = 0
    previous_next_band_width = WINDOW_WIDTH

    previous_next_band = pygame.Surface((previous_next_band_width, previous_next_band_height), pygame.SRCALPHA)
    previous_next_band.fill((0,0,0,180))
    screen.blit(previous_next_band, (previous_next_band_x, previous_next_band_y))

    # Calcul Pokémon précédent / suivant
    previous_index = (current_index - 1) % len(pokemon_ids_sorted)
    next_index = (current_index + 1) % len(pokemon_ids_sorted)
    prev_pokemon = dico_pokemon[pokemon_ids_sorted[previous_index]]
    next_pokemon = dico_pokemon[pokemon_ids_sorted[next_index]]

    # Texte à gauche (précédent)
    screen.blit(
        font.render(f"•{pokemon_ids_sorted[previous_index]} {prev_pokemon['name']}", True, (255,255,255)),
        (20, previous_next_band_y + 10)
    )

    # Texte à droite (suivant)
    next_text = font.render(f"•{pokemon_ids_sorted[next_index]} {next_pokemon['name']}", True, (255,255,255))
    next_text_rect = next_text.get_rect(topright=(WINDOW_WIDTH - 20, previous_next_band_y + 10))
    screen.blit(next_text, next_text_rect)

    # ---- Bande centrale ----
    info_panel_width = 400 + footprint_image.get_width() + 20
    info_panel_height = max(250, footprint_image.get_height() + 20)
    sprite_width = frames[0].get_width()
    sprite_height = frames[0].get_height()

    band_height = 290
    band_y = (WINDOW_HEIGHT - band_height) // 2
    band_x = 0
    band_width = WINDOW_WIDTH

    band_surface = pygame.Surface((band_width, band_height), pygame.SRCALPHA)
    band_surface.fill((0,0,0,180))
    screen.blit(band_surface, (band_x, band_y))

    # Sprite à gauche
    sprite_x = band_x + 100
    sprite_y = band_y + (band_height - sprite_height)//2
    screen.blit(frames[current_frame], (sprite_x, sprite_y))

    # Panel info + stats + empreinte
    info_panel_x = WINDOW_WIDTH // 2 - 25
    info_panel_y = band_y + 20
    info_panel_surface = pygame.Surface((info_panel_width, info_panel_height), pygame.SRCALPHA)
    info_panel_surface.fill((255,255,255,180))
    screen.blit(info_panel_surface, (info_panel_x, info_panel_y))

    # Nom + numéro
    screen.blit(font.render(f"•{number} {name}", True, (0,0,0)), (info_panel_x + 20, info_panel_y + 20))

    # Types
    type_x = info_panel_x + 20
    type_y = info_panel_y + 70
    for t in types:
        rect_width, rect_height = 80, 30
        pygame.draw.rect(screen, hex_to_rgb(type_colors[t]), (type_x, type_y, rect_width, rect_height), border_radius=5)
        type_text = small_font.render(t.upper(), True, (0,0,0))
        text_rect = type_text.get_rect(center=(type_x + rect_width//2, type_y + rect_height//2))
        screen.blit(type_text, text_rect)
        type_x += rect_width + 10

    # Stats
    stats_x = info_panel_x + 20
    stats_y = info_panel_y + 120
    draw_text(screen, f"Taille: {size} m", font, (0,0,0), stats_x, stats_y)
    draw_text(screen, f"Poids: {weight} kg", font, (0,0,0), stats_x, stats_y + 30)
    draw_text(screen, f"{species}", font, (0,0,0), stats_x, stats_y + 60)

    # Empreinte à droite des stats
    footprint_panel_width = footprint_image.get_width() + 20
    footprint_panel_height = footprint_image.get_height() + 20
    footprint_panel_surface = pygame.Surface((footprint_panel_width, footprint_panel_height), pygame.SRCALPHA)
    footprint_panel_surface.fill((128,128,128,180))
    footprint_panel_x = stats_x + 300
    footprint_panel_y = stats_y
    screen.blit(footprint_panel_surface, (footprint_panel_x, footprint_panel_y))
    footprint_rect.topleft = (footprint_panel_x + 10, footprint_panel_y + 10)
    screen.blit(footprint_image, footprint_rect)

    # Description en bas
    desc_panel_height = 120
    desc_panel = pygame.Surface((WINDOW_WIDTH - 40, desc_panel_height), pygame.SRCALPHA)
    desc_panel.fill((0,0,0,180))
    screen.blit(desc_panel, (20, WINDOW_HEIGHT - desc_panel_height - 20))
    draw_multiline_text(screen, description, font, (255,255,255), 60, WINDOW_HEIGHT - desc_panel_height, max_width=WINDOW_WIDTH-100, line_spacing=5)

    pygame.display.flip()

pygame.quit()
sys.exit()

pygame.quit()
sys.exit()
