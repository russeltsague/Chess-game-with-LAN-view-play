import sqlite3

# Connect to the database
conn = sqlite3.connect('chess_game.db')
cursor = conn.cursor()

# Query to get all moves from the 'moves' table
cursor.execute("SELECT players.id, players.name, moves.move FROM players JOIN moves ON players.id = moves.player_id ORDER BY moves.id;")

# Fetch all the rows
rows = cursor.fetchall()

# Print the data
for row in rows:
    print(row)

# Close the connection
conn.close()
