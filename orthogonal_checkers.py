#!/usr/bin/env python3
"""
Nine Square - A two-player turn-based strategy game
Author: klemtek
Description: Players move units on an 8x8 board with the goal of reaching the opponent's home area.
             Supports simple moves and jumping with chaining. No diagonal movement.
"""

import pygame
import sys
from typing import List, Tuple, Optional, Set

# Constants
BOARD_SIZE = 8
SQUARE_SIZE = 80
BOARD_WIDTH = BOARD_SIZE * SQUARE_SIZE  # 640 pixels
BOARD_HEIGHT = BOARD_SIZE * SQUARE_SIZE  # 640 pixels
FOOTER_HEIGHT = 50
WINDOW_WIDTH = BOARD_WIDTH
WINDOW_HEIGHT = BOARD_HEIGHT + FOOTER_HEIGHT

# End Turn button constants
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 35
BUTTON_X = WINDOW_WIDTH - BUTTON_WIDTH - 10
BUTTON_Y = BOARD_HEIGHT + 7

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 20, 20)
BLUE = (20, 20, 220)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BUTTON_COLOR = (60, 60, 60)
BUTTON_HOVER = (80, 80, 80)

# Unit representation
EMPTY = None
PLAYER1 = 'P1'
PLAYER2 = 'P2'

