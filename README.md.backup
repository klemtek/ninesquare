# NineSquare

A two-player turn-based strategy game implemented in Python using Pygame. Players compete to move all their units into the opponent's home area on an 8x8 checkerboard.

## Game Overview

**Nine Square** is a strategic board game where two players take turns moving their units across an 8x8 checkerboard. The goal is to move all your remaining units into your opponent's home area while potentially capturing their units through jumping.

### Key Features

- **8x8 Checkerboard**: Classic alternating black and white squares (640x640 pixels)
- **Two Players**: Player 1 (red circles) vs Player 2 (blue circles)
- **Strategic Movement**: Simple moves and jumping with chaining capabilities
- **Visual Interface**: Clear graphics with yellow selection highlights and green move indicators
- **Win Conditions**: Reach opponent's home area or eliminate all opponent units

## Game Rules

### Setup
- **Player 1 (Red)**: Starts with 9 units in the top-left 3x3 grid (positions 0,0 to 2,2)
- **Player 2 (Blue)**: Starts with 9 units in the bottom-right 3x3 grid (positions 5,5 to 7,7)
- **Goal**: Move all your units into the opponent's starting area

### Movement
1. **Simple Move**: Move one square orthogonally (north, south, east, west) to an empty adjacent square
2. **Jump**: Jump over any adjacent piece (opponent or your own) to an empty square beyond it
3. **Chain Jumps**: After a successful jump, if more jumps are available from the new position, continue jumping with the same unit

### Controls
- **Click** to select one of your units (highlighted with yellow border)
- **Click** a highlighted green square to move or jump
- **Click** the same unit again to deselect
- **Click** another of your units to switch selection
- **Click** "End Turn" button during jump sequences to voluntarily end your turn

### Win Conditions
- Move all your remaining units into the opponent's home area

## Installation & Setup

### Prerequisites
- Python 3.6 or higher
- pip (Python package installer)

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/klemtek/ninesquare.git
   cd ninesquare
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the game:
   ```bash
   python orthogonal_checkers.py
   ```

## Technical Details

### Game Architecture
- **NineSquare Class**: Main game controller handling state, logic, and rendering
- **Modular Design**: Separate methods for move validation, jump chaining, win detection, and drawing
- **Event-Driven**: Mouse click handling with position-to-board coordinate conversion

### Key Components
- **Board Representation**: 2D list with None (empty), 'P1' (Player 1), 'P2' (Player 2)
- **Move Validation**: Orthogonal-only movement with collision detection
- **Jump Logic**: Multi-jump sequences with automatic chaining capability
- **Visual Feedback**: Real-time highlighting of selected units and valid moves

### Constants
- Board: 8x8 grid, 80x80 pixel squares
- Window: 640x690 pixels (640x640 board + 50 pixel footer)
- Units: 30-pixel radius circles with white borders

## Development

### Code Structure
```
orthogonal_checkers.py    # Main game implementation
requirements.txt          # Python dependencies
README.md                # This file
```

### Key Methods
- `_get_simple_moves()`: Calculate valid single-square moves
- `_get_jump_moves()`: Calculate valid jump targets
- `handle_click()`: Process mouse input and game state changes
- `_check_win_condition()`: Determine game end conditions
- `draw()`: Render complete game state

## Contributing

This project is designed for educational purposes and game development learning. Feel free to fork, modify, and enhance the game!

### Potential Enhancements
- Add AI opponent
- Implement move history and undo functionality
- Add sound effects and animations
- Create different board sizes or rule variations
- Add network multiplayer support

## License

This project is open source. Feel free to use and modify as needed.

---

**Created by klemtek** | **Python + Pygame Implementation** 