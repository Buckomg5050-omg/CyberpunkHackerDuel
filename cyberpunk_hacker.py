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
# Base world dimensions (entire game world) - will be scaled based on level
BASE_WORLD_WIDTH, BASE_WORLD_HEIGHT = 1600, 1200
# Initialize world dimensions with base values
WORLD_WIDTH, WORLD_HEIGHT = BASE_WORLD_WIDTH, BASE_WORLD_HEIGHT

screen = pygame.display.set_mode((VIEWPORT_WIDTH, VIEWPORT_HEIGHT))
pygame.display.set_caption("Cyberpunk Hacker Duel")

# Fonts - using built-in system fonts with cyberpunk aesthetics
# Try these fonts in order of preference - many systems will have at least one
cyberpunk_fonts = ['Orbitron', 'Audiowide', 'Blender Pro', 'Tron', 'Chakra Petch', 
                    'Syncopate', 'Rajdhani', 'Electrolize', 'Orbitron', 'Titillium Web', 
                    'Exo 2', 'Quantico', 'Play', 'Ubuntu Mono', 'Courier New']

# Custom font loading from assets
def load_font(filename, size, bold=False):
    """Load a font from the assets/fonts directory"""
    try:
        font_path = os.path.join(os.path.dirname(__file__), 'assets', 'fonts', filename)
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)
        else:
            print(f"Font file not found: {font_path}")
            return get_system_font(size, bold)
    except Exception as e:
        print(f"Error loading font {filename}: {e}")
        return get_system_font(size, bold)

def get_system_font(size, bold=False):
    """Get the best available cyberpunk-style font from system fonts"""
    available_fonts = pygame.font.get_fonts()
    
    for font_name in cyberpunk_fonts:
        if font_name.lower() in available_fonts:
            return pygame.font.SysFont(font_name, size, bold=bold)
    
    # Fall back to default sans font
    return pygame.font.SysFont(None, size, bold=bold)

# Our available cyberpunk fonts in assets
asset_fonts = {
    'quantico_regular': 'quantico-regular.ttf',
    'quantico_bold': 'quantico-bold.ttf',
    'tr2n': 'Tr2n.ttf',
    'doctor_glitch': 'Doctor Glitch.otf',
    'origin_tech': 'OriginTech personal use.ttf',
    'interfearence': 'Interfearence.ttf',
    'metro_grunge': 'Metro Grunge.ttf',
    'doctor_satan': 'Doctor Satan.ttf',
    'pixel_game': 'Pixel Game.otf'
}

# Load fonts from assets directory first, fallback to system fonts
try:
    # Load different fonts for different UI elements to create visual hierarchy
    font = load_font(asset_fonts['origin_tech'], 36)  # Main game font
    alert_font = load_font(asset_fonts['doctor_satan'], 42)  # Alert messages
    small_font = load_font(asset_fonts['tr2n'], 16)  # Small text
    score_font = load_font(asset_fonts['pixel_game'], 24)  # Score display with Pixel Game font
    title_font = load_font(asset_fonts['doctor_glitch'], 48)  # Title
    subtitle_font = load_font(asset_fonts['tr2n'], 22)  # Subtitle
    section_font = load_font(asset_fonts['metro_grunge'], 24)  # Section headers
    button_font = load_font(asset_fonts['tr2n'], 22)  # Button text
    text_font = load_font(asset_fonts['quantico_regular'], 16)  # Instructions text
    start_font = load_font(asset_fonts['quantico_bold'], 28)  # Start prompt - Changed from interfearence to quantico_bold
except Exception as e:
    print(f"Error setting up custom fonts: {e}. Falling back to system fonts.")
    # Fall back to system fonts
    font = get_system_font(36)
    alert_font = get_system_font(42, bold=True)
    small_font = get_system_font(16)
    score_font = get_system_font(24)
    title_font = get_system_font(48, bold=True)
    subtitle_font = get_system_font(22)
    section_font = get_system_font(24, bold=True)
    button_font = get_system_font(22, bold=True)
    text_font = get_system_font(16)
    start_font = get_system_font(28, bold=True)

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
print(f"Looking for sound files in: {sounds_folder}")

# Create a DummySound class for when sound files can't be loaded
class DummySound:
    def play(self, *args, **kwargs): pass
    def set_volume(self, *args, **kwargs): pass

# Initialize with dummy sounds by default
ambient_sound = DummySound()
impact_sound = DummySound()
collect_sound = DummySound()
sound_enabled = False

try:
    # Initialize sound mixer
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    
    # Try to load each sound file separately
    sound_loaded_count = 0
    
    # Load ambient sound
    try:
        ambient_path = os.path.join(sounds_folder, 'ambient_hum.wav')
        if os.path.exists(ambient_path) and os.path.getsize(ambient_path) > 100:  # Ensure it's not empty
            ambient_sound = pygame.mixer.Sound(ambient_path)
            ambient_sound.set_volume(0.3)
            print("Loaded ambient sound")
            sound_loaded_count += 1
    except Exception as e:
        print(f"Failed to load ambient sound: {e}")
    
    # Load impact sound
    try:
        impact_path = os.path.join(sounds_folder, 'impact.wav')
        if os.path.exists(impact_path) and os.path.getsize(impact_path) > 100:
            impact_sound = pygame.mixer.Sound(impact_path)
            impact_sound.set_volume(0.5)
            print("Loaded impact sound")
            sound_loaded_count += 1
    except Exception as e:
        print(f"Failed to load impact sound: {e}")
    
    # Load collect sound
    try:
        collect_path = os.path.join(sounds_folder, 'collect.wav')
        if os.path.exists(collect_path) and os.path.getsize(collect_path) > 100:
            collect_sound = pygame.mixer.Sound(collect_path)
            collect_sound.set_volume(0.4)
            print("Loaded collect sound")
            sound_loaded_count += 1
    except Exception as e:
        print(f"Failed to load collect sound: {e}")
    
    # Enable sound if we managed to load at least one sound
    if sound_loaded_count > 0:
        sound_enabled = True
        print(f"Successfully loaded {sound_loaded_count}/3 sound files")
    else:
        print("No sound files could be loaded, running in silent mode")
except Exception as e:
    print(f"Error initializing sound system: {e}")
    print("Warning: Sound system initialization failed. Running without audio.")

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
player_dead = False

# Player health settings
player_max_health = 100
player_health = player_max_health
player_health_regen = 0  # Health regeneration per second (can be implemented later)
damage_cooldown = 0  # Cooldown between damage events
damage_cooldown_duration = 1.0  # Seconds of invulnerability after taking damage

# Define decoy particles list for trailing effect when decoy is ready
decoy_ready_particles = []

# Variables to track previous player position for trail effects
prev_player_x = 0
prev_player_y = 0

# Security node settings
node_x = WORLD_WIDTH - 150  # Position it on the right side of the world
node_y = WORLD_HEIGHT // 2   # Center it vertically
node_radius = 20
node_pulse_time = 0
node_pulse_interval = 0.5  # seconds
node_current_color = NODE_COLOR_BRIGHT
node_is_bright = True

# Firewall settings
firewall_width = 8  # Start with level 1 width
firewall_height = 200  # Start with a shorter firewall that can be dodged
firewall_x = 0
firewall_y = WORLD_HEIGHT // 2 - 100  # Position it in the middle of the screen initially
firewall_speed = 3  # Start with level 1 speed
firewall_alpha_base = 200
firewall_flicker_intensity = 20  # Start with level 1 flicker intensity
firewall_vertical_speed = 1  # Speed at which the firewall moves vertically
firewall_vertical_direction = 1  # 1 = down, -1 = up
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
show_decoy_tutorial = True  # Flag to show tutorial only on first use
tutorial_active = False  # Flag to indicate tutorial is currently displayed
show_shard_tutorial = True  # Flag to show shard tutorial only on first collection
shard_tutorial_active = False  # Flag to indicate shard tutorial is currently displayed

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
current_environment = ENVIRONMENT_MAZE  # Always use maze environment
environment_timer = 0
environment_change_interval = 15  # seconds (no longer used for automatic switching)
environment_transition = False
transition_duration = 0.5  # seconds
transition_timer = 0
# Wall settings
walls = []  # List to store wall rectangles
wall_width = 10
wall_height = 50
num_walls = 20
wall_alpha = 0  # For fade-in effect
walls_visible = True  # New variable to track if walls are visible
wall_timer_active = False  # New variable to track if wall timer is active
wall_timer = 0  # Timer for walls reappearing
wall_hide_duration = 15  # How long walls stay hidden in seconds

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
current_level = 1  # Track the current level
max_level = 3  # Maximum number of levels in the game
level_completed = False  # Track if level is completed but not yet progressed

