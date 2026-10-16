# Snake Game - Power Ups Edition

A modern and visually improved classic Snake game built with **Python** and **Pygame**.

## Features

- Smooth and clean modern graphics
- **Golden Food** (higher score)
- **Power-ups**:
  - Slow Motion (blue)
  - Ghost Mode – pass through walls and yourself (purple)
- Moving obstacles (orange walls)
- Progressive speed increase
- High score saving
- Countdown at the start
- WASD + Arrow keys support

## Requirements

- Python 3.8+
- pygame
- numpy

Install dependencies:

```bash
pip install pygame numpy
```

## How to Run

```bash
python snake.py
```

## Controls

| Key | Action |
|---------|------------------|
| Arrow Keys / WASD | Move the snake |
| R | Restart after Game Over |

## Game Elements

| Element | Description |
|-------------------|------------------------------------------|
| Red Food | +10 points |
| Golden Food | +30 points |
| Blue Orb | Slow Motion power-up |
| Purple Orb | Ghost Mode (pass through walls/body) |
| Orange Blocks | Moving walls (deadly) |

## Project Structure

```
snake-game/
├── snake.py          # Main game file
├── highscore.txt     # Saved high score (auto-generated)
└── README.md
```

## Author

Made with ❤️ using Python & Pygame
