import pygame
import sys
from copy import deepcopy
import time

# Constants for the game pieces
EMPTY = 0
BLACK = 1
WHITE = -1
black_count = 0
white_count = 0

# Board size for Othello
BOARD_SIZE = 8
CELL_SIZE = 60
WINDOW_WIDTH = BOARD_SIZE * CELL_SIZE
WINDOW_HEIGHT = BOARD_SIZE * CELL_SIZE

# Colors
WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
GREEN_COLOR = (0, 128, 0)
GREY_COLOR = (192,192,192)
GRID_COLOR = (0, 128, 0)

# Initialize Pygame
pygame.init()

# Create the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Othello")

def initial_state():
    # Create an initial Othello game board
    board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    board[3][3] = board[4][4] = WHITE
    board[3][4] = board[4][3] = BLACK
    return board

def draw_board(board):
    screen.fill(GREY_COLOR)

    # Draw gridlines
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == BLACK:
                pygame.draw.circle(screen, BLACK_COLOR, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2 - 5)
            elif board[row][col] == WHITE:
                pygame.draw.circle(screen, WHITE_COLOR, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2 - 5)

# Function to determine the current player based on the number of pieces
def player(board):
    global black_count, white_count

    if black_count == white_count:
        return BLACK
    else:
        return WHITE

# Function to get a list of possible actions (valid moves) for the current player
def actions(board):
    # Return a list of possible actions (valid moves) for the current player
    player_color = player(board)
    possible_actions = []

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if is_valid_move(board, i, j, player_color):
                possible_actions.append((i, j))

    return possible_actions

# Function to check if a move is valid
def is_valid_move(board, row, col, player_color):
    # Check if a move is valid
    if board[row][col] != EMPTY:
        return False

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    for dr, dc in directions:
        r, c = row + dr, col + dc
        flipped = False

        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            if board[r][c] == player_color:
                if flipped:
                    return True
                break
            elif board[r][c] == EMPTY:
                break
            else:
                flipped = True

            r, c = r + dr, c + dc

    return False

# Function to apply a player's action to the board and flip pieces accordingly
def result(board, action):
    row, col = action
    player_color = player(board)
    new_board = deepcopy(board)
    new_board[row][col] = player_color

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    for dr, dc in directions:
        r, c = row + dr, col + dc
        flipped = False
        flip_list = []

        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            if new_board[r][c] == player_color:
                if flipped:
                    for fr, fc in flip_list:
                        new_board[fr][fc] = player_color
                break
            elif new_board[r][c] == EMPTY:
                break
            else:
                flipped = True
                flip_list.append((r, c))

            r, c = r + dr, c + dc

    return new_board

# Function to determine the winner based on the number of pieces
def winner(board):
    black_count = sum(row.count(BLACK) for row in board)
    white_count = sum(row.count(WHITE) for row in board)

    if black_count > white_count:
        return BLACK
    elif white_count > black_count:
        return WHITE
    else:
        return EMPTY

# Function to check if the game is over
def terminal(board):
    return not any(actions(board)) or all(all(cell != EMPTY for cell in row) for row in board)

# Function to calculate the utility value for the AI player
def utility(board):
    player_color = player(board)
    if player_color == BLACK:
        return sum(row.count(BLACK) for row in board) - sum(row.count(WHITE) for row in board)
    else:
        return sum(row.count(WHITE) for row in board) - sum(row.count(BLACK) for row in board)

# Alpha-beta pruning minimax algorithm
def alphabeta(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or terminal(board):
        return utility(board), None

    if maximizing_player:
        max_val = float('-inf')
        best_move = None
        for action in actions(board):
            value, _ = alphabeta(result(board, action), depth - 1, alpha, beta, False)
            if value > max_val:
                max_val = value
                best_move = action
            alpha = max(alpha, max_val)
            if alpha >= beta:
                break  # Prune the remaining branches
        return max_val, best_move
    else:
        min_val = float('inf')
        best_move = None
        for action in actions(board):
            value, _ = alphabeta(result(board, action), depth - 1, alpha, beta, True)
            if value < min_val:
                min_val = value
                best_move = action
            beta = min(beta, min_val)
            if alpha >= beta:
                break  # Prune the remaining branches
        return min_val, best_move

# Set the font size and color for displaying player turn
FONT_SIZE = 36
font = pygame.font.Font(None, FONT_SIZE)
PLAYER_LABEL_COLOR = GREEN_COLOR
HIGHLIGHT_COLOR = (0, 255, 0) 

# Function to display the current player's turn
def draw_player_turn(player):
    label = font.render("Turn: " + ("Black" if player == BLACK else "White"), 1, PLAYER_LABEL_COLOR)
    screen.blit(label, (10, 10))

# Function to highlight possible moves
def draw_possible_moves(board):
    for action in actions(board):
        row, col = action
        x = col * CELL_SIZE
        y = row * CELL_SIZE
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, (x, y, CELL_SIZE, CELL_SIZE), 2)

# Main game loop
def main():
    global black_count, white_count

    board = initial_state()
    depth = 5  # AI search depth
    player_turn = BLACK  # Start with the user as White

    while not terminal(board):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(GREEN_COLOR)
        draw_board(board)
        draw_possible_moves(board)
        draw_player_turn(player_turn)
        pygame.display.update()

        if player_turn == WHITE:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    col = x // CELL_SIZE
                    row = y // CELL_SIZE
                    if (row, col) in actions(board):
                        board = result(board, (row, col))
                        player_turn = BLACK
                        white_count += 1 

        elif player_turn == BLACK:
            _, best_move = alphabeta(board, depth, float('-inf'), float('inf'), True)
            if best_move:
                board = result(board, best_move)
                player_turn = WHITE
                black_count += 1  

    # Game over, determine the winner
    winning_player = winner(board)
    if winning_player == BLACK:
        print("Black wins!")
        label = font.render("Black Wins!", 20, PLAYER_LABEL_COLOR)
    elif winning_player == WHITE:
        print("White wins!")
        label = font.render("White Wins!", 20, PLAYER_LABEL_COLOR)
    else:
        print("It's a tie!")
        label = font.render("It's a Tie!", 20, PLAYER_LABEL_COLOR)

    screen.blit(label, (WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 - 20))
    pygame.display.update()

if __name__ == "__main__":
    main()