class NineSquare:
    """Main game class for Nine Square"""
    
    def __init__(self):
        """Initialize the game"""
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Nine Square")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 24)
        
        # Game state
        self.board = self._initialize_board()
        self.current_player = PLAYER1
        self.selected_unit = None  # (row, col) of selected unit
        self.possible_moves = set()  # Set of (row, col) tuples for valid moves
        self.possible_jumps = set()  # Set of (row, col) tuples for valid jumps
        self.game_over = False
        self.winner = None
        self.in_jump_sequence = False  # True when player is in middle of chained jumps
        self.button_hovered = False  # Track if End Turn button is hovered
        
    def _initialize_board(self) -> List[List[Optional[str]]]:
        """Initialize the 8x8 board with starting positions"""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        # Player 1 (red) starts in top-left 3x3
        for row in range(3):
            for col in range(3):
                board[row][col] = PLAYER1
                
        # Player 2 (blue) starts in bottom-right 3x3
        for row in range(5, 8):
            for col in range(5, 8):
                board[row][col] = PLAYER2
                
        return board
    
    def _is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within board bounds"""
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE
    
    def _get_simple_moves(self, row: int, col: int) -> Set[Tuple[int, int]]:
        """Get all valid simple moves (one square orthogonally) for a unit"""
        moves = set()
        # Orthogonal directions: north, south, east, west
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (self._is_valid_position(new_row, new_col) and 
                self.board[new_row][new_col] == EMPTY):
                moves.add((new_row, new_col))
                
        return moves
    
    def _get_jump_moves(self, row: int, col: int) -> Set[Tuple[int, int]]:
        """Get all valid jump moves for a unit"""
        jumps = set()
        player = self.board[row][col]
        
        # Orthogonal directions: north, south, east, west
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        
        for dr, dc in directions:
            # Check adjacent square for any piece (opponent OR own piece)
            adj_row, adj_col = row + dr, col + dc
            if (self._is_valid_position(adj_row, adj_col) and 
                self.board[adj_row][adj_col] is not None):  # Any piece, not just opponent
                
                # Check landing square (beyond the piece)
                land_row, land_col = adj_row + dr, adj_col + dc
                if (self._is_valid_position(land_row, land_col) and 
                    self.board[land_row][land_col] == EMPTY):
                    jumps.add((land_row, land_col))
                    
        return jumps
    
    def _is_in_home_area(self, row: int, col: int, player: str) -> bool:
        """Check if position is in the specified player's target home area"""
        if player == PLAYER1:
            # Player 1's target is bottom-right 3x3
            return 5 <= row <= 7 and 5 <= col <= 7
        else:
            # Player 2's target is top-left 3x3
            return 0 <= row <= 2 and 0 <= col <= 2
    
    def _check_win_condition(self) -> Optional[str]:
        """Check if any player has won"""
        p1_units = []
        p2_units = []
        
        # Count units and their positions
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == PLAYER1:
                    p1_units.append((row, col))
                elif self.board[row][col] == PLAYER2:
                    p2_units.append((row, col))
        
        # Check if all units are in opponent's home area
        p1_all_in_target = all(self._is_in_home_area(row, col, PLAYER1) for row, col in p1_units)
        p2_all_in_target = all(self._is_in_home_area(row, col, PLAYER2) for row, col in p2_units)
        
        if p1_all_in_target:
            return PLAYER1
        if p2_all_in_target:
            return PLAYER2
            
        return None
    
    def _perform_jump(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Perform a jump move without removing the jumped unit"""
        # Move the unit (jumped piece stays on the board)
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = EMPTY
        
        # Note: We DO NOT remove the jumped unit - it stays on the board
        return True
    
    def _perform_simple_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Perform a simple move"""
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = EMPTY
        return True
    
    def _is_point_in_button(self, pos: Tuple[int, int]) -> bool:
        """Check if a point is inside the End Turn button"""
        x, y = pos
        return (BUTTON_X <= x <= BUTTON_X + BUTTON_WIDTH and 
                BUTTON_Y <= y <= BUTTON_Y + BUTTON_HEIGHT)
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> None:
        """Handle mouse click events"""
        if self.game_over:
            return
        
        # Check if End Turn button was clicked during jump sequence
        if self.in_jump_sequence and self._is_point_in_button(mouse_pos):
            self._end_turn()
            return
            
        # Convert mouse position to board coordinates
        col = mouse_pos[0] // SQUARE_SIZE
        row = mouse_pos[1] // SQUARE_SIZE
        
        # Check if click is within board
        if not self._is_valid_position(row, col):
            return
            
        # If no unit is selected, try to select one
        if self.selected_unit is None:
            if self.board[row][col] == self.current_player:
                self.selected_unit = (row, col)
                self.possible_moves = self._get_simple_moves(row, col)
                self.possible_jumps = self._get_jump_moves(row, col)
        else:
            # Unit is selected, try to move
            selected_row, selected_col = self.selected_unit
            target_pos = (row, col)
            
            # Check if clicking on same unit (deselect)
            if target_pos == self.selected_unit:
                self._deselect_unit()
                return
            
            # Check if target is a valid jump
            if target_pos in self.possible_jumps:
                self._perform_jump(selected_row, selected_col, row, col)
                
                # Check for additional jumps from new position
                new_jumps = self._get_jump_moves(row, col)
                if new_jumps:
                    # Continue jump sequence
                    self.in_jump_sequence = True
                    self.selected_unit = (row, col)
                    self.possible_moves = set()  # No simple moves during jump sequence
                    self.possible_jumps = new_jumps
                else:
                    # End turn
                    self._end_turn()
                    
            # Check if target is a valid simple move (only if not in jump sequence)
            elif target_pos in self.possible_moves and not self.in_jump_sequence:
                self._perform_simple_move(selected_row, selected_col, row, col)
                self._end_turn()
                
            # Check if clicking on own unit (switch selection)
            elif self.board[row][col] == self.current_player and not self.in_jump_sequence:
                self.selected_unit = (row, col)
                self.possible_moves = self._get_simple_moves(row, col)
                self.possible_jumps = self._get_jump_moves(row, col)
                
            # Invalid move, deselect if not in jump sequence
            elif not self.in_jump_sequence:
                self._deselect_unit()
    
    def handle_mouse_motion(self, mouse_pos: Tuple[int, int]) -> None:
        """Handle mouse motion for button hover effects"""
        if self.in_jump_sequence:
            self.button_hovered = self._is_point_in_button(mouse_pos)
    
    def _deselect_unit(self) -> None:
        """Deselect current unit and clear possible moves"""
        self.selected_unit = None
        self.possible_moves = set()
        self.possible_jumps = set()
        self.in_jump_sequence = False
    
    def _end_turn(self) -> None:
        """End current player's turn and switch to other player"""
        self._deselect_unit()
        
        # Check for win condition
        winner = self._check_win_condition()
        if winner:
            self.game_over = True
            self.winner = winner
        else:
            # Switch players
            self.current_player = PLAYER2 if self.current_player == PLAYER1 else PLAYER1
    
    def draw_board(self) -> None:
        """Draw the checkerboard"""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                # Calculate square position
                x = col * SQUARE_SIZE
                y = row * SQUARE_SIZE
                
                # Alternate colors for checkerboard
                color = WHITE if (row + col) % 2 == 0 else BLACK
                pygame.draw.rect(self.screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
                
                # Draw highlights for selected unit and possible moves
                if self.selected_unit == (row, col):
                    # Yellow border for selected unit
                    pygame.draw.rect(self.screen, YELLOW, (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)
                elif (row, col) in self.possible_moves or (row, col) in self.possible_jumps:
                    # Green border for possible moves
                    pygame.draw.rect(self.screen, GREEN, (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)
    
    def draw_units(self) -> None:
        """Draw all units on the board"""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                unit = self.board[row][col]
                if unit is not None:
                    # Calculate center of square
                    center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                    center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
                    
                    # Choose color based on player
                    color = RED if unit == PLAYER1 else BLUE
                    
                    # Draw circle
                    pygame.draw.circle(self.screen, color, (center_x, center_y), 30)
                    # Add white border for visibility
                    pygame.draw.circle(self.screen, WHITE, (center_x, center_y), 30, 2)
    
    def draw_end_turn_button(self) -> None:
        """Draw the End Turn button when in jump sequence"""
        if not self.in_jump_sequence:
            return
            
        # Button color changes on hover
        button_color = BUTTON_HOVER if self.button_hovered else BUTTON_COLOR
        
        # Draw button background
        button_rect = pygame.Rect(BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, button_color, button_rect)
        pygame.draw.rect(self.screen, WHITE, button_rect, 2)  # White border
        
        # Draw button text
        text = "End Turn"
        text_surface = self.button_font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def draw_footer(self) -> None:
        """Draw the footer with game status"""
        # Footer background
        footer_rect = pygame.Rect(0, BOARD_HEIGHT, WINDOW_WIDTH, FOOTER_HEIGHT)
        pygame.draw.rect(self.screen, BLACK, footer_rect)
        
        # Status text
        if self.game_over:
            if self.winner:
                winner_color = 'Red' if self.winner == PLAYER1 else 'Blue'
                text = f"{winner_color} Wins!"
            else:
                text = "Game Over"
        else:
            player_color = 'Red' if self.current_player == PLAYER1 else 'Blue'
            if self.in_jump_sequence:
                text = f"{player_color} Turn - Continue Jumping or End Turn"
            else:
                text = f"{player_color} Turn"
        
        # Render and center text (adjust position if button is showing)
        text_surface = self.font.render(text, True, WHITE)
        if self.in_jump_sequence:
            # Position text to the left when button is showing
            text_x = 20
            text_y = BOARD_HEIGHT + FOOTER_HEIGHT // 2
            text_rect = text_surface.get_rect(left=text_x, centery=text_y)
        else:
            # Center text when no button
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, BOARD_HEIGHT + FOOTER_HEIGHT // 2))
        
        self.screen.blit(text_surface, text_rect)
    
    def draw(self) -> None:
        """Draw the entire game"""
        self.screen.fill(BLACK)
        self.draw_board()
        self.draw_units()
        self.draw_footer()
        self.draw_end_turn_button()
        pygame.display.flip()
    
    def run(self) -> None:
        """Main game loop"""
        running = True
        win_time = None
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        self.handle_click(event.pos)
                        
                        # Start win timer if game just ended
                        if self.game_over and win_time is None:
                            win_time = pygame.time.get_ticks()
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event.pos)
            
            # Exit after 3 seconds when game is over
            if self.game_over and win_time is not None:
                if pygame.time.get_ticks() - win_time >= 3000:  # 3 seconds
                    running = False
            
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

def main():
    """Main function to start the game"""
    game = NineSquare()
    game.run()

if __name__ == "__main__":
    main() 