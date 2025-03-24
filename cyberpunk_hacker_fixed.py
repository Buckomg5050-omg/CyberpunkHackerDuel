import pygame
import random
import math
import sys
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize sound mixer

# Screen dimensions (viewport)
VIEWPORT_WIDTH, VIEWPORT_HEIGHT = 800, 600
# World dimensions (entire game world)
WORLD_WIDTH, WORLD_HEIGHT = 1600, 1200

screen = pygame.display.set_mode((VIEWPORT_WIDTH, VIEWPORT_HEIGHT))
pygame.display.set_caption("Cyberpunk Hacker Duel")

# Camera settings
camera_x, camera_y = 0, 0
camera_smoothness = 0.1  # Lower = smoother (0-1)

# Colors
BLACK = (0, 0, 0)
GRID_COLOR = (0, 255, 0)
PLAYER_COLOR = (0, 100, 255)
NODE_COLOR_BRIGHT = (255, 50, 50)
NODE_COLOR_DIM = (150, 10, 10)
FIREWALL_COLOR = (255, 120, 0)  # Orange for firewall
DECOY_COLOR = (100, 150, 255)  # Lighter blue for decoy
COOLDOWN_COLOR = (0, 180, 0)  # Green for cooldown bar
SCANNER_COLOR = (255, 255, 0)  # Yellow for scanner
WALL_COLOR = (180, 0, 255)  # Neon purple for maze walls
STATIC_COLOR = (200, 200, 200)  # White/gray for static effect
SHARD_COLOR = (0, 255, 255)  # Cyan for data shards
SCORE_COLOR = (50, 255, 100)  # Neon green for score
PARTICLE_COLOR = (0, 255, 0)  # Green for ambient particles

# Screen shake settings
screen_shake = False
shake_intensity = 0
shake_duration = 0
shake_timer = 0
max_shake_offset = 5

# Sound settings and loading
sounds_folder = os.path.join(os.path.dirname(__file__), 'sounds')
try:
    ambient_sound = pygame.mixer.Sound(os.path.join(sounds_folder, 'ambient_hum.wav'))
    impact_sound = pygame.mixer.Sound(os.path.join(sounds_folder, 'impact.wav'))
    collect_sound = pygame.mixer.Sound(os.path.join(sounds_folder, 'collect.wav'))
    # Set volumes
    ambient_sound.set_volume(0.3)
    impact_sound.set_volume(0.5)
    collect_sound.set_volume(0.4)
    sound_enabled = True
except:
    print("Warning: Sound files not found or error loading sounds. Running without audio.")
    sound_enabled = False

# Ambient particles
particles = []
max_particles = 150
particle_spawn_rate = 5  # particles per frame

# Player settings
player_size = 30
# Center the player in the world initially
player_x = WORLD_WIDTH // 4 - player_size // 2  # Start in the first quarter of the map
player_y = WORLD_HEIGHT - 200  # Starting position
player_speed = 5
player_start_x = WORLD_WIDTH // 4 - player_size // 2
player_start_y = WORLD_HEIGHT - 200

# Security node settings
node_x = 1400
node_y = 100
node_radius = 20
node_pulse_time = 0
node_pulse_interval = 0.5  # seconds
node_current_color = NODE_COLOR_BRIGHT
node_is_bright = True

# Firewall settings
firewall_width = 10
firewall_height = WORLD_HEIGHT
firewall_x = 0
firewall_speed = 3
firewall_alpha_base = 200
firewall_flicker_intensity = 30
firewall_alert_time = 0
show_alert = False
alert_duration = 2  # seconds

# Decoy settings
decoy_active = False
decoy_x = 0
decoy_y = 0
decoy_duration = 0
decoy_max_duration = 2  # seconds
decoy_cooldown = 0
decoy_max_cooldown = 5  # seconds
decoy_alpha = 200
decoy_can_use = True
decoy_count = 0  # Track how many times decoy has been used
decoy_upgraded = False  # Track if decoy has been upgraded

# Scanner settings
scanner_active = False
scanner_x = 0
scanner_y = 0
scanner_radius = 5
scanner_speed = 6
scanner_trail = []  # Store positions for trail effect
max_trail_length = 15
scanner_flicker_intensity = 40

# Environment settings
ENVIRONMENT_OPEN = 0
ENVIRONMENT_MAZE = 1
current_environment = ENVIRONMENT_OPEN
environment_timer = 0
environment_change_interval = 15  # seconds
environment_transition = False
transition_duration = 0.5  # seconds
transition_timer = 0
walls = []  # List to store wall rectangles
wall_width = 10
wall_height = 50
num_walls = 20
wall_alpha = 0  # For fade-in effect

# Data shard settings
data_shards = []  # List to store active data shards
max_shards = 3  # Maximum number of shards at once
shard_size = 15  # Size of the triangular shards
shard_spawn_timer = 0
shard_spawn_interval = 5  # seconds
shard_glow_intensity = 0
shard_glow_direction = 1
shard_pulse_speed = 0.03
player_score = 0  # Player's score from collecting data shards
showing_upgrade = False
upgrade_timer = 0
upgrade_duration = 2  # seconds

# Grid settings
grid_spacing = 40
grid_alpha_base = 40  # Base transparency
grid_alpha_pulse = 0
grid_pulse_direction = 1
grid_pulse_speed = 0.5
grid_jitter = 3  # Max pixel jitter

# Game state
game_won = False

# Clock for controlling FPS
clock = pygame.time.Clock()
FPS = 60

# Fonts
font = pygame.font.SysFont('Arial', 36)
alert_font = pygame.font.SysFont('Arial', 42)
small_font = pygame.font.SysFont('Arial', 16)
score_font = pygame.font.SysFont('Arial', 24)

# Coordinate conversion functions
def world_to_screen(world_x, world_y):
    """Convert world coordinates to screen coordinates"""
    screen_x = world_x - camera_x
    screen_y = world_y - camera_y
    return screen_x, screen_y

def screen_to_world(screen_x, screen_y):
    """Convert screen coordinates to world coordinates"""
    world_x = screen_x + camera_x
    world_y = screen_y + camera_y
    return world_x, world_y

def update_camera():
    """Update camera position to smoothly follow the player"""
    global camera_x, camera_y
    
    # Calculate target camera position (center on player)
    target_camera_x = player_x - VIEWPORT_WIDTH // 2 + player_size // 2
    target_camera_y = player_y - VIEWPORT_HEIGHT // 2 + player_size // 2
    
    # Clamp camera to world boundaries
    target_camera_x = max(0, min(WORLD_WIDTH - VIEWPORT_WIDTH, target_camera_x))
    target_camera_y = max(0, min(WORLD_HEIGHT - VIEWPORT_HEIGHT, target_camera_y))
    
    # Smoothly interpolate towards target
    camera_x += (target_camera_x - camera_x) * camera_smoothness
    camera_y += (target_camera_y - camera_y) * camera_smoothness

def is_visible_on_screen(world_x, world_y, width, height):
    """Check if an object is visible on screen"""
    screen_x, screen_y = world_to_screen(world_x, world_y)
    return (screen_x + width >= 0 and 
            screen_x <= VIEWPORT_WIDTH and 
            screen_y + height >= 0 and 
            screen_y <= VIEWPORT_HEIGHT)

