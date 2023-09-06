from datetime import datetime
import sqlalchemy as sq
from configparser import ConfigParser
from sqlalchemy.orm import sessionmaker
from models import create_tables, Users, Preferences, Likes, Blocks, Matches

class data_base:

    def __init__(self, config):
        self.config = config
        self.initialize(self.config)

    def initialize(self, config: str):

        self.configur = ConfigParser()
        self.configur.read(config)
        self.dsn = (self.configur.get('connection', 'dbtype') + '://' +
               self.configur.get('connection', 'user') + 
               ':' + self.configur.get('connection', 'password') + 
               '@' + self.configur.get('connection', 'server') + 
               ':' + self.configur.get('connection', 'port') + '/' 
               + self.configur.get('connection', 'db'))
        self.engine = sq.create_engine(self.dsn)
        return self.engine

    def create_session(self, engine):

        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()
        self.session.commit()
        return self.session  

    def build_tables(self):

        create_tables(self.engine)

    def add_user(self, vk_id, fname, lname, gender, birth_date, location, state):

        mysession = self.create_session(self.engine)

        newuser = Users(vk_id = vk_id,
                        fname = fname,
                        lname = lname,
                        gender = gender,
                        birth_date = datetime.strptime(birth_date, '%d.%m.%Y'),
                        location = location,
                        state = state)

        mysession.add(newuser)   
        mysession.commit()
        mysession.close()

    def update_state(self, vk_id, new_state):

        mysession = self.create_session(self.engine)

        user_to_update = mysession.query(Users).filter_by(vk_id=vk_id).first()

        if user_to_update:
        
            user_to_update.state = new_state
            mysession.commit()

        else:
            
            print("User not found.")

            mysession.close()

'''
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

'''
if __name__ == "__main__":

    newdb = data_base('config.ini')
    newdb.build_tables()
    newdb.create_session(newdb.engine)
    newdb.add_user('id123456', 'Ivan', 'Ivanov', 'm', '20.12.2001', 'Moscow', '')
    newdb.update_state('id123456', 'start')
    #add_user('id456789', 'Ivanova', 'f', '03.12.1995', 'Kazan', '')
    #add_user('id025345', 'Pupkin', 'm', '20.12.2000', 'Voronezh', '')
    #add_user('id345666', 'Pupkin', 'm', '20.12.2000', 'Nizhniy Novgorod', '')
    #add_user('id034534', 'Pupkina', 'f', '20.01.1996', 'Peterburg', '')
    #like(1,2)
    #like(1,4)