from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable =True)
    username = Column(String, unique =True , nullable= False)
    
class Game(Base):
    __tablename__ = 'games'
    id = Column(Integer , primary_key=True)
    player1_id = Column(Integer, ForeignKey('player.id'), nullable= False)
    player2_id = Column(Integer, ForeignKey('player.id'), nullable= False)
    result= Column(String)
    date = Column(DateTime)