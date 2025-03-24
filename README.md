# Cyberpunk Hacker Duel

A cyberpunk-themed hacker infiltration game built with Pygame where you navigate a maze-like environment, avoiding firewalls, deploying decoys, disabling walls by spending data shards, and reaching security nodes to progress through levels.

## Features

- **Cyberpunk Visual Design**: Flickering green gridlines with dynamic lighting and ambiance
- **Sleek Character Design**: Angular player character with responsive blue glow effects
- **Maze Navigation**: Navigate through a maze with strategically placed walls
- **Wall Disabling System**: Temporarily disable walls by spending collected data shards
- **Player Health System**: Health bar with damage from firewalls and walls, with visual feedback
- **Adaptive AI**: Security system that evolves and responds to player actions
- **Visual Feedback System**: Color-coded player states indicate ability readiness with particle effects
- **Interactive Tutorials**: Guided instructions for game mechanics with pause functionality
- **Progression System**: Multiple levels with increasing difficulty and expanding world size
- **Resource Management**: Strategic collection and use of data shards
- **Immersive Effects**: Screen shake, particle systems, and glitch effects
- **Polished UI**: Cyberpunk-styled interface with intuitive visual cues
- **Firewall Attraction**: Advanced firewall behavior that responds to decoy placement in both vertical and horizontal directions

## Recent Updates

- **Player Health System**: Added a health system with a stylish red health bar and damage from obstacles
- **Enhanced Decoy Indicator**: Decoy readiness now displays particle effects even when the player is stationary
- **Security Node Redesign**: Changed from pulsing red circle to a more thematic red microchip design
- **Improved Level Progression**: Fixed level scaling with proper world size expansion between levels
- **Enhanced Firewall AI**: Improved the firewall's attraction to decoys with better vertical and horizontal tracking
- **Player Collision Refinement**: Better collision detection to prevent snagging on walls
- **Visual Feedback Enhancements**: More responsive particle effects to indicate ability states

## Controls

- **WASD or Arrow Keys**: Move your character
- **Q**: Deploy decoy (draws security systems away from you)
- **E**: Disable walls (costs 5 data shards, lasts for 15 seconds)
- **Space**: Start game (on title screen)
- **ESC**: Exit game (when completed)
- **Mouse**: Click buttons in UI

## Game Elements

- **Player Avatar**: Blue angular shape with dynamic glowing effects
- **Security Node**: Red microchip (your objective) with pulsing effect
- **Firewall**: Orange vertical line that pursues the player or decoy
- **Data Shards**: Cyan triangular collectibles that enable upgrades
- **Scanner**: Yellow tracking device that appears after multiple decoy uses
- **Decoy System**: Blue hologram that attracts security systems
  - **Visual Indicator**: Player color brightness and particle effects indicate decoy readiness
- **Maze Walls**: Purple obstacles that can be temporarily disabled by spending data shards

## Tutorial System

The game features two tutorial popups that help new players:

1. **Decoy Tutorial**: Appears on first decoy use, explaining the color-coded visual feedback system
2. **Data Shard Tutorial**: Appears on first shard collection, explaining the upgrade system

## Level Progression

- **Level 1**: Introduction to core mechanics with moderate difficulty
- **Level 2**: Increased challenge with faster firewalls, expanded world, and tracker introduction
- **Level 3**: Maximum difficulty with even faster threats and more aggressive AI
- Each level increases world size and security system complexity

## Game Mechanics Detail

### Player Health System
The player health system adds a survival element to the game:
- Red health bar displayed at the top center of the screen
- Player takes 5 damage points when colliding with firewalls
- Player takes 1 damage point when colliding with maze walls
- Visual feedback with red flashing effect when taking damage
- Brief invulnerability period after taking damage
- Death and position reset when health reaches zero

### Decoy System
The decoy system allows players to create a distraction that attracts the firewall. The decoy:
- Is indicated by blue particle effects around the player (now visible even when standing still)
- Has a cooldown period after use
- Becomes increasingly vital in higher levels as security systems become more aggressive

### Firewall Behavior
The firewall pursues the player or decoy with:
- Horizontal movement that accelerates based on distance
- Vertical tracking that adapts to the decoy's position
- Level-based attraction multiplier that increases with difficulty
- Natural-looking movement patterns with slight randomization

### World Scaling
As players progress through levels:
- The world expands in size, making navigation more challenging
- Security node positions adjust to maintain fair gameplay
- Maze walls become more complex and strategically placed

## Sound Setup

The game looks for sound files in the `sounds` directory:

1. `ambient_hum.wav`: Background cyberpunk ambience
2. `impact.wav`: Collision with firewall
3. `collect.wav`: Data shard collection

If these files are missing, the game will run without sound. To add sounds:

1. Download free cyberpunk/sci-fi sound effects (.wav format)
2. Name them as listed above and place them in the `sounds` folder
3. Recommended sources: Freesound.org, OpenGameArt.org

The repository includes `create_collect_sound.py`, a utility script that can generate a custom collect sound using numpy and scipy.

## Custom Fonts

The game uses a variety of cyberpunk-styled fonts located in the `assets/fonts` directory. If custom fonts are unavailable, the game will fall back to system fonts.

## Requirements

- Python 3.x
- Pygame library

## Installation

1. Ensure you have Python installed on your system.
2. Install Pygame using pip:

```
pip install pygame
```

3. Optional: Install numpy and scipy to use the sound creation utility:

```
pip install numpy scipy
```

## How to Run

Run the game by executing:

```
python cyberpunk_hacker.py
```

## Game Development

This game demonstrates several game development concepts:

- **State Management**: Game progression through different levels and states
- **Visual Feedback**: Using color and effects to communicate game state
- **Dynamic Difficulty**: Adaptive AI that responds to player tactics
- **Tutorial Integration**: Non-intrusive learning mechanics
- **Resource Management**: Strategic use of data shards to disable obstacles
- **Immersive Design**: Consistent aesthetic with atmospheric effects 
- **Level Scaling**: Progressive difficulty through world expansion and AI enhancement

## Contributing

Feel free to fork this repository and submit pull requests for enhancements or bug fixes. Some potential areas for contribution:

- Additional levels with unique challenges
- New enemy types with different behaviors
- Power-up systems beyond the current mechanics
- Visual and audio enhancements
- Performance optimizations 