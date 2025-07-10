import pygame
import os
import asyncio
import platform
from pygame import Surface, draw, transform, font, gfxdraw # Import gfxdraw for antialiasing
import math

# Initialize Pygame
pygame.init()

# Constants
ICON_SIZE = 64 # Increased size for better detail
BUTTON_ICON_SIZE = 32 # Size for buttons in the Tkinter app
ICONS_DIR = "icons"

# --- Enhanced Color Palette for Realism and 3D Effect ---
COLORS = {
    "bg_transparent": (0, 0, 0, 0), # Fully transparent background
    "shadow_light": (0, 0, 0, 60), # Light shadow for subtle depth
    "shadow_medium": (0, 0, 0, 100), # Medium shadow
    "shadow_dark": (0, 0, 0, 150), # Darker shadow for more pronounced 3D
    
    "metallic_light": (220, 220, 220),
    "metallic_mid": (150, 150, 150),
    "metallic_dark": (80, 80, 80),

    "wood_light": (180, 100, 60),
    "wood_dark": (100, 40, 0),

    "rubber_light": (255, 120, 120),
    "rubber_dark": (180, 0, 0),

    "plastic_blue_light": (100, 150, 255),
    "plastic_blue_dark": (50, 80, 200),

    "green_light": (80, 220, 170),
    "green_dark": (10, 100, 70),

    "yellow_light": (255, 255, 100),
    "yellow_dark": (200, 180, 0),

    "white_gloss": (255, 255, 255, 180), # Semi-transparent white for highlights
    "black_detail": (30, 30, 30),
}

# Ensure icons folder exists
os.makedirs(ICONS_DIR, exist_ok=True)

# --- Helper Functions for Drawing Enhanced Graphics ---

def draw_linear_gradient(surface, rect, start_color, end_color, orientation='vertical'):
    """Draws a linear gradient on a given surface within a rectangle."""
    if rect.width <= 0 or rect.height <= 0:
        return
    
    temp_surf = Surface((rect.width, rect.height), pygame.SRCALPHA)
    start_rgb = pygame.Color(*start_color[:3])
    end_rgb = pygame.Color(*end_color[:3])
    
    if orientation == 'vertical':
        for y in range(rect.height):
            t = y / rect.height
            r = int(start_rgb.r * (1 - t) + end_rgb.r * t)
            g = int(start_rgb.g * (1 - t) + end_rgb.g * t)
            b = int(start_rgb.b * (1 - t) + end_rgb.b * t)
            draw.line(temp_surf, (r, g, b), (0, y), (rect.width, y))
    elif orientation == 'horizontal':
        for x in range(rect.width):
            t = x / rect.width
            r = int(start_rgb.r * (1 - t) + end_rgb.r * t)
            g = int(start_rgb.g * (1 - t) + end_rgb.g * t)
            b = int(start_color[2] * (1 - t) + end_rgb.b * t)
            draw.line(temp_surf, (r, g, b), (x, 0), (x, rect.height))
            
    surface.blit(temp_surf, rect.topleft)

def draw_radial_gradient(surface, center, radius, start_color, end_color):
    """Draws a radial gradient on a given surface."""
    if radius <= 0:
        return
    
    temp_surf = Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    temp_rect = temp_surf.get_rect(center=(radius, radius))
    
    start_rgb = pygame.Color(*start_color[:3])
    end_rgb = pygame.Color(*end_color[:3])

    for x in range(temp_rect.width):
        for y in range(temp_rect.height):
            dist = math.sqrt((x - radius)**2 + (y - radius)**2)
            if dist <= radius:
                t = dist / radius
                r = int(start_rgb.r * (1 - t) + end_rgb.r * t)
                g = int(start_rgb.g * (1 - t) + end_rgb.g * t)
                b = int(start_rgb.b * (1 - t) + end_rgb.b * t)
                temp_surf.set_at((x, y), (r, g, b))
    
    surface.blit(temp_surf, (center[0] - radius, center[1] - radius))


