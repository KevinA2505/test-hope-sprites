# Hope Sprite Demo

This small demo uses Pygame to animate the sprite sheets found in `assets/img`.
The latest version separates the game logic into several classes and includes a
larger scrolling world.

## Requirements
- Python 3
- Pygame
- Pillow

Install dependencies:
```bash
pip install pygame pillow
```

Run the game:
```bash
python game.py
```

Controls:
- `A`/`D` or Left/Right arrows to move
- `Left Shift` to toggle crouch
- `Space`, `W` or Up arrow to jump
  - Jumping while crouched gives a higher leap
```
