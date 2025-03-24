# Cyberpunk Hacker Duel

A cyberpunk-themed hacker infiltration game built with Pygame where you navigate a maze-like environment, avoiding firewalls, deploying decoys, disabling walls by spending data shards, and reaching security nodes to progress through levels.

## Features

- **Cyberpunk Visual Design**: Flickering green gridlines with dynamic lighting and ambiance
- **Sleek Character Design**: Angular player character with responsive blue glow effects
- **Maze Navigation**: Navigate through a maze with strategically placed walls
- **Wall Disabling System**: Temporarily disable walls by spending collected data shards
- **Adaptive AI**: Security system that evolves and responds to player actions
- **Visual Feedback System**: Color-coded player states indicate ability readiness
- **Interactive Tutorials**: Guided instructions for game mechanics with pause functionality
- **Progression System**: Multiple levels with increasing difficulty
- **Resource Management**: Strategic collection and use of data shards
- **Immersive Effects**: Screen shake, particle systems, and glitch effects
- **Polished UI**: Cyberpunk-styled interface with intuitive visual cues

## Controls

- **WASD or Arrow Keys**: Move your character
- **Q**: Deploy decoy (draws security systems away from you)
- **E**: Disable walls (costs 5 data shards, lasts for 15 seconds)
- **Space**: Start game (on title screen)
- **ESC**: Exit game (when completed)
- **Mouse**: Click buttons in UI

## Game Elements

- **Player Avatar**: Blue angular shape with dynamic glowing effects
- **Security Node**: Pulsing red circle (your objective)
- **Firewall**: Orange vertical line that pursues the player or decoy
- **Data Shards**: Cyan triangular collectibles that enable upgrades
- **Scanner**: Yellow tracking device that appears after multiple decoy uses
- **Decoy System**: Blue hologram that attracts security systems
  - **Visual Indicator**: Player color brightness indicates decoy readiness
- **Maze Walls**: Purple obstacles that can be temporarily disabled by spending data shards

## Tutorial System

The game features two tutorial popups that help new players:

1. **Decoy Tutorial**: Appears on first decoy use, explaining the color-coded visual feedback system
2. **Data Shard Tutorial**: Appears on first shard collection, explaining the upgrade system

## Level Progression

- **Level 1**: Introduction to core mechanics with moderate difficulty
- **Level 2**: Increased challenge with faster firewalls
- **Level 3**: Maximum difficulty with even faster threats
- Additional levels can be added by modifying the game code

## Sound Setup

The game looks for sound files in the `sounds` directory:

1. `ambient_hum.wav`: Background cyberpunk ambience
2. `impact.wav`: Collision with firewall
3. `collect.wav`: Data shard collection

If these files are missing, the game will run without sound. To add sounds:

1. Download free cyberpunk/sci-fi sound effects (.wav format)
2. Name them as listed above and place them in the `sounds` folder
3. Recommended sources: Freesound.org, OpenGameArt.org

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