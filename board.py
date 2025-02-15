import socket
import threading
import pygame
import sys
import time
import chess
import sqlite3
from database.db import DBManager  # Make sure to import the DBManager

# Initialize the DBManager
db_manager = DBManager()

# Initialize pygame
pygame.init()

# Game constants
board_size = 8
square_size = 70
WIDTH = square_size * board_size + 250
HEIGHT = square_size * board_size

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
light_square_color = (254, 254, 220)
dark_square_color = (125, 135, 150)

# Font for text
font = pygame.font.Font(None, 36)

# Create a pygame window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game with LAN Multiplayer")

# Initialize the chessboard using python-chess
board = chess.Board()

# Networking variables
sock = None
is_server = None
turn = True  # True for White, False for Black (server starts as White)
move_list = []  # List to keep track of moves

player_names = ["", ""]  # List to store player names
player_ids = [None, None]  # List to store player IDs


# Function to initialize the network
def setup_connection():
    global sock, is_server, turn, player_names, player1_name, player2_name, player_ids
    role = input("Choose your role (server/client/viewer): ").strip().lower()
    
    if role == "server":

        is_server = True
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", 5555))
        sock.listen(1)
        print("Waiting for a client to connect...")
        conn, addr = sock.accept()
        print(f"Client connected from {addr}")
        sock = conn

        
        player1_name = input("Enter your name (Player1, White): ").strip()
        player1_id = db_manager.save_player(player1_name)
        print(f"Player 1 (White) saved with name {player1_name} and ID {player1_id}")

    elif role == "client":

        is_server = False
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_ip = input("Enter the server IP address: ").strip()
        sock.connect((server_ip, 5555))
        print("Connected to the server.")
        turn = False  # Clients start as Black

        player2_name = input("Enter Player2's name (Black): ").strip()
        player2_id = db_manager.save_player(player2_name)        
        print(f"Player 2 (Black) saved with name {player2_name} and ID {player2_id}")

    elif role == "viewer":
        is_server = False
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_ip = input("Enter the server IP address: ").strip()
        sock.connect((server_ip, 5555))
        print("Connected to the server.")
        turn = False  # Clients start as Black


    else:
        print("Invalid role. Restart the game and choose server or client.")
        sys.exit()


# Function to send moves to the opponent
def send_move(move):
    if sock:
        # Add player identifier (e.g., "Player1" or "Player2") to the move
        player_name = player_names[0] if turn else player_names[1]
        move_data = f"{player_name}:{move}"  # Example: "Player1:e2e4"
        sock.send(move_data.encode())


# Function to receive moves from the opponent
def receive_moves():
    global turn
    while True:
        try:
            move_data = sock.recv(1024).decode()
            if move_data:
                print(f"Move received: {move_data}")

                # Parse player and move
                player_name, move = move_data.split(":")
                
                # Push move to the chess board
                board.push_uci(move)
                
                # Get piece type
                start_square, end_square = move[:2], move[2:]
                piece = board.piece_at(chess.parse_square(end_square))
                piece_name = {
                    chess.PAWN: "Pawn",
                    chess.KNIGHT: "Knight",
                    chess.BISHOP: "Bishop",
                    chess.ROOK: "Rook",
                    chess.QUEEN: "Queen",
                    chess.KING: "King"
                }.get(piece.piece_type, "Unknown") if piece else "Unknown"

                # Add move to the move_list
                move_list.append({
                    "player": player_name,
                    "piece": piece_name,
                    "move": f"{start_square} to {end_square}"
                })
                
                turn = not turn  # Switch turns
        except Exception as e:
            print(f"Error receiving move: {e}")
            break