def update_screen_shake():
    """Update screen shake effect if active"""
    global screen_shake, shake_intensity, shake_timer
    
    if not screen_shake:
        return
        
    # Update timer
    shake_timer += clock.get_time() / 1000
    if shake_timer >= shake_duration:
        screen_shake = False
        shake_timer = 0
        shake_intensity = 0
        return
        
    # Decrease intensity over time for a smoother effect
    progress = shake_timer / shake_duration
    shake_intensity = int(max_shake_offset * (1 - progress))

def trigger_screen_shake(duration=0.3, intensity=5):
    """Trigger a screen shake effect"""
    global screen_shake, shake_duration, shake_timer, shake_intensity
    
    screen_shake = True
    shake_duration = duration
    shake_timer = 0
    shake_intensity = min(intensity, max_shake_offset)

def spawn_particles(count=5):
    """Spawn new ambient particles"""
    for _ in range(count):
        # Spawn particles in visible area around camera
        x = random.randint(int(camera_x), int(camera_x + VIEWPORT_WIDTH))
        y = random.randint(int(camera_y), int(camera_y + VIEWPORT_HEIGHT))
        size = random.uniform(1.0, 3.0)
        lifetime = random.uniform(2.0, 5.0)  # seconds
        fade_speed = random.uniform(0.3, 0.7)
        particles.append({
            'x': x,
            'y': y,
            'size': size,
            'alpha': 0,  # Start invisible and fade in
            'fade_in': True,
            'fade_speed': fade_speed,
            'lifetime': lifetime,
            'age': 0
        })

def update_particles():
    """Update all particles (fade in/out, remove old ones)"""
    global particles
    
    # Spawn new particles
    if len(particles) < max_particles:
        spawn_particles(particle_spawn_rate)
    
    # Update existing particles
    for i in range(len(particles) - 1, -1, -1):
        particle = particles[i]
        
        # Update age
        particle['age'] += clock.get_time() / 1000
        
        # Check if particle should be removed
        if particle['age'] >= particle['lifetime']:
            particles.pop(i)
            continue
            
        # Handle fading
        if particle['fade_in']:
            # Fading in
            particle['alpha'] += particle['fade_speed'] * (clock.get_time() / 1000) * 255
            if particle['alpha'] >= 150:  # Max alpha value
                particle['alpha'] = 150
                particle['fade_in'] = False
        else:
            # Start fading out in the second half of lifetime
            if particle['age'] > particle['lifetime'] / 2:
                particle['alpha'] -= particle['fade_speed'] * (clock.get_time() / 1000) * 255
                particle['alpha'] = max(0, particle['alpha'])

def draw_particles():
    """Draw all particles"""
    particle_surf = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT), pygame.SRCALPHA)
    
    for particle in particles:
        # Calculate current alpha
        alpha = min(255, max(0, int(particle['alpha'])))
        if alpha <= 0:
            continue
        
        # Convert world to screen coordinates
        screen_x, screen_y = world_to_screen(particle['x'], particle['y'])
        
        # Skip particles outside the viewport
        if (screen_x < -10 or screen_x > VIEWPORT_WIDTH + 10 or 
            screen_y < -10 or screen_y > VIEWPORT_HEIGHT + 10):
            continue
            
        # Apply screen shake offset if active
        offset_x, offset_y = 0, 0
        if screen_shake:
            offset_x = random.randint(-shake_intensity, shake_intensity)
            offset_y = random.randint(-shake_intensity, shake_intensity)
            
        # Draw particle with current alpha
        pygame.draw.circle(
            particle_surf, 
            (*PARTICLE_COLOR, alpha), 
            (int(screen_x + offset_x), int(screen_y + offset_y)), 
            particle['size']
        )
        
        # Occasionally draw a small glow
        if random.random() > 0.9:
            glow_size = particle['size'] * 2
            glow_alpha = alpha // 3
            pygame.draw.circle(
                particle_surf,
                (*PARTICLE_COLOR, glow_alpha),
                (int(screen_x + offset_x), int(screen_y + offset_y)),
                glow_size
            )
    
    # Draw all particles at once
    screen.blit(particle_surf, (0, 0))

def generate_maze_walls():
    global walls
    walls = []
    
    # Safe areas - no walls should be generated here
    safe_areas = [
        # Player area
        pygame.Rect(player_x - 150, player_y - 150, player_size + 300, player_size + 300),
        # Node area
        pygame.Rect(node_x - 150, node_y - 150, node_radius * 2 + 300, node_radius * 2 + 300)
    ]
    
    # Number of walls based on world size (scale up from original)
    world_scale_factor = (WORLD_WIDTH * WORLD_HEIGHT) / (800 * 600)
    scaled_num_walls = int(num_walls * world_scale_factor)
    
    # Generate random walls
    attempts = 0
    while len(walls) < scaled_num_walls and attempts < 200:
        attempts += 1
        x = random.randint(50, WORLD_WIDTH - wall_width - 50)
        y = random.randint(50, WORLD_HEIGHT - wall_height - 50)
        
        # Create a rectangle for collision detection
        wall_rect = pygame.Rect(x, y, wall_width, wall_height)
        
        # Check if wall overlaps with safe areas
        overlap = False
        for area in safe_areas:
            if wall_rect.colliderect(area):
                overlap = True
                break
        
        # Check if wall overlaps with other walls
        for other_wall in walls:
            if wall_rect.colliderect(other_wall):
                overlap = True
                break
        
        if not overlap:
            # Randomly rotate some walls to be horizontal
            if random.random() > 0.5:
                walls.append(pygame.Rect(x, y, wall_width, wall_height))
            else:
                walls.append(pygame.Rect(x, y, wall_height, wall_width))

def draw_walls():
    if current_environment != ENVIRONMENT_MAZE:
        return
    
    # Draw the walls with current alpha value
    for wall in walls:
        # Check if wall is visible on screen
        if not is_visible_on_screen(wall.x, wall.y, wall.width, wall.height):
            continue
        
        # Convert world to screen coordinates
        screen_x, screen_y = world_to_screen(wall.x, wall.y)
        
        # Create wall surface with alpha
        wall_surf = pygame.Surface((wall.width, wall.height), pygame.SRCALPHA)
        
        # Draw main wall
        pygame.draw.rect(wall_surf, (*WALL_COLOR, wall_alpha), (0, 0, wall.width, wall.height))
        
        # Add glitch effect occasionally
        if random.random() > 0.95:
            glitch_y = random.randint(0, wall.height - 5)
            glitch_height = random.randint(2, 5)
            glitch_offset = random.randint(-2, 2)
            if glitch_offset != 0 and glitch_y + glitch_height < wall.height:
                section = wall_surf.subsurface((0, glitch_y, wall.width, glitch_height)).copy()
                wall_surf.blit(section, (glitch_offset, glitch_y))
        
        screen.blit(wall_surf, (screen_x, screen_y))

def draw_transition_effect():
    # Create static effect for transition
    static_surface = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT), pygame.SRCALPHA)
    
    # Calculate static intensity based on transition progress
    # Most intense in the middle of the transition
    progress = transition_timer / transition_duration
    intensity = 180 if progress < 0.5 else 180 * (1 - progress) * 2
    
    # Draw random static pixels
    for _ in range(5000):
        x = random.randint(0, VIEWPORT_WIDTH - 1)
        y = random.randint(0, VIEWPORT_HEIGHT - 1)
        size = random.randint(1, 3)
        alpha = random.randint(int(intensity * 0.3), int(intensity))
        color = (STATIC_COLOR[0], STATIC_COLOR[1], STATIC_COLOR[2], alpha)
        pygame.draw.rect(static_surface, color, (x, y, size, size))
    
    screen.blit(static_surface, (0, 0))

