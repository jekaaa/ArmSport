from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    Boolean,
    Float,
    Table
    )
from sqlalchemy.orm import (
    relationship
)


from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    login = Column(Text)
    password = Column(Text)

tournaments_player = Table('tournaments_player', Base.metadata,
    Column('player_id', Integer, ForeignKey('player.id')),
    Column('tournament_id', Integer, ForeignKey('tournament.id')))

games_win_grid = Table('games_win_grid', Base.metadata,
    Column('player_id', Integer, ForeignKey('player.id')),
    Column('win_grid_id', Integer, ForeignKey('win_grid.id')))

games_lose_grid = Table('games_lose_grid', Base.metadata,
    Column('player_id', Integer, ForeignKey('player.id')),
    Column('lose_grid_id', Integer, ForeignKey('lose_grid.id')))

final_grid = Table('games_final', Base.metadata,
    Column('player_id', Integer, ForeignKey('player.id')),
    Column('final_id', Integer, ForeignKey('final.id'))
)

semifinal_grid = Table('games_semifinal', Base.metadata,
    Column('player_id', Integer, ForeignKey('player.id')),
    Column('semifinal_id', Integer, ForeignKey('semifinal.id'))
)

class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    first_name = Column(Text)
    middle_name = Column(Text)
    last_name = Column(Text)
    left_hand = Column(Integer)
    right_hand = Column(Integer)
    age = Column(Integer)
    sex = Column(Boolean)
    weight = Column(Float)
    team = Column(Text)
    lose = Column(Integer)
    eventId = Column(Integer, ForeignKey('event.id'))

    event = relationship("Event", backref="players")

class Tournament(Base):
    __tablename__ = 'tournament'
    id = Column(Integer, primary_key=True)
    hand = Column(Boolean)
    eventId = Column(Integer, ForeignKey('event.id'))
    typeId = Column(Integer, ForeignKey('type.id'))
    weight = Column(Text)

    players = relationship("Player",secondary=tournaments_player)
    type = relationship("Type",backref="tournaments")
    event = relationship("Event", backref="tournaments")

class Final(Base):
    __tablename__= "final"
    id = Column(Integer, primary_key=True)
    tour = Column(Integer)
    tournamentId = Column(Integer, ForeignKey('tournament.id'))
    winnerId = Column(Integer, ForeignKey('player.id'))
    gap = Column(Boolean)
    first_fouls = Column(Integer)
    second_fouls = Column(Integer)

    games = relationship("Player", secondary=final_grid)
    tournament = relationship("Tournament", backref="final")
    winner = relationship("Player", backref="final")

class Semifinal(Base):
    __tablename__= "semifinal"
    id = Column(Integer, primary_key=True)
    tournamentId = Column(Integer, ForeignKey('tournament.id'))
    winnerId = Column(Integer, ForeignKey('player.id'))
    gap = Column(Boolean)
    first_fouls = Column(Integer)
    second_fouls = Column(Integer)

    games = relationship("Player", secondary=semifinal_grid)
    tournament = relationship("Tournament", backref="semifinal")
    winner = relationship("Player", backref="semifinal")

class WinGrid(Base):
    __tablename__ = "win_grid"
    id = Column(Integer, primary_key=True)
    tour = Column(Integer)
    tournamentId = Column(Integer, ForeignKey('tournament.id'))
    winnerId = Column(Integer, ForeignKey('player.id'))
    gap = Column(Boolean)
    first_fouls = Column(Integer)
    second_fouls = Column(Integer)

    games = relationship("Player",secondary=games_win_grid)
    tournament = relationship("Tournament", backref="win_grids")
    winner = relationship("Player",backref="win_grids")

class Table(Base):
    __tablename__ = "table"
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    tournamentId = Column(Integer, ForeignKey('tournament.id'))
    eventId = Column(Integer, ForeignKey('event.id'))

    event = relationship("Event",backref="tables")
    tournament = relationship("Tournament", backref="tables")

class LoseGrid(Base):
    __tablename__ = "lose_grid"
    id = Column(Integer, primary_key=True)
    tour = Column(Integer)
    tournamentId = Column(Integer, ForeignKey('tournament.id'))
    winnerId = Column(Integer, ForeignKey('player.id'))
    gap = Column(Boolean)
    first_fouls = Column(Integer)
    second_fouls = Column(Integer)

    games = relationship("Player",secondary=games_lose_grid)
    tournament = relationship("Tournament", backref="lose_grids")
    winner = relationship("Player", backref="lose_grids")

class Event(Base):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True)
    numberTable = Column(Integer)
    name = Column(Text)
    city = Column(Text)
    date = Column(Text)
    dateEnd = Column(Text)
    description = Column(Text)
    building = Column(Text)
    address = Column(Text)
    image_path = Column(Text)
    userId = Column(Integer,ForeignKey('user.id'))
    typeId = Column(Integer,ForeignKey('type.id'))

    type = relationship("Type",backref = "events")
    user = relationship("User",backref = "events")

class Type(Base):
    __tablename__ = 'type'
    id = Column(Integer, primary_key=True)
    name = Column(Text)

class Favorites(Base):
    __tablename__ = "favorite"
    id = Column(Integer, primary_key=True)
    userId = Column(Integer,ForeignKey('user.id'))
    eventId = Column(Integer, ForeignKey('event.id'))

    user = relationship("User",backref="favorites")
    event = relationship("Event",backref="favorites")