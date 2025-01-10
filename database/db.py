import sqlite3

class DBManager:
    def __init__(self, db_name="chess_game.db"):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        # Create the players table if it doesn't exist
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        );
        """)
        self.connection.commit()

    # Create the moves table if it doesn't exist
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            move TEXT,
            game_id INTEGER,
            FOREIGN KEY (player_id) REFERENCES players(id)
        );
        """)
        self.connection.commit()
      

    def save_player(self, player_name):
        # Save a player to the database and return their ID
        self.cursor.execute("INSERT INTO players (name) VALUES (?)", (player_name,))
        self.connection.commit()
        return self.cursor.lastrowid  # Return the player ID

    def get_player_name(self, player_id):
        # Get the player's name by ID
        self.cursor.execute("SELECT name FROM players WHERE id = ?", (player_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None


    def save_move(self, player_id, move):

        # Save a move to the database, linking it to the player by ID
        self.cursor.execute("INSERT INTO moves (player_id, move) VALUES (?, ?)", 
                            (player_id, move))
        self.connection.commit()

    def get_moves(self):
        # Retrieve all moves from the database
        self.cursor.execute("SELECT * FROM moves ORDER BY id DESC")
        return self.cursor.fetchall()

    def close_connection(self):
        # Close the database connection
        self.connection.close()

# Example usage:
if __name__ == "__main__":
    db_manager = DBManager()
    
    # # Example player names (in actual game, these will come from the player input)
    # player1_name = "Player1"
    # player2_name = "Player2"
    
    # # Save players to the database and get their IDs
    # player1_id = db_manager.save_player(player1_name)
    # player2_id = db_manager.save_player(player2_name)
    
    # # Save moves for the players
    # db_manager.save_move(player1_id, "e2e4")
    # db_manager.save_move(player2_id, "e7e5")
    
    # Example usage: saving a player and move
    player1_id = db_manager.save_player("Player1")
    db_manager.save_move(player1_id,  "e2e4")
    

    # Retrieve all moves
    moves = db_manager.get_moves()
    for move in moves:
        print(move)
    
    db_manager.close_connection()