# Function to draw the chessboard with labels placed as requested
def draw_board():
    # Adjust font size for labels
    label_font = pygame.font.Font(None, 24)  # Reduced font size

    # Draw the squares on the chessboard
    for row in range(board_size):
        for col in range(board_size):
            if is_server:
                color = light_square_color if (row + col) % 2 == 0 else dark_square_color
            else:
                color = light_square_color if (7 - row + col) % 2 == 0 else dark_square_color  # Flip for client
            pygame.draw.rect(screen, color, pygame.Rect(col * square_size, row * square_size, square_size, square_size))
    
    # Draw the column labels (a-h) at the bottom-right corner
    offset = 5  # Move the letters a little to the right
    for col in range(board_size):
        label = chr(ord('a') + col)  # Convert column number to letter (a-h)
        text = label_font.render(label, True, black)
        # Position the column labels at the extreme bottom-right corner with an offset
        screen.blit(text, ((col + 1) * square_size - text.get_width() - 10 + offset, HEIGHT - text.get_height() - 10))  # Adjusted position

    # Draw the row labels (1-8) at the extreme top-left corner
    for row in range(board_size):
        label = str(8 - row)  # Convert row number to label (8-1)
        text = label_font.render(label, True, black)
        # Position the row labels at the extreme top-left corner
        screen.blit(text, (10, row * square_size + square_size // 2 - text.get_height() // 2))  # Adjusted position

# Function to draw the pieces
def draw_pieces():
    piece_images = {
        'P': pygame.image.load('images/white_pawn.png'),
        'R': pygame.image.load('images/white_rook.png'),
        'N': pygame.image.load('images/white_knight.png'),
        'B': pygame.image.load('images/white_bishop.png'),
        'Q': pygame.image.load('images/white_king.png'),
        'K': pygame.image.load('images/white_queen.png'),
        'p': pygame.image.load('images/black_pawn.png'),
        'r': pygame.image.load('images/black_rook.png'),
        'n': pygame.image.load('images/black_knight.png'),
        'b': pygame.image.load('images/black_bishop.png'),
        'q': pygame.image.load('images/black_king.png'),
        'k': pygame.image.load('images/black_queen.png'),
       
    }

    # Scale down the piece images to be smaller
    piece_size = square_size * 0.75  # Adjust size to 75% of the square size
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row, col = divmod(square, 8)
            if not is_server:
                row, col = 7 - row, 7 - col  # Flip for client
            piece_image = piece_images.get(piece.symbol())
            if piece_image:
                piece_image = pygame.transform.scale(piece_image, (piece_size, piece_size))
                # Calculate position to center the piece within the square
                piece_x = col * square_size + (square_size - piece_size) // 2
                piece_y = (7 - row) * square_size + (square_size - piece_size) // 2
                screen.blit(piece_image, (piece_x, piece_y))


# Function to highlight the legal moves
def highlight_legal_moves():
    if start_square is not None:
        # Get legal moves for the selected piece
        legal_moves = [move.to_square for move in board.legal_moves if move.from_square == start_square]
        for square in legal_moves:
            row, col = divmod(square, 8)
            if not is_server:
                row, col = 7 - row, 7 - col  # Flip for client
            pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(col * square_size, (7 - row) * square_size, square_size, square_size), 5)  # Green border for legal moves

# Function to handle player moves
def handle_move(start_square, end_square):
    global turn
    try:
        # Convert square names to integers if needed
        if isinstance(start_square, str):
            start_square = chess.parse_square(start_square)
        if isinstance(end_square, str):
            end_square = chess.parse_square(end_square)

        move = chess.Move(start_square, end_square)
        if move in board.legal_moves:
            board.push(move)  # Apply the move locally

            # Save the move in the database
            db_manager.save_move(move.uci(), player_names[turn])

            # Get piece type
            piece = board.piece_at(end_square)
            piece_type = piece.piece_type  # Integer value representing the piece type
            piece_name = {
                chess.PAWN: "Pawn",
                chess.KNIGHT: "Knight",
                chess.BISHOP: "Bishop",
                chess.ROOK: "Rook",
                chess.QUEEN: "Queen",
                chess.KING: "King"
            }.get(piece_type, "Unknown")

            # Add move to the move_list with piece type
            move_list.append({
                "player": player_names[turn],
                "piece": piece_name,
                "move": f"{chess.square_name(start_square)} to {chess.square_name(end_square)}"
            })

            send_move(move.uci())  # Send the move to the opponent
            turn = not turn       # Switch turns
        else:
            print("Illegal move!")
    except ValueError as e:
        print(f"Invalid move format: {e}")


# Function to draw the sidebar with player info and turn display
def draw_sidebar():
    pygame.draw.rect(screen, black, pygame.Rect(board_size * square_size, 0, 250, HEIGHT))
    
    # Display player names
    player1_name = db_manager.get_player_name(1)  # Get player 1 name
    player2_name = db_manager.get_player_name(2)  # Get player 2 name
    player1_text = font.render(f"White: {player1_name}", True, white)
    player2_text = font.render(f"Black: {player2_name}", True, white)
    screen.blit(player1_text, (board_size * square_size + 20, 20))
    screen.blit(player2_text, (board_size * square_size + 20, 60))
    
    # Display current turn
    turn_message = f"{player1_name} to Play" if board.turn else f"{player2_name} to Play"
    turn_text = font.render(turn_message, True, white)
    screen.blit(turn_text, (board_size * square_size + 20, 120))
    
    # Display game status (e.g., Check or Checkmate)
    if board.is_checkmate():
        status_text = "Checkmate!"
    elif board.is_check():
        status_text = "Check!"
    elif board.is_stalemate():
        status_text = "Stalemate!"
    else:
        status_text = ""
    status_display = font.render(status_text, True, white)
    screen.blit(status_display, (board_size * square_size + 20, 160))

    # Display move tracker
    move_text_y = 200  # Initial Y position for displaying moves
    for move_entry in move_list:
        move_text = f"{move_entry['player']} ({move_entry['piece']}): {move_entry['move']}"
        move_display = font.render(move_text, True, white)
        screen.blit(move_display, (board_size * square_size + 20, move_text_y))
        move_text_y += 20  # Increment Y position for the next move

# Main game loop
def main():
    global turn, start_square
    setup_connection()  # Initialize the network
    threading.Thread(target=receive_moves, daemon=True).start()

    start_square = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and turn:
                x, y = pygame.mouse.get_pos()
                col, row = x // square_size, y // square_size
                square = chess.square(col, 7 - row) if is_server else chess.square(7 - col, row)  # Flip for client
                
                if start_square is None:
                    start_square = square  # Select the piece
                else:
                    handle_move(chess.square_name(start_square), chess.square_name(square))
                    start_square = None  # Deselect after making the move

        screen.fill(black)
        draw_board()
        draw_pieces()
        highlight_legal_moves()  # Draw legal moves for the selected piece
        draw_sidebar()
        pygame.display.flip()

if __name__ == "__main__":
    main()
