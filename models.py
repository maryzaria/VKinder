import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Users(Base):

    __tablename__ = 'users'
    
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    fname = sq.Column(sq.String(length=100), nullable=False)
    lname = sq.Column(sq.String(length=100), nullable=False)
    gender = sq.Column(sq.String(length=1), nullable=False)
    birth_date = sq.Column(sq.Date, nullable=False)
    location = sq.Column(sq.String(length=50), nullable=False)

    def __str__(self):
        return f"{self.id}: {self.fname} , {self.lname} , {self.gender}, {self.birth_date}, {self.location}"
   

class Preferences(Base):

    __tablename__ = 'preferences'
    
    id = sq.Column(sq.Integer, sq.ForeignKey("users.id"), primary_key=True)
    gender = sq.Column(sq.String(length=1), nullable=False)
    age_from = sq.Column(sq.Integer, nullable=False)
    age_to = sq.Column(sq.Integer)
    location = sq.Column(sq.String(length=50), nullable=False)
    

    preferences = relationship(Users, backref='preferences')

    def __str__(self):
        return f"{self.id}: {self.gender}, {self.age_from}, {self.age_to}, {self.location}"


class Likes(Base):

    __tablename__ = 'likes'
    
    liker = sq.Column(sq.Integer, sq.ForeignKey("users.id"), primary_key=True, nullable=False)
    liked = sq.Column(sq.Integer, primary_key=True, nullable=False)

    likes = relationship(Users, backref='likes')

    def __str__(self):
        return f"{self.liker}: {self.liked}"


class Blocks(Base):

    __tablename__ = 'blocks'
    
    blocker = sq.Column(sq.Integer, sq.ForeignKey("users.id"), primary_key=True, nullable=False)
    blocked = sq.Column(sq.Integer, primary_key=True, nullable=False)

    blocks = relationship(Users, backref='blocks')

    def __str__(self):
        return f"{self.blocker}: {self.blocked}"

class Matches(Base):

    __tablename__ = 'matches'

    user1 = sq.Column(sq.Integer, sq.ForeignKey("users.id"), primary_key=True, nullable=False)
    user2 = sq.Column(sq.Integer, primary_key=True, nullable=False)
    matches = relationship(Users, backref='matches')

    def __str__(self):
        return f"{self.id}: {self.user1}, {self.user2}"


def create_tables(engine):
    Base.metadata.create_all(engine)