def check_wall_collision(new_x, new_y):
    if current_environment != ENVIRONMENT_MAZE:
        return False
    
    # Create player rect at the new position
    player_rect = pygame.Rect(new_x, new_y, player_size, player_size)
    
    # Check collision with any wall
    for wall in walls:
        if player_rect.colliderect(wall):
            return True
    
    return False

def update_environment():
    global environment_timer, current_environment, environment_transition, transition_timer, wall_alpha, walls
    
    # Update main environment timer
    environment_timer += clock.get_time() / 1000
    
    # Check if it's time to change environments
    if environment_timer >= environment_change_interval and not environment_transition:
        environment_transition = True
        transition_timer = 0
        
        # Generate new walls if transitioning to maze
        if current_environment == ENVIRONMENT_OPEN:
            generate_maze_walls()
            wall_alpha = 0  # Start with invisible walls
    
    # Handle transition if active
    if environment_transition:
        transition_timer += clock.get_time() / 1000
        
        # Fade in walls if going to maze environment
        if current_environment == ENVIRONMENT_OPEN:
            wall_alpha = min(200, int(255 * (transition_timer / transition_duration)))
        
        # Complete transition when timer is finished
        if transition_timer >= transition_duration:
            environment_transition = False
            environment_timer = 0
            
            # Toggle environment
            if current_environment == ENVIRONMENT_OPEN:
                current_environment = ENVIRONMENT_MAZE
                wall_alpha = 200  # Full visibility
            else:
                current_environment = ENVIRONMENT_OPEN
                walls = []  # Clear walls

def draw_grid():
    # Pulse effect
    global grid_alpha_pulse, grid_pulse_direction
    grid_alpha_pulse += grid_pulse_speed * grid_pulse_direction
    if grid_alpha_pulse > 30 or grid_alpha_pulse < 0:
        grid_pulse_direction *= -1
    
    current_alpha = min(255, max(10, int(grid_alpha_base + grid_alpha_pulse)))
    
    # Create a surface for the grid
    grid_surface = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT), pygame.SRCALPHA)
    
    # Calculate visible grid area based on camera position
    start_x = max(0, camera_x - (camera_x % grid_spacing))
    end_x = min(WORLD_WIDTH, camera_x + VIEWPORT_WIDTH + grid_spacing)
    start_y = max(0, camera_y - (camera_y % grid_spacing))
    end_y = min(WORLD_HEIGHT, camera_y + VIEWPORT_HEIGHT + grid_spacing)
    
    # Draw vertical lines
    for world_x in range(int(start_x), int(end_x), grid_spacing):
        # Convert to screen coordinates
        screen_x, _ = world_to_screen(world_x, 0)
        
        # Add jitter to x position
        jitter_x = screen_x + random.randint(-grid_jitter, grid_jitter)
        
        # Randomly adjust alpha for flickering effect
        line_alpha = max(10, current_alpha + random.randint(-20, 10))
        color = (*GRID_COLOR, line_alpha)
        
        pygame.draw.line(grid_surface, color, (jitter_x, 0), (jitter_x, VIEWPORT_HEIGHT), 1)
    
    # Draw horizontal lines
    for world_y in range(int(start_y), int(end_y), grid_spacing):
        # Convert to screen coordinates
        _, screen_y = world_to_screen(0, world_y)
        
        # Add jitter to y position
        jitter_y = screen_y + random.randint(-grid_jitter, grid_jitter)
        
        # Randomly adjust alpha for flickering effect
        line_alpha = max(10, current_alpha + random.randint(-20, 10))
        color = (*GRID_COLOR, line_alpha)
        
        pygame.draw.line(grid_surface, color, (0, jitter_y), (VIEWPORT_WIDTH, jitter_y), 1)
    
    screen.blit(grid_surface, (0, 0))

def draw_player():
    # Calculate screen shake offset if active
    offset_x, offset_y = 0, 0
    if screen_shake:
        offset_x = random.randint(-shake_intensity, shake_intensity)
        offset_y = random.randint(-shake_intensity, shake_intensity)
    
    # Convert world to screen coordinates
    screen_x, screen_y = world_to_screen(player_x, player_y)
    
    # Create glow effect layers
    glow_size = player_size + 12
    for i in range(3):
        glow_alpha = 60 - (i * 20)
        glow_size_current = player_size + 4 + (i * 4)
        glow_surf = pygame.Surface((glow_size_current, glow_size_current), pygame.SRCALPHA)
        
        # Draw angular shape glow
        points = [
            (glow_size_current * 0.1, glow_size_current * 0.5),  # Left point
            (glow_size_current * 0.5, glow_size_current * 0.1),  # Top point
            (glow_size_current * 0.9, glow_size_current * 0.5),  # Right point
            (glow_size_current * 0.7, glow_size_current * 0.9),  # Bottom right
            (glow_size_current * 0.3, glow_size_current * 0.9)   # Bottom left
        ]
        
        pygame.draw.polygon(glow_surf, (*PLAYER_COLOR, glow_alpha), points)
        
        # Position and draw with screen shake offset
        pos_x = screen_x - (glow_size_current - player_size) // 2 + offset_x
        pos_y = screen_y - (glow_size_current - player_size) // 2 + offset_y
        screen.blit(glow_surf, (pos_x, pos_y))
    
    # Create main player surface
    player_surf = pygame.Surface((player_size, player_size), pygame.SRCALPHA)
    
    # Draw angular, sleek player shape
    points = [
        (player_size * 0.1, player_size * 0.5),  # Left point
        (player_size * 0.5, player_size * 0.1),  # Top point
        (player_size * 0.9, player_size * 0.5),  # Right point
        (player_size * 0.7, player_size * 0.9),  # Bottom right
        (player_size * 0.3, player_size * 0.9)   # Bottom left
    ]
    
    # Draw main shape
    pygame.draw.polygon(player_surf, PLAYER_COLOR, points)
    
    # Draw highlight on edges - ensure RGB values are valid
    highlight_color = (
        min(255, PLAYER_COLOR[0] + 30),
        min(255, PLAYER_COLOR[1] + 30),
        min(255, PLAYER_COLOR[2] + 30)
    )
    pygame.draw.polygon(player_surf, highlight_color, points, 1)
    
    # Position and draw with screen shake offset
    screen.blit(player_surf, (screen_x + offset_x, screen_y + offset_y))

