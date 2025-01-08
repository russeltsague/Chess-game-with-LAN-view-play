import socket
import threading
import pygame
import sys
import time
import chess

# Initialize pygame
pygame.init()

# Game constants
board_size = 8
square_size = 110
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

# Function to initialize the network
def setup_connection():
    global sock, is_server, turn
    role = input("Choose your role (server/client): ").strip().lower()
    
    if role == "server":
        is_server = True
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", 5555))
        sock.listen(1)
        print("Waiting for a client to connect...")
        conn, addr = sock.accept()
        print(f"Client connected from {addr}")
        sock = conn
    elif role == "client":
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
        sock.send(move.encode())

# Function to receive moves from the opponent
def receive_moves():
    global turn
    while True:
        try:
            move = sock.recv(1024).decode()
            if move:
                print(f"Move received: {move}")
                board.push_uci(move)  # Update the board with the received move
                turn = not turn       # Switch turns
        except Exception as e:
            print(f"Error receiving move: {e}")
            break

# Function to draw the chessboard (flipped for client)
def draw_board():
    for row in range(board_size):
        for col in range(board_size):
            if is_server:
                color = light_square_color if (row + col) % 2 == 0 else dark_square_color
            else:
                color = light_square_color if (7 - row + col) % 2 == 0 else dark_square_color  # Flip for client
            pygame.draw.rect(screen, color, pygame.Rect(col * square_size, row * square_size, square_size, square_size))

# Function to draw the pieces
def draw_pieces():
    piece_images = {
        'P': pygame.image.load('images/white_pawn.png'),
        'R': pygame.image.load('images/white_rook.png'),
        'N': pygame.image.load('images/white_knight.png'),
        'B': pygame.image.load('images/white_bishop.png'),
        'Q': pygame.image.load('images/white_queen.png'),
        'K': pygame.image.load('images/white_king.png'),
        'p': pygame.image.load('images/black_pawn.png'),
        'r': pygame.image.load('images/black_rook.png'),
        'n': pygame.image.load('images/black_knight.png'),
        'b': pygame.image.load('images/black_bishop.png'),
        'q': pygame.image.load('images/black_queen.png'),
        'k': pygame.image.load('images/black_king.png'),
    }
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row, col = divmod(square, 8)
            if not is_server:
                row, col = 7 - row, 7 - col  # Flip for client
            piece_image = piece_images.get(piece.symbol())
            if piece_image:
                piece_image = pygame.transform.scale(piece_image, (square_size, square_size))
                screen.blit(piece_image, (col * square_size, (7 - row) * square_size))

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
        move = chess.Move.from_uci(f"{start_square}{end_square}")
        if move in board.legal_moves:
            board.push(move)  # Apply the move locally
            send_move(move.uci())  # Send the move to the opponent
            move_list.append(move.uci())  # Add the move to the tracker
            turn = not turn       # Switch turns
        else:
            print("Illegal move!")
    except ValueError:
        print("Invalid move format!")

# Function to draw the sidebar with player info and turn display
def draw_sidebar():
    pygame.draw.rect(screen, black, pygame.Rect(board_size * square_size, 0, 250, HEIGHT))
    
    # Display player names
    player1_name = font.render("White: You", True, white)
    player2_name = font.render("Black: Opponent", True, white)
    screen.blit(player1_name, (board_size * square_size + 20, 20))
    screen.blit(player2_name, (board_size * square_size + 20, 60))
    
    # Display current turn
    turn_message = "White to Play" if board.turn else "Black to Play"
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
    move_text = "Moves:\n" + "\n".join(move_list[-5:])  # Show last 5 moves
    move_tracker = font.render(move_text, True, white)
    screen.blit(move_tracker, (board_size * square_size + 20, 200))

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
