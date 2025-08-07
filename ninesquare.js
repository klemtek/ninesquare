/**
 * Nine Square - Web Version
 * A two-player turn-based strategy game
 * Converted from Python/Pygame to JavaScript/HTML5 Canvas
 */

class NineSquare {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.gameInfo = document.getElementById('gameInfo');
        this.endTurnBtn = document.getElementById('endTurnBtn');
        
        // Constants
        this.BOARD_SIZE = 8;
        this.SQUARE_SIZE = 80;
        this.BOARD_WIDTH = this.BOARD_SIZE * this.SQUARE_SIZE;
        this.BOARD_HEIGHT = this.BOARD_SIZE * this.SQUARE_SIZE;
        
        // Colors
        this.BLACK = '#000000';
        this.WHITE = '#ffffff';
        this.RED = '#dc1414';
        this.BLUE = '#1414dc';
        this.YELLOW = '#ffff00';
        this.GREEN = '#00ff00';
        
        // Unit representation
        this.EMPTY = null;
        this.PLAYER1 = 'P1';
        this.PLAYER2 = 'P2';
        
        // Game state
        this.board = this.initializeBoard();
        this.currentPlayer = this.PLAYER1;
        this.selectedUnit = null;
        this.possibleMoves = new Set();
        this.possibleJumps = new Set();
        this.gameOver = false;
        this.winner = null;
        this.inJumpSequence = false;
        
        // Event listeners
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
        