def draw_security_node():
    global node_pulse_time, node_current_color, node_is_bright
    
    # Check if node is visible on screen first
    if not is_visible_on_screen(node_x - node_radius, node_y - node_radius, node_radius * 2, node_radius * 2):
        return
    
    # Convert world to screen coordinates
    screen_x, screen_y = world_to_screen(node_x, node_y)
    
    # Update pulse timer
    node_pulse_time += clock.get_time() / 1000  # Convert to seconds
    
    # Toggle color based on pulse interval
    if node_pulse_time >= node_pulse_interval:
        node_pulse_time = 0
        node_is_bright = not node_is_bright
        node_current_color = NODE_COLOR_BRIGHT if node_is_bright else NODE_COLOR_DIM
    
    # Draw glow effect (larger semi-transparent circle)
    glow_radius = node_radius * 1.5
    glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
    glow_alpha = 100 if node_is_bright else 50
    pygame.draw.circle(glow_surface, (*node_current_color, glow_alpha), (glow_radius, glow_radius), glow_radius)
    screen.blit(glow_surface, (screen_x - glow_radius, screen_y - glow_radius))
    
    # Draw the node
    pygame.draw.circle(screen, node_current_color, (screen_x, screen_y), node_radius)

def draw_firewall():
    global firewall_x
    
    # Move firewall based on decoy presence
    if decoy_active:
        # Calculate direction toward decoy
        if firewall_x < decoy_x:
            firewall_x += firewall_speed
        elif firewall_x > decoy_x:
            firewall_x -= firewall_speed
    else:
        # Normal movement
        firewall_x += firewall_speed
        
        # Reset if off screen
        if firewall_x > WORLD_WIDTH:
            firewall_x = -firewall_width
    
    # Convert world to screen coordinates
    screen_x, _ = world_to_screen(firewall_x, 0)
    
    # Check if firewall is visible on screen
    if screen_x < -firewall_width or screen_x > VIEWPORT_WIDTH:
        return
    
    # Create firewall surface with flicker effect
    firewall_surf = pygame.Surface((firewall_width, VIEWPORT_HEIGHT), pygame.SRCALPHA)
    
    # Add flickering effect (randomly adjust alpha)
    flicker_alpha = min(255, max(100, firewall_alpha_base + random.randint(-firewall_flicker_intensity, firewall_flicker_intensity)))
    
    # Draw the firewall line with flicker
    firewall_color_with_alpha = (*FIREWALL_COLOR, flicker_alpha)
    pygame.draw.rect(firewall_surf, firewall_color_with_alpha, (0, 0, firewall_width, VIEWPORT_HEIGHT))
    
    # Occasionally add glitch effect (horizontal displacement)
    if random.random() > 0.95:
        glitch_y = random.randint(0, VIEWPORT_HEIGHT - 50)
        glitch_height = random.randint(10, 40)
        glitch_offset = random.randint(-3, 3)
        if glitch_offset != 0:
            section = firewall_surf.subsurface((0, glitch_y, firewall_width, glitch_height)).copy()
            firewall_surf.blit(section, (glitch_offset, glitch_y))
    
    screen.blit(firewall_surf, (screen_x, 0))

def reset_player_position():
    global player_x, player_y, show_alert, firewall_alert_time
    player_x = player_start_x
    player_y = player_start_y
    show_alert = True
    firewall_alert_time = 0
    
    # Trigger intense screen shake
    trigger_screen_shake(0.4, 5)
    
    # Play impact sound
    if sound_enabled:
        try:
            impact_sound.play()
        except:
            pass

def spawn_decoy():
    global decoy_active, decoy_x, decoy_y, decoy_duration, decoy_can_use, decoy_cooldown, decoy_count, scanner_active
    if decoy_can_use:
        decoy_active = True
        decoy_x = player_x
        decoy_y = player_y
        decoy_duration = decoy_max_duration
        decoy_can_use = False
        decoy_cooldown = decoy_max_cooldown
        decoy_count += 1
        
        # If player has used decoy twice or more, spawn a scanner
        if decoy_count >= 2:
            spawn_scanner()

def spawn_scanner():
    global scanner_active, scanner_x, scanner_y, scanner_trail
    
    # Spawn from firewall position
    scanner_active = True
    scanner_x = firewall_x + firewall_width // 2
    scanner_y = random.randint(50, WORLD_HEIGHT - 50)  # Random y position
    scanner_trail = []  # Reset trail

def update_decoy():
    global decoy_active, decoy_duration, decoy_cooldown, decoy_can_use
    
    # Update decoy timer if active
    if decoy_active:
        decoy_duration -= clock.get_time() / 1000
        if decoy_duration <= 0:
            decoy_active = False
    
    # Update cooldown if not ready
    if not decoy_can_use:
        decoy_cooldown -= clock.get_time() / 1000
        if decoy_cooldown <= 0:
            decoy_can_use = True

def update_scanner():
    global scanner_active, scanner_x, scanner_y, decoy_active
    
    if not scanner_active or not decoy_active:
        # Reset scanner if decoy disappears
        if scanner_active and not decoy_active:
            scanner_active = False
        return
    
    # Calculate direction to decoy
    decoy_center_x = decoy_x + player_size // 2
    decoy_center_y = decoy_y + player_size // 2
    
    dx = decoy_center_x - scanner_x
    dy = decoy_center_y - scanner_y
    
    # Normalize direction
    distance = max(0.1, math.sqrt(dx * dx + dy * dy))
    dx /= distance
    dy /= distance
    
    # Move scanner toward decoy
    scanner_x += dx * scanner_speed
    scanner_y += dy * scanner_speed
    
    # Check if scanner reached decoy
    if check_scanner_decoy_collision():
        destroy_decoy()

def destroy_decoy():
    global decoy_active, scanner_active
    decoy_active = False
    scanner_active = False

