from datetime import datetime
import sqlalchemy
from configparser import ConfigParser
from sqlalchemy.orm import sessionmaker
from models import create_tables, Users, Preferences, Likes, Blocks, Matches

configur = ConfigParser()
configur.read('config.ini')
  

DSN = (configur.get('connection', 'dbtype') + '://' +
       configur.get('connection', 'user') + 
       ':' + configur.get('connection', 'password') + 
       '@' + configur.get('connection', 'server') + 
       ':' + configur.get('connection', 'port') + '/' 
       + configur.get('connection', 'db'))

engine = sqlalchemy.create_engine(DSN)

create_tables(engine)

Session = sessionmaker(bind=engine)

session = Session()
session.commit()   


def add_user(fname, lname, gender, birth_date, location):

    newuser = Users(fname = fname,
                    lname = lname,
                    gender = gender,
                    birth_date = datetime.strptime(birth_date, '%d.%m.%Y'),
                    location = location)

    session.add(newuser)   
    session.commit()


def like(liker, liked):

    newlike = Likes(liker = liker,
                    liked = liked)
    session.add(newlike)   
    session.commit()

def block(blocker, blocked):

    newlike = Likes(blocker = blocker,
                    blocked = blocked)
    session.add(newlike)   
    session.commit()


session.close


if __name__ == "__main__":

    add_user('adsad', 'fssfsdf', 'm', '20.12.2021', 'kazan')
    add_user('Alena', 'fssfsdf', 'f', '03.12.1995', 'kazan')
    add_user('Vasia', 'fssfsdf', 'm', '20.12.2000', 'voronezh')
    like(1,2)
    like(1,4)