        // Start the game
        this.draw();
    }
    
    initializeBoard() {
        const board = Array(this.BOARD_SIZE).fill(null).map(() => 
            Array(this.BOARD_SIZE).fill(this.EMPTY)
        );
        
        // Player 1 (red) starts in top-left 3x3
        for (let row = 0; row < 3; row++) {
            for (let col = 0; col < 3; col++) {
                board[row][col] = this.PLAYER1;
            }
        }
        
        // Player 2 (blue) starts in bottom-right 3x3
        for (let row = 5; row < 8; row++) {
            for (let col = 5; col < 8; col++) {
                board[row][col] = this.PLAYER2;
            }
        }
        
        return board;
    }
    
    isValidPosition(row, col) {
        return row >= 0 && row < this.BOARD_SIZE && col >= 0 && col < this.BOARD_SIZE;
    }
    
    getSimpleMoves(row, col) {
        const moves = new Set();
        const directions = [[-1, 0], [1, 0], [0, 1], [0, -1]]; // north, south, east, west
        
        for (const [dr, dc] of directions) {
            const newRow = row + dr;
            const newCol = col + dc;
            if (this.isValidPosition(newRow, newCol) && 
                this.board[newRow][newCol] === this.EMPTY) {
                moves.add(`${newRow},${newCol}`);
            }
        }
        
        return moves;
    }
    
    getJumpMoves(row, col) {
        const jumps = new Set();
        const directions = [[-1, 0], [1, 0], [0, 1], [0, -1]]; // north, south, east, west
        
        for (const [dr, dc] of directions) {
            // Check adjacent square for any piece
            const adjRow = row + dr;
            const adjCol = col + dc;
            if (this.isValidPosition(adjRow, adjCol) && 
                this.board[adjRow][adjCol] !== this.EMPTY) {
                
                // Check landing square (beyond the piece)
                const landRow = adjRow + dr;
                const landCol = adjCol + dc;
                if (this.isValidPosition(landRow, landCol) && 
                    this.board[landRow][landCol] === this.EMPTY) {
                    jumps.add(`${landRow},${landCol}`);
                }
            }
        }
        
        return jumps;
    }
    
    isInHomeArea(row, col, player) {
        if (player === this.PLAYER1) {
            // Player 1's target is bottom-right 3x3
            return row >= 5 && row <= 7 && col >= 5 && col <= 7;
        } else {
            // Player 2's target is top-left 3x3
            return row >= 0 && row <= 2 && col >= 0 && col <= 2;
        }
    }
    
    checkWinCondition() {
        const p1Units = [];
        const p2Units = [];
        
        // Count units and their positions
        for (let row = 0; row < this.BOARD_SIZE; row++) {
            for (let col = 0; col < this.BOARD_SIZE; col++) {
                if (this.board[row][col] === this.PLAYER1) {
                    p1Units.push([row, col]);
                } else if (this.board[row][col] === this.PLAYER2) {
                    p2Units.push([row, col]);
                }
            }
        }
        
        // Check if all units are in opponent's home area
        const p1AllInTarget = p1Units.every(([row, col]) => 
            this.isInHomeArea(row, col, this.PLAYER1)
        );
        const p2AllInTarget = p2Units.every(([row, col]) => 
            this.isInHomeArea(row, col, this.PLAYER2)
        );
        
        if (p1AllInTarget) return this.PLAYER1;
        if (p2AllInTarget) return this.PLAYER2;
        
        return null;
    }
    
    performJump(fromRow, fromCol, toRow, toCol) {
        // Move the unit (jumped piece stays on the board)
        this.board[toRow][toCol] = this.board[fromRow][fromCol];
        this.board[fromRow][fromCol] = this.EMPTY;
        return true;
    }
    
    performSimpleMove(fromRow, fromCol, toRow, toCol) {
        this.board[toRow][toCol] = this.board[fromRow][fromCol];
        this.board[fromRow][fromCol] = this.EMPTY;
        return true;
    }
    
    handleClick(event) {
        if (this.gameOver) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const col = Math.floor(x / this.SQUARE_SIZE);
        const row = Math.floor(y / this.SQUARE_SIZE);
        
        if (!this.isValidPosition(row, col)) return;
        
        // If no unit is selected, try to select one
        if (this.selectedUnit === null) {
            if (this.board[row][col] === this.currentPlayer) {
                this.selectedUnit = [row, col];
                this.possibleMoves = this.getSimpleMoves(row, col);
                this.possibleJumps = this.getJumpMoves(row, col);
                this.draw();
            }
        } else {
            // Unit is selected, try to move
            const [selectedRow, selectedCol] = this.selectedUnit;
            const targetPos = `${row},${col}`;
            
            // Check if clicking on same unit (deselect)
            if (row === selectedRow && col === selectedCol) {
                this.deselectUnit();
                return;
            }
            
            // Check if target is a valid jump
            if (this.possibleJumps.has(targetPos)) {
                this.performJump(selectedRow, selectedCol, row, col);
                
                // Check for additional jumps from new position
                const newJumps = this.getJumpMoves(row, col);
                if (newJumps.size > 0) {
                    // Continue jump sequence
                    this.inJumpSequence = true;
                    this.selectedUnit = [row, col];
                    this.possibleMoves = new Set(); // No simple moves during jump sequence
                    this.possibleJumps = newJumps;
                    this.updateEndTurnButton();
                } else {
                    // End turn
                    this.endTurnInternal();
                }
                
            // Check if target is a valid simple move (only if not in jump sequence)
            } else if (this.possibleMoves.has(targetPos) && !this.inJumpSequence) {
                this.performSimpleMove(selectedRow, selectedCol, row, col);
                this.endTurnInternal();
                
            // Check if clicking on own unit (switch selection)
            } else if (this.board[row][col] === this.currentPlayer && !this.inJumpSequence) {
                this.selectedUnit = [row, col];
                this.possibleMoves = this.getSimpleMoves(row, col);
                this.possibleJumps = this.getJumpMoves(row, col);
                
            // Invalid move, deselect if not in jump sequence
            } else if (!this.inJumpSequence) {
                this.deselectUnit();
            }
            
            this.draw();
        }
    }
    
    deselectUnit() {
        this.selectedUnit = null;
        this.possibleMoves = new Set();
        this.possibleJumps = new Set();
        this.inJumpSequence = false;
        this.updateEndTurnButton();
        this.draw();
    }
    
    endTurn() {
        if (this.inJumpSequence) {
            this.endTurnInternal();
        }
    }
    
    endTurnInternal() {
        this.deselectUnit();
        
        // Check for win condition
        const winner = this.checkWinCondition();
        if (winner) {
            this.gameOver = true;
            this.winner = winner;
            setTimeout(() => {
                alert(`${winner === this.PLAYER1 ? 'Red' : 'Blue'} Wins!`);
            }, 100);
        } else {
            // Switch players
            this.currentPlayer = this.currentPlayer === this.PLAYER1 ? this.PLAYER2 : this.PLAYER1;
        }
        
        this.updateGameInfo();
        this.draw();
    }
    
    updateEndTurnButton() {
        this.endTurnBtn.style.display = this.inJumpSequence ? 'block' : 'none';
    }
    
    updateGameInfo() {
        if (this.gameOver) {
            if (this.winner) {
                const winnerColor = this.winner === this.PLAYER1 ? 'Red' : 'Blue';
                this.gameInfo.innerHTML = `<span class="${winnerColor.toLowerCase()}-text">${winnerColor} Wins!</span>`;
            } else {
                this.gameInfo.textContent = "Game Over";
            }
        } else {
            const playerColor = this.currentPlayer === this.PLAYER1 ? 'Red' : 'Blue';
            if (this.inJumpSequence) {
                this.gameInfo.innerHTML = `<span class="${playerColor.toLowerCase()}-text">${playerColor} Turn - Continue Jumping</span>`;
            } else {
                this.gameInfo.innerHTML = `<span class="${playerColor.toLowerCase()}-text">${playerColor} Turn</span>`;
            }
        }
    }
    
    drawBoard() {
        for (let row = 0; row < this.BOARD_SIZE; row++) {
            for (let col = 0; col < this.BOARD_SIZE; col++) {
                const x = col * this.SQUARE_SIZE;
                const y = row * this.SQUARE_SIZE;
                
                // Alternate colors for checkerboard
                const color = (row + col) % 2 === 0 ? this.WHITE : this.BLACK;
                this.ctx.fillStyle = color;
                this.ctx.fillRect(x, y, this.SQUARE_SIZE, this.SQUARE_SIZE);
                
                // Draw highlights for selected unit and possible moves
                if (this.selectedUnit && 
                    this.selectedUnit[0] === row && this.selectedUnit[1] === col) {
                    // Yellow border for selected unit
                    this.ctx.strokeStyle = this.YELLOW;
                    this.ctx.lineWidth = 4;
                    this.ctx.strokeRect(x, y, this.SQUARE_SIZE, this.SQUARE_SIZE);
                } else if (this.possibleMoves.has(`${row},${col}`) || 
                          this.possibleJumps.has(`${row},${col}`)) {
                    // Green border for possible moves
                    this.ctx.strokeStyle = this.GREEN;
                    this.ctx.lineWidth = 4;
                    this.ctx.strokeRect(x, y, this.SQUARE_SIZE, this.SQUARE_SIZE);
                }
            }
        }
    }
    
    drawUnits() {
        for (let row = 0; row < this.BOARD_SIZE; row++) {
            for (let col = 0; col < this.BOARD_SIZE; col++) {
                const unit = this.board[row][col];
                if (unit !== this.EMPTY) {
                    const centerX = col * this.SQUARE_SIZE + this.SQUARE_SIZE / 2;
                    const centerY = row * this.SQUARE_SIZE + this.SQUARE_SIZE / 2;
                    
                    // Choose color based on player
                    const color = unit === this.PLAYER1 ? this.RED : this.BLUE;
                    
                    // Draw circle
                    this.ctx.beginPath();
                    this.ctx.arc(centerX, centerY, 30, 0, 2 * Math.PI);
                    this.ctx.fillStyle = color;
                    this.ctx.fill();
                    
                    // Add white border for visibility
                    this.ctx.strokeStyle = this.WHITE;
                    this.ctx.lineWidth = 2;
                    this.ctx.stroke();
                }
            }
        }
    }
    
    draw() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.drawBoard();
        this.drawUnits();
        this.updateGameInfo();
        this.updateEndTurnButton();
    }
}

// Start the game when page loads
let game;
window.addEventListener('load', () => {
    game = new NineSquare();
});