def draw_shadow_effect(surface, shape_surface, offset=(3, 3), blur_radius=5, shadow_color=COLORS["shadow_medium"]):
    """
    Draws a realistic drop shadow for a given shape.
    shape_surface: A surface containing the shape to cast a shadow (non-transparent parts).
    """
    if shape_surface.get_width() <= 0 or shape_surface.get_height() <= 0:
        return

    # Create a shadow surface
    shadow_surf = Surface(shape_surface.get_size(), pygame.SRCALPHA)
    shadow_surf.fill(shadow_color) # Fill with shadow color (including alpha)
    
    # Use the shape's alpha channel as a mask for the shadow
    shadow_surf.blit(shape_surface, (0, 0), None, pygame.BLEND_RGBA_MULT)

    # Blur the shadow surface (simple box blur for Pygame)
    for _ in range(blur_radius):
        shadow_surf = transform.smoothscale(shadow_surf, (shadow_surf.get_width() // 2, shadow_surf.get_height() // 2))
        shadow_surf = transform.smoothscale(shadow_surf, (shape_surface.get_width(), shape_surface.get_height()))

    # Blit the blurred shadow onto the main surface with offset
    surface.blit(shadow_surf, (offset[0], offset[1]))

def draw_rounded_rect_pygame(surface, color, rect, radius):
    """Draws a filled rounded rectangle on a surface."""
    if rect.width <= 0 or rect.height <= 0:
        return
    
    # Cap radius to prevent drawing issues
    radius = min(radius, rect.width // 2, rect.height // 2)
    
    # Draw main rectangles
    draw.rect(surface, color, (rect.x + radius, rect.y, rect.width - 2 * radius, rect.height))
    draw.rect(surface, color, (rect.x, rect.y + radius, rect.width, rect.height - 2 * radius))
    
    # Draw corner circles (antialiased)
    gfxdraw.aacircle(surface, rect.x + radius, rect.y + radius, radius, color)
    gfxdraw.filled_circle(surface, rect.x + radius, rect.y + radius, radius, color)
    
    gfxdraw.aacircle(surface, rect.x + rect.width - radius, rect.y + radius, radius, color)
    gfxdraw.filled_circle(surface, rect.x + rect.width - radius, rect.y + radius, radius, color)
    
    gfxdraw.aacircle(surface, rect.x + radius, rect.y + rect.height - radius, radius, color)
    gfxdraw.filled_circle(surface, rect.x + radius, rect.y + rect.height - radius, radius, color)
    
    gfxdraw.aacircle(surface, rect.x + rect.width - radius, rect.y + rect.height - radius, radius, color)
    gfxdraw.filled_circle(surface, rect.x + rect.width - radius, rect.y + rect.height - radius, radius, color)

def get_font(size):
    """Attempts to get a suitable font for icons."""
    try:
        return font.SysFont("Arial", size, bold=True)
    except Exception:
        try:
            return font.SysFont(font.get_default_font(), size, bold=True)
        except Exception:
            return font.Font(None, size) # Fallback to default Pygame font

# --- Icon Drawing Functions ---

def create_app_icon():
    surface = Surface((ICON_SIZE, ICON_SIZE), pygame.SRCALPHA)
    
    # Base palette shape with radial gradient
    palette_base_surf = Surface((ICON_SIZE, ICON_SIZE), pygame.SRCALPHA)
    palette_rect = pygame.Rect(ICON_SIZE // 8, ICON_SIZE // 8, ICON_SIZE * 3 // 4, ICON_SIZE * 3 // 4)
    gfxdraw.aacircle(palette_base_surf, palette_rect.centerx, palette_rect.centery, palette_rect.width // 2, COLORS["metallic_mid"])
    gfxdraw.filled_circle(palette_base_surf, palette_rect.centerx, palette_rect.centery, palette_rect.width // 2, COLORS["metallic_mid"])
    draw_radial_gradient(palette_base_surf, palette_rect.center, palette_rect.width // 2, COLORS["metallic_light"], COLORS["metallic_dark"])
    
    draw_shadow_effect(surface, palette_base_surf, offset=(3,3), blur_radius=5, shadow_color=COLORS["shadow_dark"])
    surface.blit(palette_base_surf, (0,0))

    # Color blobs with highlights
    blob_radius = ICON_SIZE // 8
    
    # Red blob
    draw.circle(surface, (255, 60, 60), (ICON_SIZE // 2 - 10, ICON_SIZE // 2 - 10), blob_radius)
    draw.circle(surface, COLORS["white_gloss"], (ICON_SIZE // 2 - 12, ICON_SIZE // 2 - 12), blob_radius // 2)
    
    # Blue blob
    draw.circle(surface, (60, 60, 255), (ICON_SIZE // 2 + 5, ICON_SIZE // 2 - 10), blob_radius)
    draw.circle(surface, COLORS["white_gloss"], (ICON_SIZE // 2 + 7, ICON_SIZE // 2 - 12), blob_radius // 2)

    # Green blob
    draw.circle(surface, (60, 255, 60), (ICON_SIZE // 2 - 5, ICON_SIZE // 2 + 5), blob_radius)
    draw.circle(surface, COLORS["white_gloss"], (ICON_SIZE // 2 - 3, ICON_SIZE // 2 + 7), blob_radius // 2)

    # Brush handle (cylindrical with wood texture)
    handle_width = ICON_SIZE // 8
    handle_height = ICON_SIZE // 2
    handle_rect = pygame.Rect(ICON_SIZE // 2 - handle_width // 2, ICON_SIZE // 2 + 5, handle_width, handle_height)
    
    handle_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    draw_rounded_rect_pygame(handle_surf, COLORS["wood_dark"], handle_rect, handle_width // 4)
    draw_linear_gradient(handle_surf, handle_rect, COLORS["wood_light"], COLORS["wood_dark"])
    
    # Add subtle wood grain lines
    for i in range(5):
        draw.line(handle_surf, COLORS["wood_dark"] + (80,), (handle_rect.x + 2, handle_rect.y + i * (handle_height / 5)),
                  (handle_rect.x + handle_rect.width - 2, handle_rect.y + i * (handle_height / 5) + 3), 1)
    surface.blit(handle_surf, (0,0))

    # Brush bristles (soft and textured)
    bristle_x_offset = handle_width + 5
    bristle_y_start = handle_rect.y + handle_rect.height - 5
    bristle_y_end = ICON_SIZE - ICON_SIZE // 8
    
    bristles_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    draw.polygon(bristles_surf, (255, 255, 255, 200), [(ICON_SIZE // 2 - bristle_x_offset, bristle_y_start),
                                                 (ICON_SIZE // 2 + bristle_x_offset, bristle_y_start),
                                                 (ICON_SIZE // 2, bristle_y_end)])
    bristles_surf.set_alpha(200) # Semi-transparent for softness
    
    # Add individual lines for texture and depth
    for i in range(-7, 8, 2):
        draw.line(bristles_surf, (200, 200, 200), (ICON_SIZE // 2 + i, bristle_y_start), 
                  (ICON_SIZE // 2 + i * 0.7, bristle_y_end - 5), 1)
    
    surface.blit(bristles_surf, (0,0))

    return surface

def create_color_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    # Base disc with radial gradient
    outer_radius = BUTTON_ICON_SIZE // 2 - BUTTON_ICON_SIZE // 8
    disc_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    gfxdraw.aacircle(disc_surf, BUTTON_ICON_SIZE // 2, BUTTON_ICON_SIZE // 2, outer_radius, COLORS["metallic_mid"])
    gfxdraw.filled_circle(disc_surf, BUTTON_ICON_SIZE // 2, BUTTON_ICON_SIZE // 2, outer_radius, COLORS["metallic_mid"])
    draw_radial_gradient(disc_surf, (BUTTON_ICON_SIZE // 2, BUTTON_ICON_SIZE // 2), outer_radius, COLORS["metallic_light"], COLORS["metallic_dark"])
    
    draw_shadow_effect(surface, disc_surf, offset=(1,1), blur_radius=2, shadow_color=COLORS["shadow_light"])
    surface.blit(disc_surf, (0,0))

    # Rainbow arcs
    colors = [(255, 0, 0), (255, 128, 0), (255, 255, 0), (0, 200, 0), (0, 0, 255), (75, 0, 130)]
    arc_width = outer_radius - int(outer_radius * 0.6) # Width of the arc
    
    for i, color in enumerate(colors):
        angle_start = 180 + i * (180 / len(colors))
        angle_end = angle_start + (180 / len(colors))
        
        # We'll draw a thick line along the arc.
        for angle in range(int(angle_start), int(angle_end)):
            rad_angle = math.radians(angle)
            x = BUTTON_ICON_SIZE // 2 + outer_radius * math.cos(rad_angle)
            y = BUTTON_ICON_SIZE // 2 + outer_radius * math.sin(rad_angle)
            draw.circle(surface, color, (int(x), int(y)), arc_width // 2) # Draw small circles along arc

    # Hole in the middle
    inner_radius = int(outer_radius * 0.6)
    gfxdraw.aacircle(surface, BUTTON_ICON_SIZE // 2, BUTTON_ICON_SIZE // 2, inner_radius, (250, 250, 250))
    gfxdraw.filled_circle(surface, BUTTON_ICON_SIZE // 2, BUTTON_ICON_SIZE // 2, inner_radius, (250, 250, 250))
    
    # Inner shadow for the hole
    gfxdraw.aacircle(surface, BUTTON_ICON_SIZE // 2 + 1, BUTTON_ICON_SIZE // 2 + 1, inner_radius - 1, (0, 0, 0, 50))
    gfxdraw.filled_circle(surface, BUTTON_ICON_SIZE // 2 + 1, BUTTON_ICON_SIZE // 2 + 1, inner_radius - 1, (0, 0, 0, 50))

    # Highlight for glossy effect
    gfxdraw.aacircle(surface, int(BUTTON_ICON_SIZE // 2 - outer_radius * 0.4), int(BUTTON_ICON_SIZE // 2 - outer_radius * 0.4), int(outer_radius * 0.3), COLORS["white_gloss"])
    gfxdraw.filled_circle(surface, int(BUTTON_ICON_SIZE // 2 - outer_radius * 0.4), int(BUTTON_ICON_SIZE // 2 - outer_radius * 0.4), int(outer_radius * 0.3), COLORS["white_gloss"])

    return surface

def create_brush_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    # Handle (cylindrical with wood texture)
    handle_width = BUTTON_ICON_SIZE // 5
    handle_height = BUTTON_ICON_SIZE * 0.6
    handle_rect = pygame.Rect(BUTTON_ICON_SIZE // 2 - handle_width // 2, BUTTON_ICON_SIZE // 8, handle_width, handle_height)
    
    handle_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    draw_rounded_rect_pygame(handle_surf, COLORS["wood_dark"], handle_rect, handle_width // 3)
    draw_linear_gradient(handle_surf, handle_rect, COLORS["wood_light"], COLORS["wood_dark"])
    
    # Add subtle wood grain lines
    for i in range(5):
        draw.line(handle_surf, COLORS["wood_dark"] + (80,), (handle_rect.x + 2, handle_rect.y + i * (handle_height / 5)),
                  (handle_rect.x + handle_rect.width - 2, handle_rect.y + i * (handle_height / 5) + 3), 1)
    surface.blit(handle_surf, (0,0))

    # Ferrule (metallic band with reflections)
    ferrule_height = BUTTON_ICON_SIZE // 10
    ferrule_rect = pygame.Rect(handle_rect.x - 2, handle_rect.y + handle_rect.height - ferrule_height // 2, handle_rect.width + 4, ferrule_height)
    
    ferrule_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    draw_rounded_rect_pygame(ferrule_surf, COLORS["metallic_dark"], ferrule_rect, ferrule_height // 2)
    draw_linear_gradient(ferrule_surf, ferrule_rect, COLORS["metallic_light"], COLORS["metallic_dark"])
    
    # Add metallic reflections
    draw.line(ferrule_surf, COLORS["white_gloss"][:3] + (150,), (ferrule_rect.x, ferrule_rect.y + 2), (ferrule_rect.x + ferrule_rect.width, ferrule_rect.y + 2), 1)
    draw.line(ferrule_surf, COLORS["white_gloss"][:3] + (80,), (ferrule_rect.x, ferrule_rect.y + ferrule_rect.height - 2), (ferrule_rect.x + ferrule_rect.width, ferrule_rect.y + ferrule_rect.height - 2), 1)
    surface.blit(ferrule_surf, (0,0))

    # Bristles (soft and textured)
    bristle_x_offset = handle_width + 5
    bristle_y_start = ferrule_rect.y + ferrule_rect.height - 5
    bristle_y_end = BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8
    
    bristles_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    draw.polygon(bristles_surf, (255, 255, 255, 200), [(BUTTON_ICON_SIZE // 2 - bristle_x_offset, bristle_y_start),
                                                 (BUTTON_ICON_SIZE // 2 + bristle_x_offset, bristle_y_start),
                                                 (BUTTON_ICON_SIZE // 2, bristle_y_end)])
    bristles_surf.set_alpha(200) # Semi-transparent for softness
    
    # Add individual lines for texture and depth
    for i in range(-7, 8, 2):
        draw.line(bristles_surf, (200, 200, 200), (BUTTON_ICON_SIZE // 2 + i, bristle_y_start), 
                  (BUTTON_ICON_SIZE // 2 + i * 0.7, bristle_y_end - 5), 1)
    
    surface.blit(bristles_surf, (0,0))
    draw_shadow_effect(surface, handle_surf, offset=(2,2), blur_radius=3, shadow_color=COLORS["shadow_medium"])

    return surface

def create_eraser_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    # Main red body with gradient and subtle texture
    eraser_width = BUTTON_ICON_SIZE - 2 * (BUTTON_ICON_SIZE // 8)
    eraser_height = BUTTON_ICON_SIZE - 2 * (BUTTON_ICON_SIZE // 8)
    eraser_radius = eraser_width // 6
    
    body_rect = pygame.Rect(BUTTON_ICON_SIZE // 8, BUTTON_ICON_SIZE // 2 - eraser_height // 2, eraser_width, eraser_height)
    
    body_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    draw_rounded_rect_pygame(body_surf, COLORS["rubber_dark"], body_rect, eraser_radius)
    draw_linear_gradient(body_surf, body_rect, COLORS["rubber_light"], COLORS["rubber_dark"])
    
    # Add subtle rubber texture lines
    for i in range(3):
        draw.line(body_surf, (0, 0, 0, 30), (body_rect.x + 5, body_rect.y + 5 + i * 8),
                  (body_rect.x + body_rect.width - 5, body_rect.y + 5 + i * 8), 1)
    surface.blit(body_surf, (0,0))

    # Grey tip with gradient and metallic sheen
    tip_width = eraser_width * 0.3
    tip_rect = pygame.Rect(body_rect.x + eraser_width - tip_width, body_rect.y, tip_width, eraser_height)
    
    tip_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    draw_rounded_rect_pygame(tip_surf, COLORS["metallic_dark"], tip_rect, eraser_radius)
    draw_linear_gradient(tip_surf, tip_rect, COLORS["metallic_light"], COLORS["metallic_dark"])
    
    # Add metallic reflections
    draw.line(tip_surf, COLORS["white_gloss"][:3] + (180,), (tip_rect.x + 2, tip_rect.y + 2), (tip_rect.x + tip_rect.width - 2, tip_rect.y + 2), 1)
    draw.line(tip_surf, COLORS["white_gloss"][:3] + (100,), (tip_rect.x + 2, tip_rect.y + tip_rect.height - 2), (tip_rect.x + tip_rect.width - 2, tip_rect.y + tip_rect.height - 2), 1)
    surface.blit(tip_surf, (0,0))

    draw_shadow_effect(surface, body_surf, offset=(2,2), blur_radius=3, shadow_color=COLORS["shadow_medium"])
    return surface

def create_fill_bucket_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    bucket_width = BUTTON_ICON_SIZE // 3
    bucket_height = BUTTON_ICON_SIZE // 2
    
    # Bucket body (metallic look with perspective)
    bucket_points = [
        (BUTTON_ICON_SIZE // 2 - bucket_width, BUTTON_ICON_SIZE // 2 - bucket_height),
        (BUTTON_ICON_SIZE // 2 + bucket_width, BUTTON_ICON_SIZE // 2 - bucket_height),
        (BUTTON_ICON_SIZE // 2 + bucket_width * 0.8, BUTTON_ICON_SIZE // 2 + bucket_height),
        (BUTTON_ICON_SIZE // 2 - bucket_width * 0.8, BUTTON_ICON_SIZE // 2 + bucket_height)
    ]
    
    bucket_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    draw.polygon(bucket_surf, COLORS["metallic_dark"], bucket_points)
    draw_linear_gradient(bucket_surf, bucket_surf.get_rect(), COLORS["metallic_light"], COLORS["metallic_dark"])
    surface.blit(bucket_surf, (0,0))

    # Handle
    gfxdraw.arc(surface, BUTTON_ICON_SIZE // 2 + bucket_width - 5, BUTTON_ICON_SIZE // 2 - bucket_height + 5, 5, 90, 270, COLORS["metallic_dark"])
    gfxdraw.arc(surface, BUTTON_ICON_SIZE // 2 + bucket_width - 5, BUTTON_ICON_SIZE // 2 - bucket_height + 5, 6, 90, 270, COLORS["metallic_light"])

    # Spilling paint (blue)
    paint_points = [
        (BUTTON_ICON_SIZE // 2 + bucket_width * 0.5, BUTTON_ICON_SIZE // 2 - bucket_height + 5),
        (BUTTON_ICON_SIZE // 2 + bucket_width * 0.8, BUTTON_ICON_SIZE // 2 + bucket_height - 5),
        (BUTTON_ICON_SIZE // 2 + bucket_width * 1.2, BUTTON_ICON_SIZE // 2 + bucket_height + 10),
        (BUTTON_ICON_SIZE // 2 + bucket_width * 0.7, BUTTON_ICON_SIZE // 2 + bucket_height + 15),
        (BUTTON_ICON_SIZE // 2 + bucket_width * 0.2, BUTTON_ICON_SIZE // 2 + bucket_height + 10)
    ]
    draw.polygon(surface, COLORS["plastic_blue_light"], paint_points)
    draw_shadow_effect(surface, bucket_surf, offset=(2,2), blur_radius=3, shadow_color=COLORS["shadow_medium"])
    return surface

def create_text_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    # Stylized 'A' for text tool with 3D effect
    text_size = int(BUTTON_ICON_SIZE * 0.6)
    font_obj = get_font(text_size)
    
    # Create text surface for shadow
    text_shadow_surf = font_obj.render("A", True, COLORS["black_detail"][:3] + (150,))
    surface.blit(text_shadow_surf, (BUTTON_ICON_SIZE // 8 + 2, BUTTON_ICON_SIZE // 8 + 2))

    # Create text surface for main text with gradient
    text_main_surf = font_obj.render("A", True, COLORS["black_detail"])
    surface.blit(text_main_surf, (BUTTON_ICON_SIZE // 8, BUTTON_ICON_SIZE // 8))

    draw_shadow_effect(surface, text_main_surf, offset=(1,1), blur_radius=2, shadow_color=COLORS["shadow_light"])
    return surface

def create_line_shape_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    start_point = (BUTTON_ICON_SIZE // 8 + 5, BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8 - 5)
    end_point = (BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8 - 5, BUTTON_ICON_SIZE // 8 + 5)
    
    # Draw line with thickness
    draw.line(surface, COLORS["black_detail"], start_point, end_point, 3)
    
    # Add small circles at ends for 3D effect
    end_radius = 3
    gfxdraw.aacircle(surface, start_point[0], start_point[1], end_radius, COLORS["metallic_mid"])
    gfxdraw.filled_circle(surface, start_point[0], start_point[1], end_radius, COLORS["metallic_mid"])
    
    gfxdraw.aacircle(surface, end_point[0], end_point[1], end_radius, COLORS["metallic_mid"])
    gfxdraw.filled_circle(surface, end_point[0], end_point[1], end_radius, COLORS["metallic_mid"])
    
    draw_shadow_effect(surface, surface, offset=(1,1), blur_radius=2, shadow_color=COLORS["shadow_light"])
    return surface

def create_rectangle_shape_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    rect_x1 = BUTTON_ICON_SIZE // 8
    rect_y1 = BUTTON_ICON_SIZE // 8
    rect_x2 = BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8
    rect_y2 = BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8
    
    # Front face
    draw_rounded_rect_pygame(surface, COLORS["plastic_blue_light"], pygame.Rect(rect_x1, rect_y1, rect_x2 - rect_x1, rect_y2 - rect_y1), 5)
    
    # Top face (simulated perspective)
    top_offset_x = BUTTON_ICON_SIZE // 10
    top_offset_y = BUTTON_ICON_SIZE // 10
    draw.polygon(surface, COLORS["plastic_blue_light"][:3] + (150,), [
        (rect_x1, rect_y1), (rect_x1 + top_offset_x, rect_y1 - top_offset_y),
        (rect_x2 + top_offset_x, rect_y1 - top_offset_y), (rect_x2, rect_y1)
    ])

    # Side face (simulated perspective)
    draw.polygon(surface, COLORS["plastic_blue_dark"], [
        (rect_x2, rect_y1), (rect_x2 + top_offset_x, rect_y1 - top_offset_y),
        (rect_x2 + top_offset_x, rect_y2 - top_offset_y), (rect_x2, rect_y2)
    ])
    
    draw_shadow_effect(surface, surface, offset=(2,2), blur_radius=3, shadow_color=COLORS["shadow_medium"])
    return surface

def create_circle_shape_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    sphere_radius = BUTTON_ICON_SIZE // 2 - BUTTON_ICON_SIZE // 8
    
    # Base sphere with radial gradient
    sphere_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    gfxdraw.aacircle(sphere_surf, BUTTON_ICON_SIZE // 2, BUTTON_ICON_SIZE // 2, sphere_radius, COLORS["plastic_blue_light"])
    gfxdraw.filled_circle(sphere_surf, BUTTON_ICON_SIZE // 2, BUTTON_ICON_SIZE // 2, sphere_radius, COLORS["plastic_blue_light"])
    draw_radial_gradient(sphere_surf, (BUTTON_ICON_SIZE // 2 - sphere_radius // 3, BUTTON_ICON_SIZE // 2 - sphere_radius // 3),
                         int(sphere_radius * 1.5), COLORS["white_gloss"], COLORS["plastic_blue_light"][:3] + (0,)) # Highlight
    
    draw_shadow_effect(surface, sphere_surf, offset=(2,2), blur_radius=3, shadow_color=COLORS["shadow_medium"])
    surface.blit(sphere_surf, (0,0))
    return surface

def create_triangle_shape_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    base_y = BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8
    top_y = BUTTON_ICON_SIZE // 8
    
    # Base triangle
    points = [
        (BUTTON_ICON_SIZE // 2, top_y),
        (BUTTON_ICON_SIZE // 8, base_y),
        (BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8, base_y)
    ]
    draw.polygon(surface, COLORS["plastic_blue_light"], points)
    
    # Add shading for 3D effect
    draw.polygon(surface, COLORS["plastic_blue_dark"], [
        (BUTTON_ICON_SIZE // 2, top_y),
        (BUTTON_ICON_SIZE // 8, base_y),
        (BUTTON_ICON_SIZE // 2, base_y) # Half of base for shading
    ])
    
    draw_shadow_effect(surface, surface, offset=(2,2), blur_radius=3, shadow_color=COLORS["shadow_medium"])
    return surface

def create_star_shape_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    center_x, center_y = BUTTON_ICON_SIZE // 2, BUTTON_ICON_SIZE // 2
    num_points = 5 # A classic 5-point star
    outer_radius = BUTTON_ICON_SIZE // 2 - BUTTON_ICON_SIZE // 8
    inner_radius = outer_radius * 0.4 # Standard star ratio

    points = []
    for i in range(num_points * 2):
        radius = outer_radius if i % 2 == 0 else inner_radius
        angle = math.pi / num_points * i - math.pi / 2 # Start from top
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))
    
    # Draw star with gradient
    star_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    draw.polygon(star_surf, COLORS["yellow_dark"], points)
    draw_radial_gradient(star_surf, (center_x, center_y), outer_radius, COLORS["yellow_light"], COLORS["yellow_dark"])
    surface.blit(star_surf, (0,0))

    # Add highlight for 3D effect
    highlight_points = [
        points[0], # Top point
        points[1], # Next inner point
        points[2], # Next outer point
        points[3] # Next inner point
    ]
    draw.polygon(surface, COLORS["white_gloss"], highlight_points)
    
    draw_shadow_effect(surface, star_surf, offset=(2,2), blur_radius=3, shadow_color=COLORS["shadow_medium"])
    return surface

def create_selection_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    selection_rect = pygame.Rect(BUTTON_ICON_SIZE // 8, BUTTON_ICON_SIZE // 8, 
                                 BUTTON_ICON_SIZE * 3 // 4, BUTTON_ICON_SIZE * 3 // 4)
    
    # Draw a solid base for the selection area
    draw.rect(surface, COLORS["plastic_blue_light"][:3] + (50,), selection_rect) # Light blue transparent fill

    # Draw dotted outline
    dot_length = 3
    gap_length = 3
    line_color = COLORS["black_detail"][:3] + (200,) # Darker, semi-transparent
    
    # Top line
    for x in range(selection_rect.x, selection_rect.x + selection_rect.width, dot_length + gap_length):
        draw.line(surface, line_color, (x, selection_rect.y), (min(x + dot_length, selection_rect.x + selection_rect.width), selection_rect.y), 1)
    # Bottom line
    for x in range(selection_rect.x, selection_rect.x + selection_rect.width, dot_length + gap_length):
        draw.line(surface, line_color, (x, selection_rect.y + selection_rect.height - 1), (min(x + dot_length, selection_rect.x + selection_rect.width), selection_rect.y + selection_rect.height - 1), 1)
    # Left line
    for y in range(selection_rect.y, selection_rect.y + selection_rect.height, dot_length + gap_length):
        draw.line(surface, line_color, (selection_rect.x, y), (selection_rect.x, min(y + dot_length, selection_rect.y + selection_rect.height)), 1)
    # Right line
    for y in range(selection_rect.y, selection_rect.y + selection_rect.height, dot_length + gap_length):
        draw.line(surface, line_color, (selection_rect.x + selection_rect.width - 1, y), (selection_rect.x + selection_rect.width - 1, min(y + dot_length, selection_rect.y + selection_rect.height)), 1)

    draw_shadow_effect(surface, surface, offset=(1,1), blur_radius=2, shadow_color=COLORS["shadow_light"])
    return surface

def create_image_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    # Sky background with gradient
    sky_rect = pygame.Rect(0, 0, BUTTON_ICON_SIZE, BUTTON_ICON_SIZE)
    draw_linear_gradient(surface, sky_rect, (135, 206, 250), (200, 230, 255))

    # Sun
    sun_radius = BUTTON_ICON_SIZE // 8
    draw.circle(surface, COLORS["yellow_light"], (BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8 - sun_radius, BUTTON_ICON_SIZE // 8 + sun_radius), sun_radius)

    # Mountains (layered for depth)
    mountain1_points = [(BUTTON_ICON_SIZE // 8, BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8), 
                        (BUTTON_ICON_SIZE // 2 - 5, BUTTON_ICON_SIZE // 8 + 10), 
                        (BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8 - 10, BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8)]
    draw.polygon(surface, COLORS["metallic_dark"], mountain1_points)
    
    mountain2_points = [(BUTTON_ICON_SIZE // 8 + 15, BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8), 
                        (BUTTON_ICON_SIZE // 2 + 10, BUTTON_ICON_SIZE // 8), 
                        (BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8, BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8)]
    draw.polygon(surface, COLORS["metallic_mid"], mountain2_points)

    # Base line / ground
    draw.line(surface, COLORS["green_dark"], (BUTTON_ICON_SIZE // 8, BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8), 
              (BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8, BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8), 2)
    
    draw_shadow_effect(surface, surface, offset=(2,2), blur_radius=3, shadow_color=COLORS["shadow_medium"])
    return surface

def create_pencil_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    pencil_width = BUTTON_ICON_SIZE // 6
    pencil_height = BUTTON_ICON_SIZE - 2 * (BUTTON_ICON_SIZE // 8)
    
    # Pencil body (yellow, with gradient)
    body_rect = pygame.Rect(BUTTON_ICON_SIZE // 2 - pencil_width // 2, BUTTON_ICON_SIZE // 8, pencil_width, int(pencil_height * 0.8))
    
    body_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    draw_rounded_rect_pygame(body_surf, COLORS["yellow_dark"], body_rect, pencil_width // 4)
    draw_linear_gradient(body_surf, body_rect, COLORS["yellow_light"], COLORS["yellow_dark"])
    surface.blit(body_surf, (0,0))

    # Pencil tip (wood color)
    tip_points = [
        (body_rect.x, body_rect.y + body_rect.height),
        (body_rect.x + body_rect.width, body_rect.y + body_rect.height),
        (BUTTON_ICON_SIZE // 2, BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8)
    ]
    draw.polygon(surface, COLORS["wood_dark"], tip_points)

    # Pencil lead
    draw.polygon(surface, COLORS["black_detail"], [
        (BUTTON_ICON_SIZE // 2 - 2, BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8 - 5), 
        (BUTTON_ICON_SIZE // 2 + 2, BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8 - 5), 
        (BUTTON_ICON_SIZE // 2, BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8)
    ])

    # Eraser at the top
    eraser_height = int(pencil_height * 0.1)
    eraser_rect = pygame.Rect(body_rect.x, BUTTON_ICON_SIZE // 8, pencil_width, eraser_height)
    draw.rect(surface, COLORS["rubber_light"], eraser_rect)
    draw.rect(surface, COLORS["metallic_mid"], (eraser_rect.x, eraser_rect.y, eraser_rect.width, 2)) # Metallic band

    draw_shadow_effect(surface, body_surf, offset=(2,2), blur_radius=3, shadow_color=COLORS["shadow_medium"])
    return surface

def create_pipette_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    # Body of the pipette
    pipette_width = BUTTON_ICON_SIZE // 5
    pipette_height = BUTTON_ICON_SIZE * 0.7
    
    pipette_points = [
        (BUTTON_ICON_SIZE // 2 - pipette_width // 2, BUTTON_ICON_SIZE // 8),
        (BUTTON_ICON_SIZE // 2 + pipette_width // 2, BUTTON_ICON_SIZE // 8),
        (BUTTON_ICON_SIZE // 2 + pipette_width // 4, BUTTON_ICON_SIZE // 8 + pipette_height),
        (BUTTON_ICON_SIZE // 2 - pipette_width // 4, BUTTON_ICON_SIZE // 8 + pipette_height)
    ]
    
    pipette_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    draw.polygon(pipette_surf, COLORS["metallic_dark"], pipette_points)
    draw_linear_gradient(pipette_surf, pipette_surf.get_rect(), COLORS["metallic_light"], COLORS["metallic_dark"])
    surface.blit(pipette_surf, (0,0))

    # Tip
    tip_points = [
        (BUTTON_ICON_SIZE // 2 - pipette_width // 4, BUTTON_ICON_SIZE // 8 + pipette_height),
        (BUTTON_ICON_SIZE // 2 + pipette_width // 4, BUTTON_ICON_SIZE // 8 + pipette_height),
        (BUTTON_ICON_SIZE // 2, BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8)
    ]
    draw.polygon(surface, COLORS["black_detail"], tip_points)

    # Droplet
    draw.circle(surface, COLORS["plastic_blue_light"], (BUTTON_ICON_SIZE // 2, BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8 - 5), 5)
    
    draw_shadow_effect(surface, pipette_surf, offset=(2,2), blur_radius=3, shadow_color=COLORS["shadow_medium"])
    return surface

def create_zoom_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    lens_radius = BUTTON_ICON_SIZE // 4
    handle_length = BUTTON_ICON_SIZE // 3
    
    # Lens (glass effect)
    lens_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    gfxdraw.aacircle(lens_surf, BUTTON_ICON_SIZE // 2, BUTTON_ICON_SIZE // 2, lens_radius, COLORS["metallic_dark"])
    gfxdraw.filled_circle(lens_surf, BUTTON_ICON_SIZE // 2, BUTTON_ICON_SIZE // 2, lens_radius, COLORS["metallic_dark"])
    
    # Inner glass effect
    gfxdraw.aacircle(lens_surf, BUTTON_ICON_SIZE // 2, BUTTON_ICON_SIZE // 2, lens_radius - 2, (200, 200, 255, 100))
    gfxdraw.filled_circle(lens_surf, BUTTON_ICON_SIZE // 2, BUTTON_ICON_SIZE // 2, lens_radius - 2, (200, 200, 255, 100))
    
    # Highlight for glass
    gfxdraw.aacircle(lens_surf, int(BUTTON_ICON_SIZE // 2 - lens_radius * 0.4), int(BUTTON_ICON_SIZE // 2 - lens_radius * 0.4), int(lens_radius * 0.3), COLORS["white_gloss"])
    gfxdraw.filled_circle(lens_surf, int(BUTTON_ICON_SIZE // 2 - lens_radius * 0.4), int(BUTTON_ICON_SIZE // 2 - lens_radius * 0.4), int(lens_radius * 0.3), COLORS["white_gloss"])
    
    draw_shadow_effect(surface, lens_surf, offset=(2,2), blur_radius=3, shadow_color=COLORS["shadow_medium"])
    surface.blit(lens_surf, (0,0))

    # Handle
    handle_start = (int(BUTTON_ICON_SIZE // 2 + lens_radius * 0.7), int(BUTTON_ICON_SIZE // 2 + lens_radius * 0.7))
    handle_end = (int(handle_start[0] + handle_length * 0.7), int(handle_start[1] + handle_length * 0.7))
    draw.line(surface, COLORS["black_detail"], handle_start, handle_end, 3)
    
    return surface

def create_layers_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    layer_width = BUTTON_ICON_SIZE - 2 * (BUTTON_ICON_SIZE // 8)
    layer_height = BUTTON_ICON_SIZE // 4
    layer_offset_x = BUTTON_ICON_SIZE // 12
    layer_offset_y = BUTTON_ICON_SIZE // 12

    # Bottom layer
    bottom_rect = pygame.Rect(BUTTON_ICON_SIZE // 8, BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8 - layer_height, layer_width, layer_height)
    draw.rect(surface, COLORS["metallic_dark"], bottom_rect)
    
    # Middle layer (slightly offset)
    mid_rect = pygame.Rect(bottom_rect.x + layer_offset_x, bottom_rect.y - layer_offset_y, layer_width, layer_height)
    draw.rect(surface, COLORS["plastic_blue_dark"], mid_rect)

    # Top layer (most offset)
    top_rect = pygame.Rect(mid_rect.x + layer_offset_x, mid_rect.y - layer_offset_y, layer_width, layer_height)
    draw.rect(surface, COLORS["yellow_dark"], top_rect)

    # Add subtle highlights and shadows to each layer for depth
    for rect, color_base in [(bottom_rect, COLORS["metallic_mid"]), (mid_rect, COLORS["plastic_blue_light"]), (top_rect, COLORS["yellow_light"])]:
        # Top edge highlight
        draw.line(surface, COLORS["white_gloss"][:3] + (80,), (rect.x + 2, rect.y + 1), (rect.x + rect.width - 2, rect.y + 1), 1)
        # Right edge shadow (for perspective)
        draw.line(surface, COLORS["black_detail"][:3] + (50,), (rect.x + rect.width - 1, rect.y + 2), (rect.x + rect.width - 1, rect.y + rect.height - 2), 1)
    
    draw_shadow_effect(surface, surface, offset=(2,2), blur_radius=4, shadow_color=COLORS["shadow_medium"])
    return surface

def create_save_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    disk_width = BUTTON_ICON_SIZE - 2 * (BUTTON_ICON_SIZE // 8)
    disk_height = BUTTON_ICON_SIZE - 2 * (BUTTON_ICON_SIZE // 8)
    disk_radius = disk_width // 8

    # Main body with green gradient and slight bevel
    body_rect = pygame.Rect(BUTTON_ICON_SIZE // 8, BUTTON_ICON_SIZE // 8, disk_width, disk_height)
    body_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    draw_rounded_rect_pygame(body_surf, COLORS["green_dark"], body_rect, disk_radius)
    draw_linear_gradient(body_surf, body_rect, COLORS["green_light"], COLORS["green_dark"])
    
    # Top-left highlight for glossy effect
    gfxdraw.aacircle(body_surf, body_rect.x + 5, body_rect.y + 5, 5, COLORS["white_gloss"])
    gfxdraw.filled_circle(body_surf, body_rect.x + 5, body_rect.y + 5, 5, COLORS["white_gloss"])
    
    draw_shadow_effect(surface, body_surf, offset=(2,2), blur_radius=4, shadow_color=COLORS["shadow_medium"])
    surface.blit(body_surf, (0,0))

    # Inner white square (more defined, slightly raised)
    inner_padding_val = BUTTON_ICON_SIZE // 8 + disk_width // 4
    inner_square_rect = pygame.Rect(inner_padding_val, inner_padding_val, 
                                    BUTTON_ICON_SIZE - 2 * inner_padding_val, BUTTON_ICON_SIZE - 2 * inner_padding_val)
    
    inner_square_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    draw_rounded_rect_pygame(inner_square_surf, (255, 255, 255), inner_square_rect, disk_radius // 2)
    draw_linear_gradient(inner_square_surf, inner_square_rect, (255, 255, 255), (200, 200, 200))
    surface.blit(inner_square_surf, (0,0))

    # Arrow (more 3D and distinct)
    arrow_x_offset = BUTTON_ICON_SIZE // 10
    arrow_y_offset = BUTTON_ICON_SIZE // 10
    arrow_points = [
        (BUTTON_ICON_SIZE // 2 - arrow_x_offset, BUTTON_ICON_SIZE // 2 + arrow_y_offset),
        (BUTTON_ICON_SIZE // 2 + arrow_x_offset, BUTTON_ICON_SIZE // 2 + arrow_y_offset),
        (BUTTON_ICON_SIZE // 2, BUTTON_ICON_SIZE // 2 + arrow_y_offset + BUTTON_ICON_SIZE // 8)
    ]
    draw.polygon(surface, COLORS["black_detail"], arrow_points)
    
    # Arrow highlight
    draw.line(surface, COLORS["white_gloss"], (arrow_points[0][0] + 2, arrow_points[0][1] + 2),
             (arrow_points[1][0] - 2, arrow_points[1][1] + 2), 1)
    
    return surface

def create_clear_icon():
    surface = Surface((BUTTON_ICON_SIZE, BUTTON_ICON_SIZE), pygame.SRCALPHA)
    
    # Realistic Trash can with metallic look and depth
    body_x_offset = BUTTON_ICON_SIZE // 10
    body_y_top = BUTTON_ICON_SIZE // 8 + 5
    body_y_bottom = BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8
    
    body_points = [
        (BUTTON_ICON_SIZE // 8 + body_x_offset, body_y_top), 
        (BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8 - body_x_offset, body_y_top),
        (BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8, body_y_bottom), 
        (BUTTON_ICON_SIZE // 8, body_y_bottom)
    ]
    
    body_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    draw.polygon(body_surf, COLORS["metallic_dark"], body_points)
    draw_linear_gradient(body_surf, body_surf.get_rect(), COLORS["metallic_light"], COLORS["metallic_dark"])
    
    # Add vertical grooves/lines for metallic texture
    for i in range(5):
        x_pos_top = BUTTON_ICON_SIZE // 8 + body_x_offset + 5 + i * (body_x_offset * 2 // 5)
        x_pos_bottom = BUTTON_ICON_SIZE // 8 + 5 + i * (body_x_offset * 2 // 5) + (body_x_offset * (body_y_bottom - body_y_top) // (BUTTON_ICON_SIZE - BUTTON_ICON_SIZE // 8 - body_y_top))
        draw.line(body_surf, COLORS["metallic_dark"] + (80,), (x_pos_top, body_y_top), (x_pos_bottom, body_y_bottom), 1)
    surface.blit(body_surf, (0,0))

    # Lid (rounded rectangle with darker gradient and highlight)
    lid_height = BUTTON_ICON_SIZE // 8
    lid_rect = pygame.Rect(BUTTON_ICON_SIZE // 8, body_y_top - lid_height, BUTTON_ICON_SIZE - 2 * (BUTTON_ICON_SIZE // 8), lid_height)
    
    lid_surf = Surface(surface.get_size(), pygame.SRCALPHA)
    draw_rounded_rect_pygame(lid_surf, COLORS["metallic_dark"], lid_rect, lid_height // 2)
    draw_linear_gradient(lid_surf, lid_rect, COLORS["metallic_mid"], COLORS["metallic_dark"])
    
    # Lid highlight
    gfxdraw.aacircle(lid_surf, lid_rect.centerx, lid_rect.y + lid_height // 2, lid_height // 2 - 2, COLORS["white_gloss"])
    gfxdraw.filled_circle(lid_surf, lid_rect.centerx, lid_rect.y + lid_height // 2, lid_height // 2 - 2, COLORS["white_gloss"])
    
    surface.blit(lid_surf, (0,0))

    # Lid handle
    draw.line(surface, COLORS["black_detail"], (BUTTON_ICON_SIZE // 2 - 10, lid_rect.y + lid_rect.height // 2), 
             (BUTTON_ICON_SIZE // 2 + 10, lid_rect.y + lid_rect.height // 2), 2)
    draw.circle(surface, COLORS["black_detail"], (BUTTON_ICON_SIZE // 2 - 10, lid_rect.y + lid_rect.height // 2), 2)
    draw.circle(surface, COLORS["black_detail"], (BUTTON_ICON_SIZE // 2 + 10, lid_rect.y + lid_rect.height // 2), 2)
    
    draw_shadow_effect(surface, body_surf, offset=(2,2), blur_radius=4, shadow_color=COLORS["shadow_medium"])
    return surface

def save_icon(surface, name, target_size=None):
    """Save the icon to the icons folder, optionally resizing."""
    if target_size and surface.get_size() != target_size:
        surface = transform.smoothscale(surface, target_size)
    try:
        pygame.image.save(surface, os.path.join(ICONS_DIR, f"{name}.png"))
        print(f"Generated {os.path.join(ICONS_DIR, f'{name}.png')}")
    except Exception as e:
        print(f"Error saving {name}.png: {e}")

async def main():
    icon_functions = {
        "app_icon": create_app_icon,
        "color_icon": create_color_icon,
        "brush_icon": create_brush_icon,
        "eraser_icon": create_eraser_icon,
        "fill_icon": create_fill_bucket_icon, # Renamed from fill_bucket
        "text_icon": create_text_icon,
        "pipette_icon": create_pipette_icon, # Renamed from color_picker
        "zoom_icon": create_zoom_icon, # Renamed from magnifier
        "line_shape_icon": create_line_shape_icon, # Renamed from line
        "rectangle_shape_icon": create_rectangle_shape_icon, # Renamed from rectangle
        "circle_shape_icon": create_circle_shape_icon, # Renamed from circle
        "triangle_shape_icon": create_triangle_shape_icon,
        "star_shape_icon": create_star_shape_icon,
        "selection_icon": create_selection_icon,
        "image_icon": create_image_icon,
        "layers_icon": create_layers_icon,
        "save_icon": create_save_icon, # Added save icon
        "clear_icon": create_clear_icon, # Added clear icon
    }
    
    for name, func in icon_functions.items():
        icon_surface = func()
        # Resize button icons to BUTTON_ICON_SIZE, app_icon to ICON_SIZE
        target_size = ICON_SIZE if name == "app_icon" else BUTTON_ICON_SIZE
        save_icon(icon_surface, name, (target_size, target_size))
        await asyncio.sleep(0.01) # Minimal delay for async compatibility

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