def check_scanner_decoy_collision():
    if not scanner_active or not decoy_active:
        return False
    
    # Calculate center of decoy
    decoy_center_x = decoy_x + player_size // 2
    decoy_center_y = decoy_y + player_size // 2
    
    # Calculate distance between scanner and decoy center
    distance = math.sqrt((scanner_x - decoy_center_x) ** 2 + (scanner_y - decoy_center_y) ** 2)
    
    # Check if collision occurred
    if distance < (scanner_radius + player_size // 2):
        return True
    return False

def check_node_collision():
    # Calculate the center point of the player
    player_center_x = player_x + player_size // 2
    player_center_y = player_y + player_size // 2
    
    # Calculate distance between player center and node center
    distance = math.sqrt((player_center_x - node_x) ** 2 + (player_center_y - node_y) ** 2)
    
    # Check if the distance is less than the sum of player half-width and node radius
    if distance < (player_size // 2 + node_radius):
        return True
    return False

def check_firewall_collision():
    # Check if player overlaps with firewall
    player_right = player_x + player_size
    firewall_right = firewall_x + firewall_width
    
    # If any part of the player horizontally intersects with the firewall
    if ((firewall_x <= player_x < firewall_right) or 
            (firewall_x < player_right <= firewall_right) or
            (player_x <= firewall_x and player_right >= firewall_right)):
        return True
    return False

def draw_decoy():
    if not decoy_active:
        return
    
    # Check if decoy is visible on screen
    if not is_visible_on_screen(decoy_x, decoy_y, player_size, player_size):
        return
    
    # Convert world to screen coordinates
    screen_x, screen_y = world_to_screen(decoy_x, decoy_y)
    
    # Calculate current alpha based on remaining duration
    fade_factor = decoy_duration / decoy_max_duration
    current_alpha = int(decoy_alpha * fade_factor)
    
    # Create base decoy surface
    decoy_surf = pygame.Surface((player_size, player_size), pygame.SRCALPHA)
    
    # Add static effect
    for _ in range(20):
        static_x = random.randint(0, player_size - 1)
        static_y = random.randint(0, player_size - 1)
        static_width = random.randint(1, 5)
        static_height = random.randint(1, 5)
        static_alpha = random.randint(50, 150)
        static_color = (*DECOY_COLOR, static_alpha)
        
        if static_x + static_width > player_size:
            static_width = player_size - static_x
        if static_y + static_height > player_size:
            static_height = player_size - static_y
            
        if static_width > 0 and static_height > 0:
            pygame.draw.rect(decoy_surf, static_color, (static_x, static_y, static_width, static_height))
    
    # Create the main decoy shape
    base_decoy_alpha = min(200, current_alpha) 
    pygame.draw.rect(decoy_surf, (*DECOY_COLOR, base_decoy_alpha), (0, 0, player_size, player_size), border_radius=3)
    
    # Add glow
    glow_size = player_size + 10
    glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
    glow_alpha = min(50, current_alpha // 2)
    pygame.draw.rect(glow_surf, (*DECOY_COLOR, glow_alpha), (0, 0, glow_size, glow_size), border_radius=5)
    
    # Draw the glow and decoy
    screen.blit(glow_surf, (screen_x - 5, screen_y - 5))
    screen.blit(decoy_surf, (screen_x, screen_y))
    
    # Add occasional glitch displacement effect
    if random.random() > 0.9:
        glitch_offset_x = random.randint(-3, 3)
        glitch_offset_y = random.randint(-3, 3)
        glitch_surf = decoy_surf.copy()
        glitch_alpha = min(100, current_alpha // 2)
        glitch_surf.set_alpha(glitch_alpha)
        screen.blit(glitch_surf, (screen_x + glitch_offset_x, screen_y + glitch_offset_y))

def draw_scanner():
    global scanner_trail, scanner_x, scanner_y
    
    if not scanner_active or not decoy_active:
        return
    
    # Check if scanner is visible on screen
    if not is_visible_on_screen(scanner_x - scanner_radius*2, scanner_y - scanner_radius*2, 
                                scanner_radius*4, scanner_radius*4):
        return
    
    # Convert trail points to screen coordinates
    screen_trail = []
    for trail_x, trail_y in scanner_trail:
        screen_trail_x, screen_trail_y = world_to_screen(trail_x, trail_y)
        screen_trail.append((screen_trail_x, screen_trail_y))
    
    # Convert current scanner position to screen coordinates
    screen_x, screen_y = world_to_screen(scanner_x, scanner_y)
    
    # Add current position to trail
    scanner_trail.append((scanner_x, scanner_y))
    
    # Limit trail length
    if len(scanner_trail) > max_trail_length:
        scanner_trail = scanner_trail[-max_trail_length:]
    
    # Draw trail
    for i, (screen_trail_x, screen_trail_y) in enumerate(screen_trail):
        # Calculate alpha based on position in trail (older = more transparent)
        alpha = int(150 * (i / max_trail_length))
        trail_radius = scanner_radius * 0.8 * (i / max_trail_length)
        trail_color = (*SCANNER_COLOR, alpha)
        pygame.draw.circle(screen, trail_color, (int(screen_trail_x), int(screen_trail_y)), max(1, int(trail_radius)))
    
    # Add flickering effect to scanner
    flicker_intensity = random.randint(-scanner_flicker_intensity, scanner_flicker_intensity)
    flicker_color = (
        min(255, max(100, SCANNER_COLOR[0] + flicker_intensity)),
        min(255, max(100, SCANNER_COLOR[1] + flicker_intensity)),
        min(255, max(50, SCANNER_COLOR[2] - abs(flicker_intensity)))
    )
    
    # Draw scanner with glow effect
    glow_surf = pygame.Surface((scanner_radius * 4, scanner_radius * 4), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (*flicker_color, 70), (scanner_radius * 2, scanner_radius * 2), scanner_radius * 2)
    screen.blit(glow_surf, (screen_x - scanner_radius * 2, screen_y - scanner_radius * 2))
    
    # Draw scanner core
    pygame.draw.circle(screen, flicker_color, (int(screen_x), int(screen_y)), scanner_radius)

    # Draw scanning effect lines occasionally
    if random.random() > 0.7:
        scan_length = random.randint(10, 20)
        angle = random.uniform(0, 2 * math.pi)
        end_x = screen_x + math.cos(angle) * scan_length
        end_y = screen_y + math.sin(angle) * scan_length
        scan_color = (*flicker_color, 150)
        pygame.draw.line(screen, scan_color, (screen_x, screen_y), (end_x, end_y), 1)

def spawn_data_shard():
    # Don't spawn if at max capacity
    if len(data_shards) >= max_shards:
        return
    
    # Find a valid position for the shard
    valid_position = False
    attempts = 0
    
    while not valid_position and attempts < 50:
        attempts += 1
        # Distribute shards across the world
        x = random.randint(50, WORLD_WIDTH - 50)
        y = random.randint(50, WORLD_HEIGHT - 50)
        
        # Check if too close to player, node, or other shards
        too_close = False
        
        # Check distance to player
        if math.sqrt((x - player_x)**2 + (y - player_y)**2) < 100:
            too_close = True
            
        # Check distance to node
        if math.sqrt((x - node_x)**2 + (y - node_y)**2) < 100:
            too_close = True
            
        # Check distance to other shards
        for shard in data_shards:
            if math.sqrt((x - shard['x'])**2 + (y - shard['y'])**2) < 80:
                too_close = True
                break
        
        # Check collision with walls in maze environment
        if current_environment == ENVIRONMENT_MAZE:
            shard_rect = pygame.Rect(x - shard_size, y - shard_size, shard_size * 2, shard_size * 2)
            for wall in walls:
                if shard_rect.colliderect(wall):
                    too_close = True
                    break
        
        if not too_close:
            valid_position = True
            # Create a new data shard
            data_shards.append({
                'x': x,
                'y': y,
                'rotation': random.uniform(0, 360),  # Random initial rotation
                'rotation_speed': random.uniform(-2, 2)  # Random rotation speed
            })

def update_data_shards():
    global shard_glow_intensity, shard_glow_direction, shard_spawn_timer
    
    # Update pulse effect for all shards
    shard_glow_intensity += shard_pulse_speed * shard_glow_direction
    if shard_glow_intensity > 0.5 or shard_glow_intensity < 0:
        shard_glow_direction *= -1
    
    # Update rotation for all shards
    for shard in data_shards:
        shard['rotation'] += shard['rotation_speed']
        if shard['rotation'] >= 360:
            shard['rotation'] -= 360
    
    # Update spawn timer
    shard_spawn_timer += clock.get_time() / 1000
    if shard_spawn_timer >= shard_spawn_interval and len(data_shards) < max_shards:
        spawn_data_shard()
        shard_spawn_timer = 0

def draw_data_shards():
    for shard in data_shards:
        # Check if shard is visible on screen
        if not is_visible_on_screen(shard['x'] - shard_size, shard['y'] - shard_size, 
                                   shard_size * 2, shard_size * 2):
            continue
        
        # Convert world to screen coordinates
        screen_x, screen_y = world_to_screen(shard['x'], shard['y'])
        
        # Calculate current glow intensity
        glow_factor = 0.5 + shard_glow_intensity
        
        # Draw outer glow
        glow_size = shard_size * 1.8
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        glow_alpha = int(100 * glow_factor)
        
        # Create triangle points for glow
        center_x, center_y = glow_size, glow_size
        angle = math.radians(shard['rotation'])
        points = []
        
        for i in range(3):
            point_angle = angle + math.radians(120 * i)
            point_x = center_x + math.cos(point_angle) * glow_size
            point_y = center_y + math.sin(point_angle) * glow_size
            points.append((point_x, point_y))
        
        # Draw glow triangle
        pygame.draw.polygon(glow_surf, (*SHARD_COLOR, glow_alpha), points)
        
        # Apply a blur effect to the glow (simple implementation)
        pygame.draw.polygon(glow_surf, (*SHARD_COLOR, glow_alpha // 2), points, 5)
        
        # Draw the main shard
        shard_surf = pygame.Surface((shard_size * 2, shard_size * 2), pygame.SRCALPHA)
        center_x, center_y = shard_size, shard_size
        angle = math.radians(shard['rotation'])
        points = []
        
        for i in range(3):
            point_angle = angle + math.radians(120 * i)
            point_x = center_x + math.cos(point_angle) * shard_size
            point_y = center_y + math.sin(point_angle) * shard_size
            points.append((point_x, point_y))
        
        # Draw the main triangle with brightness based on glow factor
        bright_color = (
            min(255, int(SHARD_COLOR[0] + 50 * glow_factor)),
            min(255, int(SHARD_COLOR[1] + 50 * glow_factor)),
            min(255, int(SHARD_COLOR[2]))
        )
        pygame.draw.polygon(shard_surf, bright_color, points)
        
        # Position and draw
        screen.blit(glow_surf, (screen_x - glow_size, screen_y - glow_size))
        screen.blit(shard_surf, (screen_x - shard_size, screen_y - shard_size))

def check_shard_collection():
    global data_shards, player_score
    
    # Create player hitbox
    player_center_x = player_x + player_size // 2
    player_center_y = player_y + player_size // 2
    player_radius = player_size // 2
    
    # Check each shard
    collected_shards = []
    for i, shard in enumerate(data_shards):
        distance = math.sqrt((player_center_x - shard['x'])**2 + (player_center_y - shard['y'])**2)
        if distance < player_radius + shard_size:
            collected_shards.append(i)
    
    # If shards were collected, trigger effects
    if collected_shards:
        # Trigger a small screen shake
        trigger_screen_shake(0.2, 3)
        
        # Play collection sound
        if sound_enabled:
            try:
                collect_sound.play()
            except:
                pass
    
    # Remove collected shards (in reverse order to avoid index issues)
    for i in sorted(collected_shards, reverse=True):
        data_shards.pop(i)
        player_score += 1

def upgrade_decoy():
    global decoy_upgraded, showing_upgrade, upgrade_timer, decoy_max_duration
    
    if not decoy_upgraded and player_score >= 5:
        # Double the decoy duration
        decoy_max_duration = 4  # Increase from 2 to 4 seconds
        decoy_upgraded = True
        showing_upgrade = True
        upgrade_timer = 0

def draw_score():
    # Create glowing effect for score text
    glow_factor = 0.5 + shard_glow_intensity
    
    # Draw score with glow
    score_text = f"DATA: {player_score}/5"
    
    # Draw glow layer
    glow_surf = score_font.render(score_text, True, (*SCORE_COLOR, 100))
    for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
        screen.blit(glow_surf, (20 + offset[0], 20 + offset[1]))
    
    # Draw main text
    text_surf = score_font.render(score_text, True, SCORE_COLOR)
    screen.blit(text_surf, (20, 20))
    
    # Draw upgrade prompt if score >= 5 and not upgraded yet
    if player_score >= 5 and not decoy_upgraded:
        upgrade_text = "Press 'E' to enhance decoy"
        
        # Add glitchy effect every few frames
        if random.random() > 0.7:
            # Replace random characters with glitch characters
            chars = list(upgrade_text)
            for i in range(random.randint(0, 2)):
                idx = random.randint(0, len(chars) - 1)
                chars[idx] = random.choice(['#', '$', '%', '&', '*'])
            upgrade_text = ''.join(chars)
        
        prompt_surf = small_font.render(upgrade_text, True, SHARD_COLOR)
        prompt_rect = prompt_surf.get_rect()
        prompt_rect.left = 20
        prompt_rect.top = 50
        
        # Draw with slight movement for glitch effect
        offset_x = random.randint(-1, 1)
        offset_y = random.randint(-1, 1)
        screen.blit(prompt_surf, (prompt_rect.left + offset_x, prompt_rect.top + offset_y))

def show_upgrade_message():
    global upgrade_timer, showing_upgrade
    
    if showing_upgrade:
        upgrade_timer += clock.get_time() / 1000
        if upgrade_timer >= upgrade_duration:
            showing_upgrade = False
            return
        
        # Create upgrade message with glitch effect
        message = "DECOY ENHANCED"
        
        # Apply glitch effect
        if random.random() > 0.7:
            # Randomly replace characters
            chars = list(message)
            for i in range(random.randint(1, 3)):
                idx = random.randint(0, len(chars) - 1)
                chars[idx] = random.choice(['#', '$', '%', '&', '*', '!', '@'])
            message = ''.join(chars)
        
        # Calculate opacity based on time (fade in and out)
        progress = upgrade_timer / upgrade_duration
        alpha = 255
        if progress < 0.2:  # Fade in
            alpha = int(255 * (progress / 0.2))
        elif progress > 0.8:  # Fade out
            alpha = int(255 * ((1 - progress) / 0.2))
        
        # Render text with glow effect
        message_font = font
        text_surf = message_font.render(message, True, SHARD_COLOR)
        text_rect = text_surf.get_rect(center=(VIEWPORT_WIDTH // 2, VIEWPORT_HEIGHT // 3))
        
        # Add slight offset for glitchy movement
        offset_x = random.randint(-3, 3)
        offset_y = random.randint(-3, 3)
        
        # Draw semi-transparent background
        bg_rect = text_rect.inflate(40, 20)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surf.fill(BLACK)
        bg_surf.set_alpha(180)
        screen.blit(bg_surf, (bg_rect.left + offset_x, bg_rect.top + offset_y))
        
        # Draw glowing text
        glow_surf = message_font.render(message, True, (*SHARD_COLOR, 100))
        for glow_offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_pos = (text_rect.left + offset_x + glow_offset[0], 
                         text_rect.top + offset_y + glow_offset[1])
            screen.blit(glow_surf, glow_pos)
        
        # Set text alpha
        text_surf.set_alpha(alpha)
        screen.blit(text_surf, (text_rect.left + offset_x, text_rect.top + offset_y))

def draw_cooldown_bar():
    # Draw cooldown bar background
    bar_width = 200
    bar_height = 10
    bar_x = VIEWPORT_WIDTH // 2 - bar_width // 2
    bar_y = VIEWPORT_HEIGHT - 20
    
    # Draw background
    pygame.draw.rect(screen, (30, 30, 30), (bar_x, bar_y, bar_width, bar_height))
    
    # Calculate fill amount
    if not decoy_can_use:
        fill_percent = 1 - (decoy_cooldown / decoy_max_cooldown)
        fill_width = int(bar_width * fill_percent)
        pygame.draw.rect(screen, COOLDOWN_COLOR, (bar_x, bar_y, fill_width, bar_height))
    else:
        # Full bar when ready
        pygame.draw.rect(screen, COOLDOWN_COLOR, (bar_x, bar_y, bar_width, bar_height))
    
    # Add label
    cooldown_label = font.render("DECOY", True, (200, 200, 200))
    cooldown_label_rect = cooldown_label.get_rect()
    cooldown_label_rect.centerx = bar_x + bar_width // 2
    cooldown_label_rect.bottom = bar_y - 5
    screen.blit(cooldown_label, cooldown_label_rect)
    
    # If AI is adapting (after 2 decoys), show warning
    if decoy_count >= 2:
        warning_text = small_font.render("AI ADAPTING", True, (255, 100, 0))
        warning_rect = warning_text.get_rect()
        warning_rect.centerx = bar_x + bar_width // 2
        warning_rect.top = bar_y + bar_height + 5
        screen.blit(warning_text, warning_rect)
    
    # Show environment timer
    env_fill_percent = 1 - (environment_timer / environment_change_interval)
    env_bar_width = 100
    env_bar_height = 5
    env_bar_x = VIEWPORT_WIDTH - env_bar_width - 10
    env_bar_y = 10
    
    # Draw environment timer background
    pygame.draw.rect(screen, (30, 30, 30), (env_bar_x, env_bar_y, env_bar_width, env_bar_height))
    
    # Draw fill
    env_fill_width = int(env_bar_width * env_fill_percent)
    env_color = GRID_COLOR if current_environment == ENVIRONMENT_OPEN else WALL_COLOR
    pygame.draw.rect(screen, env_color, (env_bar_x, env_bar_y, env_fill_width, env_bar_height))
    
    # Add environment label
    env_label = small_font.render(
        "OPEN GRID" if current_environment == ENVIRONMENT_OPEN else "LOCKED MAZE", 
        True, 
        env_color
    )
    env_label_rect = env_label.get_rect()
    env_label_rect.right = env_bar_x - 5
    env_label_rect.centery = env_bar_y + env_bar_height // 2
    screen.blit(env_label, env_label_rect)

def show_win_message():
    win_text = font.render('DATA EXTRACTED', True, (0, 255, 0))
    win_rect = win_text.get_rect(center=(VIEWPORT_WIDTH // 2, VIEWPORT_HEIGHT // 2))
    
    # Create a semi-transparent background
    bg_surface = pygame.Surface((win_rect.width + 40, win_rect.height + 40))
    bg_surface.fill(BLACK)
    bg_surface.set_alpha(200)
    bg_rect = bg_surface.get_rect(center=(VIEWPORT_WIDTH // 2, VIEWPORT_HEIGHT // 2))
    
    screen.blit(bg_surface, bg_rect)
    screen.blit(win_text, win_rect)
    
    subtext = font.render('Press ESC to exit', True, (200, 200, 200))
    subtext_rect = subtext.get_rect(center=(VIEWPORT_WIDTH // 2, VIEWPORT_HEIGHT // 2 + 50))
    screen.blit(subtext, subtext_rect)

def show_alert_message():
    global firewall_alert_time, show_alert
    
    # Update alert timer
    if show_alert:
        firewall_alert_time += clock.get_time() / 1000
        if firewall_alert_time >= alert_duration:
            firewall_alert_time = 0
            show_alert = False
            return
    
    # Create alert text
    alert_text = alert_font.render('SYSTEM ALERT', True, (255, 50, 0))
    alert_rect = alert_text.get_rect(center=(VIEWPORT_WIDTH // 2, VIEWPORT_HEIGHT // 2))
    
    # Create a semi-transparent background
    bg_surface = pygame.Surface((alert_rect.width + 40, alert_rect.height + 40))
    bg_surface.fill(BLACK)
    bg_surface.set_alpha(180)
    bg_rect = bg_surface.get_rect(center=(VIEWPORT_WIDTH // 2, VIEWPORT_HEIGHT // 2))
    
    screen.blit(bg_surface, bg_rect)
    screen.blit(alert_text, alert_rect)

def draw_start_screen():
    """Draw the start screen with game instructions"""
    # Fill the background with black
    screen.fill(BLACK)
    
    # Draw animated grid as background
    draw_grid()
    
    # Draw some particles for atmosphere
    draw_particles()
    
    # Draw title with glow effect
    title_font = pygame.font.SysFont('Arial', 60, bold=True)
    
    # Calculate pulsing glow based on time
    title_pulse = math.sin(pygame.time.get_ticks() / 500) * 0.5 + 0.5  # Value between 0 and 1
    glow_size = int(10 + title_pulse * 5)
    glow_alpha = int(100 + title_pulse * 50)
    
    # Create title text with cyberpunk colors
    title_text = "CYBERPUNK HACKER DUEL"
    title_shadow = title_font.render(title_text, True, (WALL_COLOR[0], WALL_COLOR[1], WALL_COLOR[2], glow_alpha))
    title_glow = title_font.render(title_text, True, (SHARD_COLOR[0], SHARD_COLOR[1], SHARD_COLOR[2], glow_alpha))
    title_main = title_font.render(title_text, True, GRID_COLOR)
    
    # Position for title
    title_x = VIEWPORT_WIDTH // 2
    title_y = 100
    
    # Draw glow effect
    for offset in range(1, glow_size, 2):
        for x_offset, y_offset in [(offset, 0), (-offset, 0), (0, offset), (0, -offset)]:
            title_rect = title_shadow.get_rect(center=(title_x + x_offset, title_y + y_offset))
            screen.blit(title_shadow, title_rect)
    
    # Draw inner glow
    title_rect = title_glow.get_rect(center=(title_x, title_y))
    screen.blit(title_glow, title_rect)
    
    # Draw main title
    title_rect = title_main.get_rect(center=(title_x, title_y))
    screen.blit(title_main, title_rect)
    
    # Draw a glitchy subtitle with occasional character replacement
    subtitle_text = "INFILTRATE. EXTRACT. SURVIVE."
    if random.random() > 0.9:  # Occasionally glitch text
        chars = list(subtitle_text)
        glitch_count = random.randint(1, 3)
        for _ in range(glitch_count):
            idx = random.randint(0, len(chars) - 1)
            chars[idx] = random.choice(['#', '$', '%', '&', '*', '!', '@'])
        subtitle_text = ''.join(chars)
    
    subtitle_font = pygame.font.SysFont('Arial', 22)
    subtitle_surf = subtitle_font.render(subtitle_text, True, SHARD_COLOR)
    subtitle_rect = subtitle_surf.get_rect(center=(title_x, title_y + 50))
    screen.blit(subtitle_surf, subtitle_rect)
    
    # Draw instruction box
    instr_width, instr_height = 500, 300
    instr_x = (VIEWPORT_WIDTH - instr_width) // 2
    instr_y = subtitle_rect.bottom + 30
    
    # Create semi-transparent black background with border
    instr_surf = pygame.Surface((instr_width, instr_height), pygame.SRCALPHA)
    pygame.draw.rect(instr_surf, (0, 0, 0, 180), (0, 0, instr_width, instr_height))
    
    # Draw glowing border with animated effect
    border_color = (
        int(WALL_COLOR[0] * (0.5 + title_pulse * 0.5)),
        int(WALL_COLOR[1] * (0.5 + title_pulse * 0.5)),
        int(WALL_COLOR[2] * (0.5 + title_pulse * 0.5))
    )
    pygame.draw.rect(instr_surf, border_color, (0, 0, instr_width, instr_height), 2)
    
    screen.blit(instr_surf, (instr_x, instr_y))
    
    # Draw section title
    section_font = pygame.font.SysFont('Arial', 24, bold=True)
    section_surf = section_font.render("MISSION BRIEFING", True, GRID_COLOR)
    section_rect = section_surf.get_rect(center=(instr_x + instr_width // 2, instr_y + 25))
    screen.blit(section_surf, section_rect)
    
    # Draw horizontal separator line
    pygame.draw.line(screen, GRID_COLOR, 
                    (instr_x + 50, section_rect.bottom + 10),
                    (instr_x + instr_width - 50, section_rect.bottom + 10), 1)
    
    # Draw instruction text
    instructions = [
        "OBJECTIVE: Reach the security node (red circle) to extract data",
        "CONTROLS:",
        "• WASD / Arrow Keys - Move your hacker",
        "• Q - Deploy decoy to distract the firewall",
        "• E - Enhance decoy (requires 5 data shards)",
        "• ESC - Exit game",
        "",
        "TIPS:",
        "• Collect cyan data shards to power up your decoy",
        "• Avoid the orange firewall or be reset to start",
        "• Purple walls appear in maze mode - find a path around them",
        "• Environment shifts every 15 seconds - plan accordingly",
        "• The minimap in the corner shows the full world"
    ]
    
    text_font = pygame.font.SysFont('Arial', 16)
    y_offset = section_rect.bottom + 25
    
    for i, line in enumerate(instructions):
        # Highlight headers with different colors
        if line.endswith(':'):
            line_color = SHARD_COLOR
        elif line.startswith('•'):
            line_color = (200, 200, 200)
        else:
            line_color = (150, 150, 150)
            
        text_surf = text_font.render(line, True, line_color)
        text_rect = text_surf.get_rect(x=instr_x + 30, y=y_offset)
        screen.blit(text_surf, text_rect)
        y_offset += 22
    
    # Draw "Press SPACE to start" with blinking effect
    if math.sin(pygame.time.get_ticks() / 300) > 0:  # Blink effect
        start_font = pygame.font.SysFont('Arial', 28, bold=True)
        start_text = "Press SPACE to begin mission"
        
        # Create glowing text effect
        glow_surf = start_font.render(start_text, True, (SHARD_COLOR[0]//2, SHARD_COLOR[1]//2, SHARD_COLOR[2]//2))
        start_surf = start_font.render(start_text, True, SHARD_COLOR)
        
        glow_rect = glow_surf.get_rect(center=(VIEWPORT_WIDTH // 2, instr_y + instr_height + 50))
        start_rect = start_surf.get_rect(center=(VIEWPORT_WIDTH // 2, instr_y + instr_height + 50))
        
        # Draw glow first, then text
        for offset in range(1, 3):
            for x_offset, y_offset in [(offset, 0), (-offset, 0), (0, offset), (0, -offset)]:
                screen.blit(glow_surf, (glow_rect.x + x_offset, glow_rect.y + y_offset))
        
        screen.blit(start_surf, start_rect)
    
    # Occasionally add scanline effect
    if random.random() > 0.8:
        scanline_surf = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT), pygame.SRCALPHA)
        for y in range(0, VIEWPORT_HEIGHT, 4):
            pygame.draw.line(scanline_surf, (255, 255, 255, 15), (0, y), (VIEWPORT_WIDTH, y))
        screen.blit(scanline_surf, (0, 0))

# Start ambient sound loop if available
if sound_enabled:
    try:
        ambient_sound.play(-1)  # -1 makes it loop indefinitely
    except:
        print("Could not play ambient sound")

# Initialize with some shards
for _ in range(2):
    spawn_data_shard()

# Initialize particles
spawn_particles(50)  # Start with some particles

# Main game loop
running = True
game_started = False  # New flag to track if the main game has started

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and game_won:
                running = False
            # Space to start game from the start screen
            elif event.key == pygame.K_SPACE and not game_started:
                game_started = True
            # Q key to spawn decoy (only if game is started and not won)
            elif event.key == pygame.K_q and game_started and not game_won:
                if decoy_can_use:
                    spawn_decoy()
            # E key to upgrade decoy if enough data collected
            elif event.key == pygame.K_e and game_started and not game_won:
                if player_score >= 5 and not decoy_upgraded:
                    upgrade_decoy()
    
    # Show start screen if game not started
    if not game_started:
        draw_start_screen()
        pygame.display.flip()
        clock.tick(FPS)
        continue
    
    # Main game logic (only runs if game has started)
    # Get pressed keys for player movement (only if game not won)
    if not game_won:
        keys = pygame.key.get_pressed()
        
        # Calculate potential new positions
        new_x, new_y = player_x, player_y
        
        # Left movement (Left Arrow or A)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_x = max(0, player_x - player_speed)
        # Right movement (Right Arrow or D)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_x = min(WORLD_WIDTH - player_size, player_x + player_speed)
        # Up movement (Up Arrow or W)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            new_y = max(0, player_y - player_speed)
        # Down movement (Down Arrow or S)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_y = min(WORLD_HEIGHT - player_size, player_y + player_speed)
        
        # Check wall collisions before applying movement
        if not check_wall_collision(new_x, player_y):
            player_x = new_x
        if not check_wall_collision(player_x, new_y):
            player_y = new_y
    
    # Update camera position to follow player
    update_camera()
    
    # Update decoy status
    update_decoy()
    
    # Update scanner
    update_scanner()
    
    # Update environment
    update_environment()
    
    # Update data shards
    update_data_shards()
    
    # Update particles
    update_particles()
    
    # Update screen shake effect
    update_screen_shake()
    
    # Check for shard collection
    check_shard_collection()
    
    # Clear screen
    screen.fill(BLACK)
    
    # Draw grid
    draw_grid()
    
    # Draw particles (behind everything except the grid)
    draw_particles()
    
    # Draw walls if in maze environment
    draw_walls()
    
    # Draw data shards
    draw_data_shards()
    
    # Draw security node
    draw_security_node()
    
    # Draw firewall
    draw_firewall()
    
    # Draw decoy if active
    if decoy_active:
        draw_decoy()
    
    # Draw scanner if active
    if scanner_active:
        draw_scanner()
    
    # Draw player
    draw_player()
    
    # Draw score
    draw_score()
    
    # Draw cooldown bar and environment timer
    draw_cooldown_bar()
    
    # Draw upgrade message if active
    if showing_upgrade:
        show_upgrade_message()
    
    # Draw transition effect if active
    if environment_transition:
        draw_transition_effect()
    
    # Check collision with security node
    if not game_won and check_node_collision():
        game_won = True
    
    # Check collision with firewall only if game isn't won
    if not game_won and check_firewall_collision():
        reset_player_position()
    
    # Show win message if game is won
    if game_won:
        show_win_message()
    
    # Show alert message if player hit the firewall
    if show_alert:
        show_alert_message()
    
    # Update display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(FPS)

# Stop sounds before quitting
if sound_enabled:
    pygame.mixer.stop()

# Quit pygame
pygame.quit()
sys.exit()