# Clock for controlling FPS
clock = pygame.time.Clock()
FPS = 60

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
    
    # Only spawn new particles occasionally
    if random.random() < 0.3:
        spawn_particles(1)
    
    for i in range(len(particles) - 1, -1, -1):
        particle = particles[i]
        
        # Update age
        particle['age'] += clock.get_time() / 1000
        
        # Check if particle should be removed
        if particle['age'] >= particle['lifetime']:
            particles.pop(i)
            continue
            
        # Update fade effect
        if particle['fade_in']:
            # Fade in
            particle['alpha'] += particle['fade_speed'] * (clock.get_time() / 1000) * 255
            if particle['alpha'] >= 255:
                particle['alpha'] = 255
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
    # Only draw walls if they are visible (controlled by the disable_walls function)
    if not walls_visible or len(walls) == 0:
        return
    
    # Draw the walls with full visibility
    for wall in walls:
        # Check if wall is visible on screen
        if not is_visible_on_screen(wall.x, wall.y, wall.width, wall.height):
            continue
        
        # Convert world to screen coordinates
        screen_x, screen_y = world_to_screen(wall.x, wall.y)
        
        # Create wall surface with alpha
        wall_surf = pygame.Surface((wall.width, wall.height), pygame.SRCALPHA)
        
        # Draw main wall with full opacity
        pygame.draw.rect(wall_surf, (*WALL_COLOR, 200), (0, 0, wall.width, wall.height))
        
        # Add glitch effect occasionally
        if random.random() > 0.95:
            glitch_y = random.randint(0, wall.height - 5)
            glitch_height = random.randint(2, 5)
            glitch_offset = random.randint(-2, 2)
            if glitch_offset != 0 and glitch_y + glitch_height < wall.height:
                section = wall_surf.subsurface((0, glitch_y, wall.width, glitch_height)).copy()
                wall_surf.blit(section, (glitch_offset, glitch_y))
        
        # Draw the wall at the exact screen coordinates
        screen.blit(wall_surf, (screen_x, screen_y))
        
        # For debugging - uncomment to visualize wall collision boxes
        # pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(screen_x, screen_y, wall.width, wall.height), 1)

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
    # Check collision with world boundaries
    if (new_x < player_size/2 or new_x > WORLD_WIDTH - player_size/2 or
        new_y < player_size/2 or new_y > WORLD_HEIGHT - player_size/2):
        return True
    
    # Only check wall collisions if walls are visible
    # This respects the walls_visible flag that is controlled by disable_walls()
    if walls_visible and len(walls) > 0:
        # Create a player rectangle at the new position to check for collisions
        # Player position is the center, rect needs top-left
        player_rect = pygame.Rect(
            new_x - player_size/2,  # Convert center coordinates to top-left
            new_y - player_size/2,  # Convert center coordinates to top-left
            player_size,
            player_size
        )
        
        # Check collision with any wall
        for wall in walls:
            if player_rect.colliderect(wall):
                # Deal 1 damage when colliding with walls if damage cooldown expired
                global player_health, damage_cooldown
                if damage_cooldown <= 0:
                    player_health -= 1  # Wall collision deals 1 damage
                    damage_cooldown = damage_cooldown_duration / 2  # Shorter cooldown for wall collisions
                    
                    # Trigger minor screen shake for feedback
                    trigger_screen_shake(0.1, 2)
                
                return True
    
    return False

