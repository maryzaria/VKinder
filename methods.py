from datetime import datetime
import sqlalchemy as sq
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


def add_user(fname, lname, gender, birth_date, location, state):

    newuser = Users(fname = fname,
                    lname = lname,
                    gender = gender,
                    birth_date = datetime.strptime(birth_date, '%d.%m.%Y'),
                    location = location,
                    state = state)

    session.add(newuser)   
    session.commit()


def update_state(vk_id, new_state):

    user_to_update = session.query(Users).filter_by(vk_id=vk_id).first()

    if user_to_update:
    
        user_to_update.state = new_state
        session.commit()

    else:
        
        print("User not found.")

session.close()


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

    add_user('id123456', 'Ivan', 'Ivanov', 'm', '20.12.2001', 'Moscow', '')
    add_user('id456789', 'Ivanova', 'f', '03.12.1995', 'Kazan', '')
    add_user('id025345', 'Pupkin', 'm', '20.12.2000', 'Voronezh', '')
    add_user('id345666', 'Pupkin', 'm', '20.12.2000', 'Nizhniy Novgorod', '')
    add_user('id034534', 'Pupkina', 'f', '20.01.1996', 'Peterburg', '')
    #like(1,2)
    #like(1,4)