import pygame
import sys
from PIL import Image, ImageDraw
from pokedex import dico_pokemon, type_colors

# ---------- UTILITAIRES ----------
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def mix_colors(colors):
    n = len(colors)
    return (sum(c[0] for c in colors)//n, sum(c[1] for c in colors)//n, sum(c[2] for c in colors)//n)

def create_grid_overlay(width, height, spacing=20, alpha=40):
    img = Image.new("RGBA", (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    for x in range(0, width, spacing):
        draw.line([(x,0),(x,height)], fill=(0,0,0,alpha))
    for y in range(0, height, spacing):
        draw.line([(0,y),(width,y)], fill=(0,0,0,alpha))
    return img

def load_gif(path):
    frames, durations = [], []
    gif = Image.open(path)
    for frame in range(gif.n_frames):
        gif.seek(frame)
        img = gif.convert("RGBA")
        frames.append(pygame.image.fromstring(img.tobytes(), img.size, img.mode))
        durations.append(gif.info.get("duration", 100))
    return frames, durations

def draw_multiline_text(surface, text, font, color, x, y, max_width, line_spacing=5):
    words = text.split(' ')
    line, line_y = '', y
    for word in words:
        test_line = line + word + ' '
        if font.size(test_line)[0] > max_width:
            surface.blit(font.render(line, True, color), (x, line_y))
            line = word + ' '
            line_y += font.size(line)[1] + line_spacing
        else:
            line = test_line
    if line:
        surface.blit(font.render(line, True, color), (x, line_y))

def draw_text(surface, text, font, color, x, y):
    surface.blit(font.render(text, True, color), (x, y))

# ---------- INITIALISATION ----------
pygame.init()
pygame.font.init()
pygame.mixer.init()

WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pokédex")

clock = pygame.time.Clock()
font = pygame.font.Font("fonts/pokemon-dppt.ttf", 28)
small_font = pygame.font.Font("fonts/pokemon-dppt.ttf", 18)

# Musique de fond
pygame.mixer.music.load("sounds/bgm/dreamyard.wav")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

# ---------- DONNÉES POKÉMON ----------
pokemon_ids_sorted = sorted(dico_pokemon.keys())
current_index = 0

def load_pokemon(pokemon_id):
    p = dico_pokemon[pokemon_id]
    # Sprite
    frames, durations = load_gif(p['sprite_path'])
    scaled_frames = [pygame.transform.scale(f, (f.get_width()*3, f.get_height()*3)) for f in frames]
    # Empreinte
    footprint = pygame.image.load(p['footprint_path']).convert_alpha()
    footprint = pygame.transform.scale(footprint, (footprint.get_width()*3, footprint.get_height()*3))
    # Couleur de fond
    colors = [hex_to_rgb(type_colors[t]) for t in p['types']]
    bg_color = mix_colors(colors)
    return {**p, 'frames': scaled_frames, 'durations': durations, 'footprint': footprint, 'bg_color': bg_color}

pokemon = load_pokemon(pokemon_ids_sorted[current_index])
current_frame, time_accumulator = 0, 0

# Cri initial
current_cry = None
if "cry_path" in pokemon:
    try:
        current_cry = pygame.mixer.Sound(pokemon["cry_path"])
        current_cry.set_volume(0.2)
        current_cry.play()
    except:
        pass

# Grillage
GRID_WIDTH = WINDOW_WIDTH*2
grid_surface = pygame.image.fromstring(create_grid_overlay(GRID_WIDTH, WINDOW_HEIGHT, 25, 35).tobytes(),
                                       (GRID_WIDTH, WINDOW_HEIGHT), "RGBA")
grid_offset_x, grid_speed = 0, 0.3

# ---------- BOUCLE PRINCIPALE ----------
running = True
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            previous_index = current_index
            if event.key == pygame.K_RIGHT:
                current_index = (current_index + 1) % len(pokemon_ids_sorted)
            elif event.key == pygame.K_LEFT:
                current_index = (current_index - 1) % len(pokemon_ids_sorted)

            # Si le Pokémon a changé, mettre à jour
            if current_index != previous_index:
                # Changer de Pokémon
                pokemon_id = pokemon_ids_sorted[current_index]
                pokemon = load_pokemon(pokemon_id)
                current_frame = time_accumulator = 0

                # Jouer le cri du Pokémon
                if current_cry:
                    current_cry.stop()
                try:
                    if "cry_path" in pokemon:
                        current_cry = pygame.mixer.Sound(pokemon["cry_path"])
                        current_cry.set_volume(0.2)
                        current_cry.play()
                except:
                    pass

    # Animation GIF
    time_accumulator += dt
    if time_accumulator >= pokemon['durations'][current_frame]:
        time_accumulator = 0
        current_frame = (current_frame + 1) % len(pokemon['frames'])

    # Animation grillage
    grid_offset_x -= grid_speed
    if grid_offset_x <= -WINDOW_WIDTH:
        grid_offset_x = 0

    # ---------- AFFICHAGE ----------
    screen.fill(pokemon['bg_color'])
    screen.blit(grid_surface, (grid_offset_x, 0))
    screen.blit(grid_surface, (grid_offset_x + WINDOW_WIDTH, 0))

    # Bande haut
    band_h = pygame.Surface((WINDOW_WIDTH, 60), pygame.SRCALPHA)
    band_h.fill((0,0,0,180))
    screen.blit(band_h, (0,0))
    prev_p = dico_pokemon[pokemon_ids_sorted[(current_index-1)%len(pokemon_ids_sorted)]]
    next_p = dico_pokemon[pokemon_ids_sorted[(current_index+1)%len(pokemon_ids_sorted)]]
    screen.blit(font.render(f"•{pokemon_ids_sorted[(current_index-1)%len(pokemon_ids_sorted)]} {prev_p['name']}", True, (255,255,255)), (20,10))
    next_text = font.render(f"•{pokemon_ids_sorted[(current_index+1)%len(pokemon_ids_sorted)]} {next_p['name']}", True, (255,255,255))
    screen.blit(next_text, next_text.get_rect(topright=(WINDOW_WIDTH-20,10)))

    # Bande centrale
    band_height = 290
    band_y = (WINDOW_HEIGHT - band_height)//2
    band_surface = pygame.Surface((WINDOW_WIDTH, band_height), pygame.SRCALPHA)
    band_surface.fill((0,0,0,180))
    screen.blit(band_surface, (0, band_y))

    # Sprite
    sprite_x = 100
    sprite_y = band_y + (band_height - pokemon['frames'][0].get_height())//2
    screen.blit(pokemon['frames'][current_frame], (sprite_x, sprite_y))

    # Panel infos
    info_x = WINDOW_WIDTH//2 - 25
    info_y = band_y + 20
    panel_w = 400 + pokemon['footprint'].get_width() + 20
    panel_h = max(250, pokemon['footprint'].get_height() + 20)
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((255,255,255,180))
    screen.blit(panel, (info_x, info_y))

    # Nom + types
    draw_text(screen, f"•{pokemon_ids_sorted[(current_index)%len(pokemon_ids_sorted)]} {pokemon['name']}", font, (0,0,0), info_x+20, info_y+20)
    type_x, type_y = info_x + 20, info_y + 70

    for t in pokemon['types']:
        rect = pygame.Rect(type_x, type_y, 80, 30)

        # Pastille
        pygame.draw.rect(
            screen,
            hex_to_rgb(type_colors[t]),
            rect,
            border_radius=5
        )

        text = t.upper()
        text_surface = small_font.render(text, True, (255, 255, 255))  # texte principal
        text_rect = text_surface.get_rect(center=rect.center)

        # Contour noir
        outline_color = (0, 0, 0)
        outline_offsets = [(-1,0), (1,0), (0,-1), (0,1)]

        for ox, oy in outline_offsets:
            outline_surf = small_font.render(text, True, outline_color)
            outline_rect = outline_surf.get_rect(center=(text_rect.centerx + ox, text_rect.centery + oy))
            screen.blit(outline_surf, outline_rect)

        # Texte principal (par-dessus)
        screen.blit(text_surface, text_rect)

        type_x += 90

    # Stats
    draw_multiline_text(screen, f"Taille: {pokemon['size']} m", font, (0,0,0), info_x+20, info_y+120, 300)
    draw_multiline_text(screen, f"Poids: {pokemon['weight']} kg", font, (0,0,0), info_x+20, info_y+150, 300)
    draw_multiline_text(screen, f"{pokemon['species']}", font, (0,0,0), info_x+20, info_y+180, 300)

    # Empreinte
    footprint_panel = pygame.Surface((pokemon['footprint'].get_width()+20, pokemon['footprint'].get_height()+20), pygame.SRCALPHA)
    footprint_panel.fill((128,128,128,180))
    fpx = info_x + 300
    fpy = info_y + 120
    screen.blit(footprint_panel, (fpx, fpy))
    screen.blit(pokemon['footprint'], (fpx+10, fpy+10))

    # Description
    desc_panel = pygame.Surface((WINDOW_WIDTH-40, 120), pygame.SRCALPHA)
    desc_panel.fill((0,0,0,180))
    screen.blit(desc_panel, (20, WINDOW_HEIGHT-140))
    draw_multiline_text(screen, pokemon['description'], font, (255,255,255), 60, WINDOW_HEIGHT-140, WINDOW_WIDTH-100, 5)

    pygame.display.flip()

pygame.quit()
sys.exit()
