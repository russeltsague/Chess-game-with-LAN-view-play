from database.model import Player
from database.db_setup import get_session


with get_session() as session:
    
    new_player = Player(name="Shalom", username='shalom1')
    session.add(new_player)
    session.commit()    
    print("Player added successfully!")