def update_environment():
    global wall_timer, wall_timer_active, walls_visible
    
    # Handle wall timer if active - this is the only function that should
    # automatically make walls visible again after being disabled
    if wall_timer_active:
        wall_timer += clock.get_time() / 1000
        
        # Check if wall timer is complete
        if wall_timer >= wall_hide_duration:
            walls_visible = True
            wall_timer_active = False

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
    
    # Convert world to screen coordinates (player_x and player_y represent the player's center)
    screen_x, screen_y = world_to_screen(player_x - player_size/2, player_y - player_size/2)  # Convert center to top-left for drawing
    
    # Calculate visual size (5% larger than collision size)
    visual_size = int(player_size * 1.05)
    
    # Adjust player color based on decoy availability
    decoy_ready_percent = 1.0
    if not decoy_can_use:
        decoy_ready_percent = max(0.3, 1 - (decoy_cooldown / decoy_max_cooldown))
    
    # Create dynamic player color - ensure all values are valid integers
    dynamic_player_color = (
        int(PLAYER_COLOR[0]),
        int(PLAYER_COLOR[1] * 0.5 + PLAYER_COLOR[1] * 0.5 * decoy_ready_percent),
        int(PLAYER_COLOR[2] * decoy_ready_percent)
    )
    
    # Modify player color if taking damage (in damage cooldown)
    if damage_cooldown > 0:
        # Pulsing red effect when in damage cooldown
        flash_intensity = abs(math.sin(pygame.time.get_ticks() / 100)) * 0.6 + 0.4
        damage_overlay = (255 * flash_intensity, 0, 0)
        
        # Mix the damage overlay with the regular player color
        dynamic_player_color = (
            min(255, int(dynamic_player_color[0] * 0.3 + damage_overlay[0] * 0.7)),
            max(0, int(dynamic_player_color[1] * 0.3)),
            max(0, int(dynamic_player_color[2] * 0.3))
        )
    
    # Apply enhanced glow when decoy is fully charged
    is_fully_charged = decoy_can_use
    glow_layers = 4 if is_fully_charged else 3
    
    # Create glow effect layers - adjust for visual size
    glow_size = visual_size + 12
    for i in range(glow_layers):
        # Calculate glow alpha - stronger and more layers when fully charged
        if is_fully_charged:
            # Pulsing glow effect when ready
            pulse = (math.sin(pygame.time.get_ticks() / 200) * 0.3 + 0.7)
            glow_alpha = max(0, min(255, int((90 * pulse) - (i * 20))))
            glow_size_current = visual_size + 4 + (i * 5)  # Larger glow when ready
        else:
            glow_alpha = max(0, min(255, int((60 * decoy_ready_percent) - (i * 20))))
            glow_size_current = visual_size + 4 + (i * 4)
        
        glow_surf = pygame.Surface((glow_size_current, glow_size_current), pygame.SRCALPHA)
        
        # Draw angular shape glow
        points = [
            (glow_size_current * 0.1, glow_size_current * 0.5),  # Left point
            (glow_size_current * 0.5, glow_size_current * 0.1),  # Top point
            (glow_size_current * 0.9, glow_size_current * 0.5),  # Right point
            (glow_size_current * 0.7, glow_size_current * 0.9),  # Bottom right
            (glow_size_current * 0.3, glow_size_current * 0.9)   # Bottom left
        ]
        
        # Ensure color values are valid
        # Enhanced glow color when fully charged
        if is_fully_charged:
            # Create a brighter blue-cyan glow when ready
            pulse_factor = (math.sin(pygame.time.get_ticks() / 200) * 0.4 + 0.6)
            glow_color = (
                max(0, min(255, int(30 + 40 * pulse_factor))),  # Add some cyan tint
                max(0, min(255, int(dynamic_player_color[1] + 50 * pulse_factor))),
                max(0, min(255, int(dynamic_player_color[2] + 30 * pulse_factor))),
                glow_alpha
            )
        else:
            glow_color = (
                max(0, min(255, dynamic_player_color[0])),
                max(0, min(255, dynamic_player_color[1])),
                max(0, min(255, dynamic_player_color[2])),
                glow_alpha
            )
        
        pygame.draw.polygon(glow_surf, glow_color, points)
        
        # Position and draw with screen shake offset - adjust for larger visual size
        visual_offset = (visual_size - player_size) // 2
        pos_x = screen_x - (glow_size_current - visual_size) // 2 + offset_x - visual_offset
        pos_y = screen_y - (glow_size_current - visual_size) // 2 + offset_y - visual_offset
        screen.blit(glow_surf, (pos_x, pos_y))
    
    # Create main player surface with increased visual size
    player_surf = pygame.Surface((visual_size, visual_size), pygame.SRCALPHA)
    
    # Draw angular, sleek player shape
    points = [
        (visual_size * 0.1, visual_size * 0.5),  # Left point
        (visual_size * 0.5, visual_size * 0.1),  # Top point
        (visual_size * 0.9, visual_size * 0.5),  # Right point
        (visual_size * 0.7, visual_size * 0.9),  # Bottom right
        (visual_size * 0.3, visual_size * 0.9)   # Bottom left
    ]
    
    # Draw main shape with dynamic color - ensure values are valid
    clamped_color = (
        max(0, min(255, dynamic_player_color[0])),
        max(0, min(255, dynamic_player_color[1])),
        max(0, min(255, dynamic_player_color[2]))
    )
    
    # Enhance player color when fully charged
    if is_fully_charged:
        pulse = (math.sin(pygame.time.get_ticks() / 300) * 0.3 + 0.7)
        clamped_color = (
            max(0, min(255, int(clamped_color[0] + 20 * pulse))),
            max(0, min(255, int(clamped_color[1] + 30 * pulse))),
            max(0, min(255, int(clamped_color[2] + 40 * pulse)))
        )
    
    pygame.draw.polygon(player_surf, clamped_color, points)
    
    # Create highlight color - pulsing when ready
    if decoy_can_use:
        pulse = (math.sin(pygame.time.get_ticks() / 200) * 0.4 + 0.6)  # Faster, more noticeable pulse
        highlight_color = (
            max(0, min(255, int(clamped_color[0] + 70 * pulse))),
            max(0, min(255, int(clamped_color[1] + 70 * pulse))),
            max(0, min(255, int(clamped_color[2] + 70 * pulse)))
        )
    else:
        highlight_color = (
            max(0, min(255, clamped_color[0] + 30)),
            max(0, min(255, clamped_color[1] + 30)),
            max(0, min(255, clamped_color[2] + 30))
        )
    
    # Draw highlighted edges with thicker line when ready
    line_width = 2 if is_fully_charged else 1
    pygame.draw.polygon(player_surf, highlight_color, points, line_width)
    
    # Position and draw with screen shake offset - adjust position to center larger visual on the player
    visual_offset = (visual_size - player_size) // 2
    screen.blit(player_surf, (screen_x + offset_x - visual_offset, screen_y + offset_y - visual_offset))
    
    # Debug: Uncomment to visualize player collision box
    # pygame.draw.rect(screen, (255, 0, 0), (screen_x + offset_x, screen_y + offset_y, player_size, player_size), 1)

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
    
    # Calculate square size based on original circle radius
    square_size = node_radius * 2
    square_rect = pygame.Rect(
        screen_x - square_size // 2,
        screen_y - square_size // 2,
        square_size,
        square_size
    )
    
    # Draw glow effect (larger semi-transparent square)
    glow_size = square_size * 1.5
    glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
    glow_rect = pygame.Rect(0, 0, glow_size, glow_size)
    glow_alpha = 100 if node_is_bright else 50
    pygame.draw.rect(glow_surface, (*node_current_color, glow_alpha), glow_rect, border_radius=int(glow_size//10))
    screen.blit(glow_surface, (screen_x - glow_size // 2, screen_y - glow_size // 2))
    
    # Draw the node as a square
    pygame.draw.rect(screen, node_current_color, square_rect, border_radius=int(square_size//10))
    
    # Draw three horizontal lines for microchip look
    line_color = (0, 0, 0) if node_is_bright else (255, 255, 255)  # Contrasting color
    line_length = square_size - 6
    line_start_x = screen_x - line_length // 2
    
    # Calculate positions for three evenly spaced lines
    y_offset = square_size // 4
    line_y_positions = [
        screen_y - y_offset,
        screen_y,
        screen_y + y_offset
    ]
    
    # Draw the lines
    for y in line_y_positions:
        pygame.draw.line(screen, line_color, (line_start_x, y), (line_start_x + line_length, y), 2)

def draw_firewall():
    global firewall_x, firewall_y, firewall_vertical_direction
    
    # Move firewall based on level and decoy presence
    if decoy_active:
        # Calculate distance to decoy for variable speed
        dx = decoy_x - firewall_x
        dy = decoy_y - (firewall_y + firewall_height/2)  # Target middle of firewall to decoy
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Horizontal attraction to decoy - stronger at higher levels
        attraction_multiplier = 1.0 + (current_level * 0.2)  # Increases with level
        
        if firewall_x < decoy_x:
            # Speed increases as distance increases - capped at 2x normal speed
            speed_factor = min(2.0, max(1.0, distance / 300))
            firewall_x += firewall_speed * speed_factor * attraction_multiplier
        elif firewall_x > decoy_x:
            speed_factor = min(2.0, max(1.0, distance / 300))
            firewall_x -= firewall_speed * speed_factor * attraction_multiplier
            
        # Vertical movement toward decoy - all levels now, but stronger at higher levels
        vertical_attraction = 0.5 + (current_level * 0.25)  # Increases with level
        
        # Adjust vertical movement based on decoy position
        if abs(dy) > 10:  # Only move if decoy is not already aligned (within 10 pixels)
            # Make vertical movement proportional to distance but with a cap
            vert_speed_factor = min(1.5, max(0.5, abs(dy) / 200))
            vert_step = firewall_vertical_speed * vert_speed_factor * vertical_attraction
            
            if firewall_y + firewall_height/2 < decoy_y:  # If decoy is below firewall center
                firewall_y += vert_step
            else:  # If decoy is above firewall center
                firewall_y -= vert_step
                
        # Add subtle oscillation to make movement more natural
        if random.random() > 0.8:  # 20% chance each frame
            firewall_y += random.uniform(-1.0, 1.0)
    else:
        # Normal movement - depends on level
        if current_level == 1:
            # Level 1: Simple rightward movement with basic vertical bouncing
            firewall_x += firewall_speed
            
            # Simple up/down bouncing movement
            firewall_y += firewall_vertical_speed * firewall_vertical_direction
            
            # Bounce if hitting top or bottom of world
            if firewall_y <= 0:
                firewall_vertical_direction = 1
            elif firewall_y + firewall_height >= WORLD_HEIGHT:
                firewall_vertical_direction = -1
                
        elif current_level == 2:
            # Level 2: Occasional speed variations with more vertical movement
            if random.random() > 0.95:
                # Randomly adjust speed slightly for brief moments
                speed_variation = random.uniform(0.8, 1.2)
                firewall_x += firewall_speed * speed_variation
            else:
                firewall_x += firewall_speed
                
            # Faster vertical movement
            firewall_y += (firewall_vertical_speed * 1.5) * firewall_vertical_direction
            
            # Occasional direction change (2% chance per frame)
            if random.random() > 0.98:
                firewall_vertical_direction *= -1
                
            # Bounce if hitting top or bottom
            if firewall_y <= 0:
                firewall_vertical_direction = 1
            elif firewall_y + firewall_height >= WORLD_HEIGHT:
                firewall_vertical_direction = -1
                
        else:  # Level 3+
            # Level 3+: More smart tracking behavior
            # Horizontal tracking
            if random.random() > 0.7:  # 30% chance to track player
                if player_x > firewall_x + VIEWPORT_WIDTH/2:  # Only accelerate if player is far ahead
                    firewall_x += firewall_speed * 1.3
                else:
                    firewall_x += firewall_speed * 0.9  # Slow down when close to player
            else:
                firewall_x += firewall_speed
                
            # Vertical tracking - attempt to move toward player's y position
            if random.random() > 0.5:  # 50% chance to adjust vertically toward player
                if player_y > firewall_y + firewall_height/2:
                    firewall_y += firewall_vertical_speed * 2
                elif player_y < firewall_y + firewall_height/2:
                    firewall_y -= firewall_vertical_speed * 2
            else:
                # Continue in current direction
                firewall_y += firewall_vertical_speed * 2 * firewall_vertical_direction
                
                # Bounce if hitting boundaries
                if firewall_y <= 0:
                    firewall_vertical_direction = 1
                elif firewall_y + firewall_height >= WORLD_HEIGHT:
                    firewall_vertical_direction = -1
        
        # Reset if off screen horizontally
        if firewall_x > WORLD_WIDTH:
            firewall_x = -firewall_width
            # Randomize vertical position when coming back
            firewall_y = random.randint(0, WORLD_HEIGHT - firewall_height)
    
    # Convert world to screen coordinates
    screen_x, screen_y = world_to_screen(firewall_x, firewall_y)
    
    # Check if firewall is visible on screen
    if screen_x < -firewall_width or screen_x > VIEWPORT_WIDTH:
        return
    
    # Create firewall surface with flicker effect
    firewall_surf = pygame.Surface((firewall_width, firewall_height), pygame.SRCALPHA)
    
    # Add flickering effect - intensity based on level
    flicker_intensity = firewall_flicker_intensity
    if current_level == 1:
        flicker_intensity = firewall_flicker_intensity * 0.5  # Less flickering at level 1
    elif current_level == 2:
        flicker_intensity = firewall_flicker_intensity * 0.8
    
    # Apply flicker effect
    flicker_alpha = min(255, max(100, firewall_alpha_base + random.randint(-int(flicker_intensity), int(flicker_intensity))))
    
    # Draw the firewall line with flicker
    firewall_color_with_alpha = (*FIREWALL_COLOR, flicker_alpha)
    pygame.draw.rect(firewall_surf, firewall_color_with_alpha, (0, 0, firewall_width, firewall_height))
    
    # Level-specific visual enhancements
    if current_level >= 2:
        # Level 2+: Add light data particle effects
        for _ in range(current_level - 1):  # More particles at higher levels
            particle_y = random.randint(0, firewall_height)
            particle_height = random.randint(2, 5)
            pygame.draw.rect(firewall_surf, (255, 255, 255, 150), 
                             (0, particle_y, firewall_width, particle_height))
    
    if current_level >= 3:
        # Level 3+: Add scanning lines
        for _ in range(2):
            scan_y = (pygame.time.get_ticks() // 100) % firewall_height
            scan_y2 = (pygame.time.get_ticks() // 150 + 200) % firewall_height
            pygame.draw.rect(firewall_surf, (255, 255, 255, 100), 
                             (0, scan_y, firewall_width, 1))
            pygame.draw.rect(firewall_surf, (255, 255, 255, 100), 
                             (0, scan_y2, firewall_width, 1))
    
    # Occasionally add glitch effect (horizontal displacement) - more at higher levels
    glitch_chance = 0.95
    if current_level == 1:
        glitch_chance = 0.98  # 2% chance at level 1
    elif current_level == 2:
        glitch_chance = 0.96  # 4% chance at level 2
    # Level 3+ uses the default 5% chance
    
    if random.random() > glitch_chance:
        glitch_y = random.randint(0, firewall_height - 50)
        glitch_height = random.randint(10, 40)
        
        # Level 1 has minimal glitches
        if current_level == 1:
            glitch_offset = random.choice([-1, 1]) # Only shift by 1 pixel
        # Level 2 has moderate glitches
        elif current_level == 2:
            glitch_offset = random.randint(-2, 2)
        # Level 3+ has more extreme glitches
        else:
            glitch_offset = random.randint(-4, 4)
            
        if glitch_offset != 0:
            section = firewall_surf.subsurface((0, glitch_y, firewall_width, glitch_height)).copy()
            firewall_surf.blit(section, (glitch_offset, glitch_y))
    
    screen.blit(firewall_surf, (screen_x, screen_y))

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
    global decoy_active, decoy_x, decoy_y, decoy_duration, decoy_can_use, decoy_cooldown, decoy_count, scanner_active, tutorial_active
    if decoy_can_use:
        decoy_active = True
        decoy_x = player_x
        decoy_y = player_y
        decoy_duration = decoy_max_duration
        decoy_can_use = False
        decoy_cooldown = decoy_max_cooldown
        decoy_count += 1
        
        # Show tutorial on first use
        global show_decoy_tutorial
        if show_decoy_tutorial and decoy_count == 1:
            tutorial_active = True
        
        # If player has used decoy twice or more and not level 1, spawn a scanner
        if decoy_count >= 2 and current_level > 1:
            spawn_scanner()

def spawn_scanner():
    global scanner_active, scanner_x, scanner_y, scanner_trail, scanner_speed
    
    # Don't spawn scanners in level 1
    if current_level == 1:
        return
    
    # Spawn from firewall position
    scanner_active = True
    scanner_x = firewall_x + firewall_width // 2
    scanner_y = random.randint(50, WORLD_HEIGHT - 50)  # Random y position
    scanner_trail = []  # Reset trail
    
    # Adjust scanner speed based on level
    if current_level == 2:
        scanner_speed = 4  # Slower in level 2
    else:  # Level 3+
        scanner_speed = 6  # Faster in level 3+

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
    
    # Movement behavior varies by level
    if current_level == 2:
        # Level 2: Simple, somewhat inaccurate tracking
        # Add some randomness to movement (makes it less accurate)
        dx += random.uniform(-0.2, 0.2)
        dy += random.uniform(-0.2, 0.2)
        
        # Re-normalize after adding randomness
        new_dist = max(0.1, math.sqrt(dx * dx + dy * dy))
        dx /= new_dist
        dy /= new_dist
        
        # Move scanner toward decoy at constant speed
        scanner_x += dx * scanner_speed
        scanner_y += dy * scanner_speed
        
    else:  # Level 3+
        # Level 3: Advanced tracking with variable speed and prediction
        
        # Speed varies with distance - speeds up when far, slows when close
        speed_factor = min(1.5, max(0.8, distance / 200))
        
        # Add slight prediction to target ahead of the decoy's position
        # This makes the scanner appear "smarter"
        if random.random() > 0.5:  # 50% chance to use prediction
            # We don't have actual decoy velocity, but we can estimate based on player
            # movement or just provide a fixed "prediction" behavior
            prediction_x = decoy_center_x + random.randint(-10, 30)  # Predict slightly ahead
            prediction_y = decoy_center_y + random.randint(-20, 20)
            
            # Calculate direction to prediction point instead
            pred_dx = prediction_x - scanner_x
            pred_dy = prediction_y - scanner_y
            pred_dist = max(0.1, math.sqrt(pred_dx * pred_dx + pred_dy * pred_dy))
            
            # Blend the original and prediction directions
            dx = (dx + (pred_dx / pred_dist)) / 2
            dy = (dy + (pred_dy / pred_dist)) / 2
            
            # Re-normalize
            final_dist = max(0.1, math.sqrt(dx * dx + dy * dy))
            dx /= final_dist
            dy /= final_dist
        
        # Move scanner with variable speed
        scanner_x += dx * scanner_speed * speed_factor
        scanner_y += dy * scanner_speed * speed_factor
        
        # Occasionally make sharp movements to appear more aggressive
        if random.random() > 0.95:  # 5% chance
            scanner_x += dx * scanner_speed * 1.5
            scanner_y += dy * scanner_speed * 1.5
    
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
    """Check if player has collided with the security node, return True if collided"""
    # Calculate the player's rectangle
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    
    # Calculate the node's square rectangle
    square_size = node_radius * 2
    node_rect = pygame.Rect(
        node_x - square_size // 2,
        node_y - square_size // 2,
        square_size,
        square_size
    )
    
    # Safety check - make sure node is in a valid position for this level
    min_node_x = WORLD_WIDTH * 0.75  # Node should be in the right quarter of the world
    if node_x < min_node_x:
        # This might cause premature level completion, but this is a silent check now
        pass
    
    # Check if rectangles overlap
    collision = player_rect.colliderect(node_rect)
    
    # If collision, trigger screen shake for feedback
    if collision:
        trigger_screen_shake(0.3, 8)
        
    return collision

def check_firewall_collision():
    # Check if player overlaps with firewall
    player_right = player_x + player_size
    player_bottom = player_y + player_size
    firewall_right = firewall_x + firewall_width
    firewall_bottom = firewall_y + firewall_height
    
    # Check both horizontal and vertical intersection
    horizontal_overlap = ((firewall_x <= player_x < firewall_right) or 
                        (firewall_x < player_right <= firewall_right) or
                        (player_x <= firewall_x and player_right >= firewall_right))
    
    vertical_overlap = ((firewall_y <= player_y < firewall_bottom) or
                      (firewall_y < player_bottom <= firewall_bottom) or
                      (player_y <= firewall_y and player_bottom >= firewall_bottom))
    
    # Both horizontal and vertical components must overlap for a collision
    collision = horizontal_overlap and vertical_overlap
    
    # If collision occurred and damage cooldown has expired, deal damage
    global player_health, damage_cooldown, show_alert
    if collision and damage_cooldown <= 0:
        player_health -= 5  # Firewall deals 5 damage
        damage_cooldown = damage_cooldown_duration  # Start cooldown
        show_alert = True  # Show firewall alert
        
        # Play impact sound if available
        if sound_enabled:
            impact_sound.play()
        
        # Trigger screen shake for better feedback
        trigger_screen_shake()
    
    return collision

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
    
    # Limit trail length - longer trail for higher levels
    max_trail = max_trail_length
    if current_level >= 3:
        max_trail = max_trail_length + 5  # Longer trail for level 3+
        
    if len(scanner_trail) > max_trail:
        scanner_trail = scanner_trail[-max_trail:]
    
    # Draw trail - different colors and effects based on level
    scanner_color = SCANNER_COLOR
    
    if current_level == 2:
        # Level 2: Yellow scanner with simple trail
        scanner_color = (255, 255, 0)  # Yellow
        
        for i, (screen_trail_x, screen_trail_y) in enumerate(screen_trail):
            # Calculate alpha based on position in trail (older = more transparent)
            alpha = int(150 * (i / max_trail))
            # Draw trail segment
            pygame.draw.circle(screen, (*scanner_color, alpha), (screen_trail_x, screen_trail_y), 
                               scanner_radius * (i / max_trail))
            
    else:  # Level 3+
        # Level 3: Red scanner with more advanced effects
        scanner_color = (255, 50, 50)  # Red
        
        # More advanced trail with pulsing effect
        pulse = (math.sin(pygame.time.get_ticks() / 100) + 1) / 2  # 0 to 1 pulsing value
        
        for i, (screen_trail_x, screen_trail_y) in enumerate(screen_trail):
            # Calculate alpha based on position in trail with pulsing effect
            alpha = int(180 * (i / max_trail) * (0.7 + 0.3 * pulse))
            # Draw trail segment with varying sizes
            pygame.draw.circle(screen, (*scanner_color, alpha), (screen_trail_x, screen_trail_y), 
                               scanner_radius * (i / max_trail) * (0.8 + 0.4 * pulse))
    
    # Draw the scanner with flicker effect
    flicker = random.randint(-scanner_flicker_intensity, scanner_flicker_intensity)
    scanner_alpha = min(255, max(100, 200 + flicker))
    
    # Level-specific scanner appearance
    if current_level == 2:
        # Simple circle for level 2
        pygame.draw.circle(screen, (*scanner_color, scanner_alpha), (screen_x, screen_y), scanner_radius)
    else:  # Level 3+
        # More advanced scanner design for level 3+
        # Inner circle
        pygame.draw.circle(screen, (*scanner_color, scanner_alpha), (screen_x, screen_y), scanner_radius)
        
        # Outer ring pulsing
        outer_radius = scanner_radius + 3 + int(2 * math.sin(pygame.time.get_ticks() / 150))
        pygame.draw.circle(screen, (*scanner_color, scanner_alpha // 2), (screen_x, screen_y), outer_radius, 1)
        
        # Scanning lines
        line_angle = (pygame.time.get_ticks() / 20) % 360
        line_end_x = screen_x + math.cos(math.radians(line_angle)) * (scanner_radius + 8)
        line_end_y = screen_y + math.sin(math.radians(line_angle)) * (scanner_radius + 8)
        pygame.draw.line(screen, (*scanner_color, scanner_alpha), (screen_x, screen_y), (line_end_x, line_end_y), 1)

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
    global data_shards, player_score, shard_tutorial_active
    
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
        
        # Show tutorial on first shard collection
        global show_shard_tutorial
        if show_shard_tutorial and player_score == 1:
            shard_tutorial_active = True
            show_shard_tutorial = False

def disable_walls():
    """
    Disables the walls when player spends 5 data shards.
    This is the ONLY function that should modify walls_visible status.
    Walls will automatically reappear after wall_hide_duration seconds.
    """
    global walls_visible, wall_timer_active, wall_timer, player_score, showing_upgrade, upgrade_timer
    
    if player_score >= 5:
        # Only disable walls if they're currently visible
        if walls_visible:
            # Hide walls and start timer
            walls_visible = False
            wall_timer_active = True
            wall_timer = 0
            player_score -= 5  # Subtract 5 data shards
            showing_upgrade = True
            upgrade_timer = 0

def draw_score():
    # Create glowing effect for score text
    score_pulse = math.sin(pygame.time.get_ticks() / 300) * 0.3 + 0.7  # Value between 0.4 and 1.0
    
    # Base score text
    score_text = f"DATA: {player_score}"
    
    # Create colors with the pulse effect
    text_color = (
        int(SCORE_COLOR[0] * score_pulse),
        int(SCORE_COLOR[1] * score_pulse),
        int(SCORE_COLOR[2] * score_pulse)
    )
    
    # Render score with Pixel Game font
    score_surf = score_font.render(score_text, True, text_color)
    score_x = 20
    score_y = 20
    screen.blit(score_surf, (score_x, score_y))
    
    # Display upgrade prompt if enough data collected
    if player_score >= 5:
        # Create upgrade text with a glitch effect
        upgrade_text = "PRESS E TO DISABLE WALLS"
        
        # Add glitchy effect using the glitch_text function
        glitched_upgrade = glitch_text(upgrade_text, 0.2)
        
        # Keep using small_font for the prompt text
        prompt_surf = small_font.render(glitched_upgrade, True, SHARD_COLOR)
        prompt_rect = prompt_surf.get_rect()
        prompt_rect.x = score_x
        prompt_rect.top = score_y + score_surf.get_height() + 5  # Position based on score text height
        
        # Draw with slight movement for glitch effect
        offset_x = random.randint(-1, 1)
        offset_y = random.randint(-1, 1)
        screen.blit(prompt_surf, (prompt_rect.x + offset_x, prompt_rect.y + offset_y))

def show_upgrade_message():
    global upgrade_timer, showing_upgrade
    
    if showing_upgrade:
        upgrade_timer += clock.get_time() / 1000
        if upgrade_timer >= upgrade_duration:
            showing_upgrade = False
            return
        
        # Create upgrade message with glitch effect
        message = "WALLS DISABLED"
        
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
    # This function is now replaced by draw_hud
    # No need to implement any code here
    pass

def show_win_message():
    global level_completed
    level_completed = True
    
    if current_level < max_level:
        glitched_text = glitch_text('ACCESS GRANTED', 0.2)
    else:
        glitched_text = glitch_text('MAIN SERVER BREACHED', 0.2)
    
    win_text = font.render(glitched_text, True, (0, 255, 0))
    win_rect = win_text.get_rect(center=(VIEWPORT_WIDTH // 2, VIEWPORT_HEIGHT // 2 - 40))  # Moved up to make room
    
    # Create a semi-transparent background
    bg_surface = pygame.Surface((win_rect.width + 140, win_rect.height + 180))  # Increased height
    bg_surface.fill(BLACK)
    bg_surface.set_alpha(200)
    bg_rect = bg_surface.get_rect(center=(VIEWPORT_WIDTH // 2, VIEWPORT_HEIGHT // 2))
    
    screen.blit(bg_surface, bg_rect)
    screen.blit(win_text, win_rect)
    
    button_rect = None  # Initialize to None
    
    if current_level < max_level:
        subtext = font.render(f'Level {current_level} Complete', True, (200, 200, 200))
        subtext_rect = subtext.get_rect(center=(VIEWPORT_WIDTH // 2, VIEWPORT_HEIGHT // 2 - 5))
        screen.blit(subtext, subtext_rect)
        
        # Calculate next level world size for display
        next_scaling_factor = 1.0 + current_level * 0.3  # Based on our scaling formula
        next_width = int(BASE_WORLD_WIDTH * next_scaling_factor)
        next_height = int(BASE_WORLD_HEIGHT * next_scaling_factor)
        
        # Show info about expanding world
        world_text = f"Next level: World expanding to {next_width//100}x{next_height//100}"
        world_info = small_font.render(world_text, True, (180, 180, 255))  # Blue tint for emphasis
        world_rect = world_info.get_rect(center=(VIEWPORT_WIDTH // 2, VIEWPORT_HEIGHT // 2 + 30))
        screen.blit(world_info, world_rect)
        
        # Create continue button
        button_width, button_height = 250, 50
        button_x = (VIEWPORT_WIDTH - button_width) // 2
        button_y = VIEWPORT_HEIGHT // 2 + 70  # Moved down a bit
        
        button_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        
        # Change button color based on mouse hover
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        button_color = (SHARD_COLOR[0], SHARD_COLOR[1], SHARD_COLOR[2], 150)
        button_hover = button_rect.collidepoint(mouse_pos)
        
        if button_hover:
            button_color = (SHARD_COLOR[0], SHARD_COLOR[1], SHARD_COLOR[2], 220)
        
        # Draw button background
        pygame.draw.rect(button_surf, button_color, (0, 0, button_width, button_height), border_radius=10)
        
        # Draw button text
        continue_text = "HACK DEEPER"  # Changed to be more thematic
        button_text = button_font.render(continue_text, True, (255, 255, 255))
        text_rect = button_text.get_rect(center=(button_width // 2, button_height // 2))
        button_surf.blit(button_text, text_rect)
        
        # Draw to screen
        screen.blit(button_surf, (button_x, button_y))
    else:
        # Final level complete
        subtext = font.render("Game Complete", True, (200, 200, 200))
        subtext_rect = subtext.get_rect(center=(VIEWPORT_WIDTH // 2, VIEWPORT_HEIGHT // 2 + 20))
        screen.blit(subtext, subtext_rect)
        
        # Show total progression info
        final_scaling = 1.0 + (max_level - 1) * 0.3
        world_text = f"Final network size: {int(BASE_WORLD_WIDTH * final_scaling)//100}x{int(BASE_WORLD_HEIGHT * final_scaling)//100}"
        world_info = small_font.render(world_text, True, (180, 180, 255))
        world_rect = world_info.get_rect(center=(VIEWPORT_WIDTH // 2, VIEWPORT_HEIGHT // 2 + 60))
        screen.blit(world_info, world_rect)
        
        instruction = small_font.render("Press ESC to exit", True, (150, 150, 150))
        instruction_rect = instruction.get_rect(center=(VIEWPORT_WIDTH // 2, VIEWPORT_HEIGHT // 2 + 100))
        screen.blit(instruction, instruction_rect)
    
    return button_rect

def show_alert_message():
    global firewall_alert_time, show_alert
    
    # Update alert timer
    if show_alert:
        firewall_alert_time += clock.get_time() / 1000
        if firewall_alert_time >= alert_duration:
            firewall_alert_time = 0
            show_alert = False
            return
    
    # Create alert text with glitch effect
    glitched_alert = glitch_text('SYSTEM ALERT', 0.3)  # Higher intensity for more glitching
    alert_text = alert_font.render(glitched_alert, True, (255, 50, 0))
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
    # Calculate pulsing glow based on time
    title_pulse = math.sin(pygame.time.get_ticks() / 500) * 0.5 + 0.5  # Value between 0 and 1
    glow_size = int(10 + title_pulse * 5)
    glow_alpha = int(100 + title_pulse * 50)
    
    # Create title text with cyberpunk colors
    title_text = "CYBERPUNK HACKER DUEL"
    title_shadow = title_font.render(title_text, True, (WALL_COLOR[0], WALL_COLOR[1], WALL_COLOR[2], glow_alpha))
    title_glow = title_font.render(title_text, True, (SHARD_COLOR[0], SHARD_COLOR[1], SHARD_COLOR[2], glow_alpha))
    title_main = title_font.render(title_text, True, GRID_COLOR)
    
    # Position for title - ensure it's centered with margins
    title_x = VIEWPORT_WIDTH // 2
    title_y = 120
    
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
    
    subtitle_surf = subtitle_font.render(subtitle_text, True, SHARD_COLOR)
    subtitle_rect = subtitle_surf.get_rect(center=(title_x, title_y + 50))
    screen.blit(subtitle_surf, subtitle_rect)
    
    # Draw simplified instruction box
    instr_width, instr_height = 400, 165  # Increased height by 10% (from 150 to 165)
    instr_x = (VIEWPORT_WIDTH - instr_width) // 2
    instr_y = subtitle_rect.bottom + 50
    
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
    section_surf = section_font.render("MISSION", True, GRID_COLOR)
    section_rect = section_surf.get_rect(center=(instr_x + instr_width // 2, instr_y + 25))
    screen.blit(section_surf, section_rect)
    
    # Draw simplified instructions
    instructions = [
        "Reach the security node (red microchip)",
        "Use WASD/Arrows to move, Q for decoy",
        "Avoid the orange firewall",
        "E to disable walls (costs 5 data shards)",
        "Each level expands the digital world"
    ]
    
    y_offset = section_rect.bottom + 10
    
    for i, line in enumerate(instructions):
        # Make the last line about expanding world more prominent
        if i == len(instructions) - 1:
            text_surf = text_font.render(line, True, (180, 180, 255))  # Bluish color for emphasis
        else:
            text_surf = text_font.render(line, True, (200, 200, 200))
        text_rect = text_surf.get_rect(center=(instr_x + instr_width // 2, y_offset))
        screen.blit(text_surf, text_rect)
        y_offset += 25
    
    # Draw clickable start button (adjusted position due to taller instruction box)
    button_width, button_height = 200, 50
    button_x = (VIEWPORT_WIDTH - button_width) // 2
    button_y = instr_y + instr_height + 80
    
    button_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
    
    # Change button color based on mouse hover
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    button_color = (SHARD_COLOR[0], SHARD_COLOR[1], SHARD_COLOR[2], 150)
    button_hover = button_rect.collidepoint(mouse_pos)
    
    if button_hover:
        button_color = (SHARD_COLOR[0], SHARD_COLOR[1], SHARD_COLOR[2], 220)
    
    # Draw button background
    pygame.draw.rect(button_surf, button_color, (0, 0, button_width, button_height), border_radius=10)
    pygame.draw.rect(button_surf, (255, 255, 255, 100), (0, 0, button_width, button_height), 2, border_radius=10)
    
    # Draw button text
    button_text = button_font.render("START MISSION", True, (0, 0, 0) if button_hover else (255, 255, 255))
    button_text_rect = button_text.get_rect(center=(button_width//2, button_height//2))
    button_surf.blit(button_text, button_text_rect)
    
    # Draw the button
    screen.blit(button_surf, (button_x, button_y))
    
    # Occasionally add scanline effect
    if random.random() > 0.8:
        scanline_surf = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT), pygame.SRCALPHA)
        for y in range(0, VIEWPORT_HEIGHT, 4):
            pygame.draw.line(scanline_surf, (255, 255, 255, 15), (0, y), (VIEWPORT_WIDTH, y))
        screen.blit(scanline_surf, (0, 0))
    
    # Return the button rect for click detection
    return button_rect

def draw_decoy_tutorial():
    """Draw the tutorial explanation for the decoy visual indicator"""
    # Create semi-transparent overlay
    overlay = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Dark semi-transparent background
    screen.blit(overlay, (0, 0))
    
    # Create tutorial box with enough height for text and button
    box_width = 500
    box_height = 350  # Increased height to ensure space for text and button
    box_x = (VIEWPORT_WIDTH - box_width) // 2
    box_y = (VIEWPORT_HEIGHT - box_height) // 2 - 50  # Move up by 50 pixels
    
    # Draw glowing border
    pulse = (math.sin(pygame.time.get_ticks() / 500) * 0.3 + 0.7)
    border_color = (
        int(SHARD_COLOR[0] * pulse),
        int(SHARD_COLOR[1] * pulse),
        int(SHARD_COLOR[2] * pulse)
    )
    
    # Draw box with border
    box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    box_surface.fill((10, 15, 30, 230))  # Dark blue background
    pygame.draw.rect(box_surface, border_color, (0, 0, box_width, box_height), 2)
    
    # Add header
    header_text = title_font.render("DECOY SYSTEM", True, SHARD_COLOR)
    header_rect = header_text.get_rect(center=(box_width // 2, 40))
    box_surface.blit(header_text, header_rect)
    
    # Add explanation text
    tutorial_text = [
        "Your hacker avatar will change color to",
        "indicate DECOY readiness:",
        "",
        "BRIGHT BLUE GLOW = Decoy Ready",
        "DIMMED BLUE = Decoy Recharging",
        "",
        "The color will gradually brighten as",
        "your decoy recharges."
    ]
    
    # Start text higher in the box for more space
    y_offset = 90
    for line in tutorial_text:
        text_surf = text_font.render(line, True, (200, 200, 200))
        text_rect = text_surf.get_rect(center=(box_width // 2, y_offset))
        box_surface.blit(text_surf, text_rect)
        y_offset += 25
    
    # Define button dimensions
    button_width, button_height = 200, 40
    
    # Position button higher - reduce the gap between text and button from 30px to 10px
    button_rel_x = (box_width - button_width) // 2  # Centered horizontally
    button_rel_y = y_offset + 10  # Gap further reduced from 30px to 10px
    
    # Create button surface
    button_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
    
    # Calculate absolute screen position for collision detection
    button_abs_x = box_x + button_rel_x
    button_abs_y = box_y + button_rel_y
    
    # Create button rect for collision detection
    button_rect = pygame.Rect(button_abs_x, button_abs_y, button_width, button_height)
    
    # Check for mouse hover
    mouse_pos = pygame.mouse.get_pos()
    button_hover = button_rect.collidepoint(mouse_pos)
    
    # Use bright green button color to match data shard tutorial
    green_color = (0, 200, 0)  # Bright green base color
    
    # Set alpha based on hover state
    button_alpha = 255 if button_hover else 220
    
    # Apply button color with alpha
    button_color = (green_color[0], green_color[1], green_color[2], button_alpha)
    
    # Draw button background with green color
    pygame.draw.rect(button_surf, button_color, (0, 0, button_width, button_height), border_radius=5)
    pygame.draw.rect(button_surf, (255, 255, 255, 100), (0, 0, button_width, button_height), 1, border_radius=5)
    
    # Draw button text
    button_text = button_font.render("CONTINUE", True, (0, 0, 0) if button_hover else (255, 255, 255))
    button_text_rect = button_text.get_rect(center=(button_width//2, button_height//2))
    button_surf.blit(button_text, button_text_rect)
    
    # Add button to box surface at the proper relative position
    box_surface.blit(button_surf, (button_rel_x, button_rel_y))
    
    # Draw the box on screen
    screen.blit(box_surface, (box_x, box_y))
    
    return button_rect

def draw_shard_tutorial():
    """Draw the tutorial explanation for data shards"""
    # Create semi-transparent overlay
    overlay = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Dark semi-transparent background
    screen.blit(overlay, (0, 0))
    
    # Create tutorial box with same dimensions as decoy tutorial
    box_width = 500
    box_height = 350  # Match decoy tutorial box height
    box_x = (VIEWPORT_WIDTH - box_width) // 2
    box_y = (VIEWPORT_HEIGHT - box_height) // 2 - 50  # Same vertical offset as decoy tutorial
    
    # Draw glowing border
    pulse = (math.sin(pygame.time.get_ticks() / 500) * 0.3 + 0.7)
    border_color = (
        int(SHARD_COLOR[0] * pulse),
        int(SHARD_COLOR[1] * pulse),
        int(SHARD_COLOR[2] * pulse)
    )
    
    # Draw box with border - identical styling to decoy tutorial
    box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    box_surface.fill((10, 15, 30, 230))  # Dark blue background
    pygame.draw.rect(box_surface, border_color, (0, 0, box_width, box_height), 2)
    
    # Use score_font to match the score UI styling
    header_text = score_font.render("DATA SHARD SYSTEM", True, SHARD_COLOR)
    header_rect = header_text.get_rect(center=(box_width // 2, 40))
    box_surface.blit(header_text, header_rect)
    
    # Add explanation text - reduced and more concise
    tutorial_text = [
        "DATA SHARDS are valuable information packets",
        "scattered throughout the system.",
        "",
        "COLLECT 5 DATA SHARDS to unlock an upgrade",
        "for your DECOY system.",
        "",
        "Your current DATA count is displayed in the",
        "top-left corner of the screen."
    ]
    
    # Start text at same y-offset as decoy tutorial
    y_offset = 90
    for line in tutorial_text:
        text_surf = text_font.render(line, True, (200, 200, 200))
        text_rect = text_surf.get_rect(center=(box_width // 2, y_offset))
        box_surface.blit(text_surf, text_rect)
        y_offset += 25
    
    # Define button dimensions - identical to decoy tutorial
    button_width, button_height = 200, 40
    
    # Position button with same spacing from the text as decoy tutorial
    button_rel_x = (box_width - button_width) // 2  # Centered horizontally
    button_rel_y = y_offset + 10  # Same 10px gap as decoy tutorial
    
    # Create button surface
    button_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
    
    # Calculate absolute screen position for collision detection
    button_abs_x = box_x + button_rel_x
    button_abs_y = box_y + button_rel_y
    
    # Create button rect for collision detection
    button_rect = pygame.Rect(button_abs_x, button_abs_y, button_width, button_height)
    
    # Check for mouse hover
    mouse_pos = pygame.mouse.get_pos()
    button_hover = button_rect.collidepoint(mouse_pos)
    
    # Use bright green button color to match decoy tutorial
    # Using RGB values for green similar to what's shown in screenshots
    green_color = (0, 200, 0)  # Bright green base color
    
    # Set alpha based on hover state
    button_alpha = 255 if button_hover else 220
    
    # Apply button color with alpha
    button_color = (green_color[0], green_color[1], green_color[2], button_alpha)
    
    # Draw button background with bright green color
    pygame.draw.rect(button_surf, button_color, (0, 0, button_width, button_height), border_radius=5)
    pygame.draw.rect(button_surf, (255, 255, 255, 100), (0, 0, button_width, button_height), 1, border_radius=5)
    
    # Draw button text - identical to decoy tutorial
    button_text = button_font.render("CONTINUE", True, (0, 0, 0) if button_hover else (255, 255, 255))
    button_text_rect = button_text.get_rect(center=(button_width//2, button_height//2))
    button_surf.blit(button_text, button_text_rect)
    
    # Add button to box surface at the identical position as decoy tutorial
    box_surface.blit(button_surf, (button_rel_x, button_rel_y))
    
    # Draw the box on screen
    screen.blit(box_surface, (box_x, box_y))
    
    return button_rect

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
level_button_rect = None  # Store the continue button rect
tutorial_button_rect = None  # Store the tutorial continue button rect
shard_tutorial_button_rect = None  # Store the shard tutorial continue button rect

def glitch_text(text, intensity=0.1):
    """Apply a glitch effect to text by randomly replacing characters"""
    if random.random() > intensity:
        return text
    
    chars = list(text)
    glitch_count = max(1, int(len(chars) * intensity))
    for _ in range(glitch_count):
        idx = random.randint(0, len(chars) - 1)
        chars[idx] = random.choice(['#', '$', '%', '&', '*', '!', '@', '0', '1'])
    
    return ''.join(chars)

def reset_level(level):
    global current_level, player_x, player_y, player_speed, decoy_can_use, decoy_timer, decoy_active, player_dead
    global firewall_x, firewall_y, firewall_width, firewall_height, firewall_vertical_speed, firewall_active
    global walls, walls_visible, wall_timer, wall_timer_active, shard_storage_capacity, decoy_cooldown
    global score, prev_player_x, prev_player_y, WORLD_WIDTH, WORLD_HEIGHT, game_won, level_completed
    global node_x, node_y, scanner_active, scanner_radius, scanner_speed, scanner_flicker_intensity
    global SCANNER_COLOR, FIREWALL_COLOR, firewall_flicker_intensity, player_health, damage_cooldown
    
    # Reset game state
    current_level = level
    player_dead = False
    
    # Reset player health
    player_health = player_max_health
    damage_cooldown = 0
    
    # Reset completion states
    game_won = False  # Reset game won state for new level
    level_completed = False  # Reset level completion state
    
    # Scale world dimensions based on level
    scaling_factor = 1.0 + (level - 1) * 0.3  # Same formula used in win message
    WORLD_WIDTH = int(BASE_WORLD_WIDTH * scaling_factor)
    WORLD_HEIGHT = int(BASE_WORLD_HEIGHT * scaling_factor)
    
    # Reset player
    player_x = 200
    player_y = 300
    prev_player_x = player_x  # Initialize previous position
    prev_player_y = player_y
    
    # Reset dynamic game variables
    decoy_can_use = True
    decoy_timer = 0
    decoy_active = False
    scanner_active = False
    showing_upgrade = False
    
    # Reset wall variables - walls should be visible by default at level start
    walls_visible = True
    wall_timer_active = False
    wall_timer = 0
    
    # Keep data shards between levels
    data_shards = []
    
    # Set up level-specific settings
    # Add more shards for higher levels
    for _ in range(level * 3):
        spawn_data_shard()
    
    # Position security node on the right side of the world - ensure it's far enough for each level
    if level == 1:
        node_x = WORLD_WIDTH - 150
    elif level == 2:
        node_x = WORLD_WIDTH - 200  # Further right in level 2
    else:
        node_x = WORLD_WIDTH - 250  # Even further right in level 3
        
    node_y = WORLD_HEIGHT // 2
    
    # Level-specific firewall settings
    if level == 1:
        firewall_speed = 3  # Basic speed for level 1
        firewall_width = 8  # Thinner firewall at level 1
        firewall_height = 200  # Shorter firewall at level 1 - easy to dodge
        firewall_vertical_speed = 1  # Slow vertical movement
        firewall_flicker_intensity = 20  # Less flicker
        FIREWALL_COLOR = (255, 120, 0)  # Orange for level 1
        
        # No scanners in level 1
        scanner_active = False
        
    elif level == 2:
        firewall_speed = 4  # Faster firewall in level 2
        firewall_width = 10  # Medium width
        firewall_height = 300  # Medium height at level 2
        firewall_vertical_speed = 1.5  # Medium vertical movement
        firewall_flicker_intensity = 25  # Medium flicker
        FIREWALL_COLOR = (255, 80, 0)  # More intense orange-red for level 2
        
        # Level 2 scanner settings
        scanner_active = True  # Enable scanner for level 2
        scanner_radius = 4  # Smaller scanner
        scanner_speed = 4  # Slower scanner
        scanner_flicker_intensity = 20
        SCANNER_COLOR = (255, 255, 0)  # Yellow scanner for level 2
        
    else:  # Level 3+
        firewall_speed = 5  # Even faster in level 3
        firewall_width = 12  # Thicker firewall
        firewall_height = 400  # Taller firewall at level 3 - harder to dodge
        firewall_vertical_speed = 2  # Fast vertical movement
        firewall_flicker_intensity = 30  # Full flicker
        FIREWALL_COLOR = (255, 30, 0)  # Red for level 3 - more dangerous
        
        # Level 3 scanner settings - more advanced
        scanner_active = True  # Enable scanner for level 3
        scanner_radius = 5  # Larger scanner
        scanner_speed = 6  # Faster scanner
        scanner_flicker_intensity = 40
        SCANNER_COLOR = (255, 50, 50)  # Red scanner for level 3
    
    # Reset firewall position to left side of the screen
    firewall_x = -firewall_width  # Start off-screen
    firewall_y = random.randint(0, WORLD_HEIGHT - firewall_height)
    firewall_active = True
    
    # Spawn scanner if active
    if scanner_active:
        spawn_scanner()
    
    # Generate maze walls for the level
    generate_maze_walls()
    wall_alpha = 200  # Ensure walls are visible

def draw_hud():
    # Draw player health bar at top center
    health_bar_width = 250
    health_bar_height = 20
    health_bar_x = (VIEWPORT_WIDTH - health_bar_width) // 2
    health_bar_y = 15
    
    # Draw background
    pygame.draw.rect(screen, (50, 50, 50), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
    
    # Calculate health percentage
    health_percent = max(0, player_health / player_max_health)
    filled_width = int(health_bar_width * health_percent)
    
    # Use a nice shade of red for health bar
    health_color = (200, 30, 45)  # Rich red color
    
    # Draw health bar fill
    if filled_width > 0:
        pygame.draw.rect(screen, health_color, (health_bar_x, health_bar_y, filled_width, health_bar_height))
    
    # Draw border with cyberpunk style
    border_thickness = 2
    pygame.draw.rect(screen, (200, 200, 200), (health_bar_x - border_thickness, health_bar_y - border_thickness, 
                                             health_bar_width + border_thickness * 2, health_bar_height + border_thickness * 2), 
                    border_thickness)
    
    # Draw health text
    health_text = small_font.render(f"HP: {int(player_health)}/{player_max_health}", True, (255, 255, 255))
    health_text_rect = health_text.get_rect()
    health_text_rect.center = (health_bar_x + health_bar_width // 2, health_bar_y + health_bar_height // 2)
    screen.blit(health_text, health_text_rect)

    # Draw level text at top right using Pixel Game font
    level_text = score_font.render(f"LVL: {current_level}/{max_level}", True, (200, 200, 200))
    level_rect = level_text.get_rect()
    level_rect.right = VIEWPORT_WIDTH - 20
    level_rect.top = 20
    screen.blit(level_text, level_rect)
    
    # If AI is adapting (after 2 decoys), show warning
    if decoy_count >= 2:
        # Keep warning in small_font for contrast
        warning_text = small_font.render("AI ADAPTING", True, (255, 100, 0))
        warning_rect = warning_text.get_rect()
        warning_rect.right = VIEWPORT_WIDTH - 20
        warning_rect.top = level_rect.bottom + 5
        screen.blit(warning_text, warning_rect)
    
    # Draw wall timer if active
    if wall_timer_active:
        # Draw text timer with Pixel Game font
        timer_text = f"WALLS: {int(wall_hide_duration - wall_timer)}s"
        timer_color = (0, 255, 0)
        timer_surface = score_font.render(timer_text, True, timer_color)
        timer_rect = timer_surface.get_rect()
        timer_rect.right = VIEWPORT_WIDTH - 20
        
        # Adjust position based on whether warning is shown
        if decoy_count >= 2:
            timer_rect.top = warning_rect.bottom + 5
        else:
            timer_rect.top = level_rect.bottom + 5
            
        screen.blit(timer_surface, timer_rect)
        
        # Draw progress bar
        bar_width = 100
        bar_height = 8
        bar_x = timer_rect.left - 10
        bar_y = timer_rect.bottom + 5
        progress = 1.0 - (wall_timer / wall_hide_duration)
        
        # Draw background
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # Draw progress
        filled_width = int(bar_width * progress)
        if filled_width > 0:
            # Color changes from green to yellow to red as time runs out
            r = int(255 * (1 - progress))
            g = int(255 * progress)
            pygame.draw.rect(screen, (r, g, 0), (bar_x, bar_y, filled_width, bar_height))

def spawn_decoy_ready_particles():
    """Spawn particles that trail behind the player when decoy is ready"""
    global prev_player_x, prev_player_y
    
    if not decoy_can_use:
        return
    
    # Calculate player movement direction
    dx = player_x - prev_player_x
    dy = player_y - prev_player_y
    move_distance = math.sqrt(dx*dx + dy*dy)
    
    # Handle both moving and stationary player
    if move_distance < 0.5:  # If player is stationary or barely moving
        # Create particles in a circular pattern around the player
        angle = random.uniform(0, math.pi * 2)  # Random angle around player
        distance = random.uniform(3, 8)  # Random distance from player
        trail_x = player_x + math.cos(angle) * distance
        trail_y = player_y + math.sin(angle) * distance
    else:
        # Normalize direction vector for moving player
        dx /= move_distance
        dy /= move_distance
        
        # Spawn particles behind the player in the opposite direction of movement
        trail_x = player_x - dx * 5  # Position particles behind player
        trail_y = player_y - dy * 5
    
    # Spawn 1-3 particles
    count = random.randint(1, 2)
    for _ in range(count):
        # Add randomness to position
        offset_x = random.uniform(-5.0, 5.0)
        offset_y = random.uniform(-5.0, 5.0)
        
        # Particle size varies slightly
        size = random.uniform(2.0, 4.0)
        
        # Brief lifetime for trailing effect
        lifetime = random.uniform(0.3, 0.8)
        
        # Cyan/blue color matching the decoy ready effect with slight variation
        color_variation = random.uniform(-20, 20)
        color = (
            min(255, max(0, int(30 + color_variation))),  # Slight blue tint
            min(255, max(0, int(180 + color_variation))),  # Strong cyan
            min(255, max(0, int(220 + color_variation)))   # Bright blue
        )
        
        # Create particle with initial settings
        decoy_ready_particles.append({
            'x': trail_x + offset_x,
            'y': trail_y + offset_y,
            'size': size,
            'alpha': 180,  # Start fairly visible
            'color': color,
            'lifetime': lifetime,
            'age': 0
        })

def update_decoy_ready_particles():
    """Update all decoy-ready trailing particles"""
    global decoy_ready_particles, prev_player_x, prev_player_y
    
    # Only spawn particles if decoy is ready
    if decoy_can_use:
        # Calculate movement since last frame
        dx = player_x - prev_player_x
        dy = player_y - prev_player_y
        move_distance = math.sqrt(dx*dx + dy*dy)
        
        # Adjust spawn probability based on movement
        if move_distance < 0.5:  # Stationary or barely moving
            spawn_probability = 0.4  # Higher probability when stationary for more particles
        else:
            spawn_probability = 0.3  # Normal probability when moving
            
        # Spawn particles based on adjusted probability
        if random.random() < spawn_probability:
            spawn_decoy_ready_particles()
    
    # Store current position for next frame
    prev_player_x = player_x
    prev_player_y = player_y
    
    # Update existing particles
    for i in range(len(decoy_ready_particles) - 1, -1, -1):
        particle = decoy_ready_particles[i]
        
        # Update age
        particle['age'] += clock.get_time() / 1000
        
        # Remove old particles
        if particle['age'] >= particle['lifetime']:
            decoy_ready_particles.pop(i)
            continue
            
        # Calculate fade out as particle ages
        fade_ratio = particle['age'] / particle['lifetime']
        particle['alpha'] = int((1 - fade_ratio) * 180)  # Fade from 180 to 0
        
        # Also shrink slightly as they age
        particle['size'] *= (1 - 0.05 * fade_ratio)

def draw_decoy_ready_particles():
    """Draw all decoy-ready trailing particles"""
    if not decoy_can_use or len(decoy_ready_particles) == 0:
        return
        
    # Create a surface for all particles
    particle_surf = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT), pygame.SRCALPHA)
    
    for particle in decoy_ready_particles:
        # Skip if fully transparent
        if particle['alpha'] <= 0:
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
        # First draw glow
        glow_size = particle['size'] * 2
        glow_alpha = particle['alpha'] // 3
        pygame.draw.circle(
            particle_surf,
            (*particle['color'], glow_alpha),
            (int(screen_x + offset_x), int(screen_y + offset_y)),
            glow_size
        )
        
        # Then draw main particle
        pygame.draw.circle(
            particle_surf,
            (*particle['color'], particle['alpha']),
            (int(screen_x + offset_x), int(screen_y + offset_y)),
            particle['size']
        )
    
    # Draw all particles at once
    screen.blit(particle_surf, (0, 0))

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and game_won and current_level >= max_level:
                running = False
            # Space to start game from the start screen
            elif event.key == pygame.K_SPACE and not game_started:
                game_started = True
                # Reset to level 1
                reset_level(1)
            # Q key to spawn decoy (only if game is started and not won)
            elif event.key == pygame.K_q and game_started and not game_won and not tutorial_active and not shard_tutorial_active:
                if decoy_can_use:
                    spawn_decoy()
            # E key to disable walls if enough data shards collected
            elif event.key == pygame.K_e and game_started and not game_won and not tutorial_active and not shard_tutorial_active:
                if player_score >= 5:
                    disable_walls()
        # Handle mouse clicks for the start button or level progression button
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                # Check for start button if not started
                if not game_started and button_rect.collidepoint(mouse_pos):
                    game_started = True
                    # Reset to level 1
                    reset_level(1)
                # Check for level progression button if level completed
                elif level_completed and level_button_rect and level_button_rect.collidepoint(mouse_pos):
                    # Progress to next level
                    reset_level(current_level + 1)
                # Check for tutorial continue button
                elif tutorial_active and tutorial_button_rect and tutorial_button_rect.collidepoint(mouse_pos):
                    tutorial_active = False
                    show_decoy_tutorial = False
                # Check for shard tutorial continue button
                elif shard_tutorial_active and shard_tutorial_button_rect and shard_tutorial_button_rect.collidepoint(mouse_pos):
                    shard_tutorial_active = False
    
    # Show start screen if game not started
    if not game_started:
        button_rect = draw_start_screen()
        pygame.display.flip()
        clock.tick(FPS)
        continue
    
    # If tutorial is active, pause the game and show tutorial
    if tutorial_active:
        tutorial_button_rect = draw_decoy_tutorial()
        pygame.display.flip()
        clock.tick(FPS)
        continue
    
    # If shard tutorial is active, pause the game and show tutorial
    if shard_tutorial_active:
        shard_tutorial_button_rect = draw_shard_tutorial()
        pygame.display.flip()
        clock.tick(FPS)
        continue
    
    # Main game logic (only runs if game has started)
    # Get pressed keys for player movement (only if game not won)
    if not game_won:
        keys = pygame.key.get_pressed()
        
        # Store original position
        original_x, original_y = player_x, player_y
        
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
            
        # Try diagonal movement if both horizontal and vertical movement failed
        # This allows sliding along walls instead of getting stuck
        if player_x == original_x and player_y == original_y and (new_x != original_x or new_y != original_y):
            # Try to move diagonally at least in one direction - half speed sliding
            if not check_wall_collision(new_x, player_y + (new_y - player_y) * 0.5):
                player_y += (new_y - player_y) * 0.5
            if not check_wall_collision(player_x + (new_x - player_x) * 0.5, new_y):
                player_x += (new_x - player_x) * 0.5
    
    # Update camera position to follow player
    update_camera()
    
    # Update damage cooldown timer
    if damage_cooldown > 0:
        damage_cooldown -= clock.get_time() / 1000  # Subtract elapsed time in seconds
    
    # Check if player is dead and handle it
    if player_health <= 0 and not player_dead:
        player_dead = True
        reset_player_position()  # Reset position
        player_health = player_max_health  # Refill health
        
        # Visual/Audio feedback
        if sound_enabled:
            impact_sound.play()
        trigger_screen_shake(0.7, 15)  # Strong shake effect
    
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
    
    # Update decoy-ready particles
    update_decoy_ready_particles()
    
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
    
    # Draw decoy-ready particle trails
    draw_decoy_ready_particles()
    
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
    
    # Draw HUD with level info, world size and wall timer
    draw_hud()
    
    # Draw upgrade message if active
    if showing_upgrade:
        show_upgrade_message()
    
    # Check collision with security node
    if not game_won and check_node_collision():
        game_won = True
        # Make level completion more obvious
        if sound_enabled:
            collect_sound.play()
        trigger_screen_shake(0.5, 10)
    
    # Check collision with firewall only if game isn't won
    if not game_won and check_firewall_collision():
        reset_player_position()
    
    # Show win message if game is won
    if game_won:
        level_button_rect = show_win_message()
    else:
        level_button_rect = None
    
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
