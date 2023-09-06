from datetime import datetime
import sqlalchemy as sq
from configparser import ConfigParser
from sqlalchemy.orm import sessionmaker
from models import create_tables, Users, Preferences, Likes, Blocks, Matches
from sqlalchemy import exc

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

    def add_user(self, vk_id, fname, lname, gender, birth_date, location, state, cursess):

        newuser = Users(vk_id = vk_id,
                        fname = fname,
                        lname = lname,
                        gender = gender,
                        birth_date = datetime.strptime(birth_date, '%d.%m.%Y'),
                        location = location,
                        state = state)

        cursess.add(newuser)   
        cursess.commit()

    def update_state(self, vk_id, new_state, cursess):

        self.user_to_update = cursess.query(Users).filter_by(vk_id=vk_id).first()

        if self.user_to_update:
        
            self.user_to_update.state = new_state
            cursess.commit()

        else:
            
            print("User not found.")


    def like(self, liker, liked, cursess):
      
        self.newlike = Likes(liker = liker,
                        liked = liked)
        cursess.add(self.newlike)   
        try:
            cursess.commit()
        except exc.IntegrityError:
            pass

    def block(self, blocker, blocked, cursess):

        cursess = self.create_session(self.engine)

        self.newblock = Blocks(blocker = blocker,
                        blocked = blocked)
        cursess.add(self.newblock)   
        try:
            cursess.commit()
        except exc.IntegrityError:
            pass

    def match(self, matcher, matched, cursess):

        self.newmatch = Matches(user1 = matcher,
                        user2 = matched)
        cursess.add(self.newmatch)   
        try:
            cursess.commit()
        except exc.IntegrityError:
            pass

    def prefer_location(self, vk_id, location, cursess):

        #находим запись пользователя в БД
        self.user_to_update = cursess.query(Users).filter_by(vk_id=vk_id).first()
        #проверяем существует ли запись в БД
        if self.user_to_update:
            newpref = Preferences(vk_id = vk_id,
                                  location = location)
            cursess.add(newpref)   
            cursess.commit()

        else:
            print("User not found.")


    def prefer_age(self, vk_id, age: str, cursess):

        cursess = self.create_session(self.engine)
        #находим запись пользователя в БД
        self.user_to_update = cursess.query(Users).filter_by(vk_id=vk_id).first()
        #проверяем существует ли запись в БД
        if self.user_to_update:

            self.pref_to_update = cursess.query(Preferences).filter_by(vk_id=vk_id).first()
            self.pref_to_update.age = age
            cursess.commit()

        else:
            print("User not found.")


    def prefer_gender(self, vk_id, gender: str, cursess):

        #находим запись пользователя в БД
        self.user_to_update = cursess.query(Users).filter_by(vk_id=vk_id).first()
        #проверяем существует ли запись в БД
        if self.user_to_update:

            self.pref_to_update = cursess.query(Preferences).filter_by(vk_id=vk_id).first()
            self.pref_to_update.gender = gender
            cursess.commit()

        else:
            print("User not found.")


    def get_pref(self, vk_id, cursess):
        
        
        self.user_to_update = cursess.query(Users).filter_by(vk_id=vk_id).first()
        if self.user_to_update:
            self.pref = cursess.query(Preferences).filter_by(vk_id=vk_id).first()
            result = {'vk_id': self.pref.vk_id,
                      'gender': self.pref.gender,
                      'age': self.pref.age,
                      'location': self.pref.location}

        else:
            print('User does not exist.')
        cursess.close
        return result

if __name__ == "__main__":

    newdb = data_base('config.ini')
    
    newdb.build_tables()
    
    mysession = newdb.create_session(newdb.engine)
    
    newdb.add_user('123456', 'Ivan', 'Ivanov', 'm', '20.12.2001', 'Moscow', '', mysession)
    newdb.add_user('456789', 'Ivanna', 'Ivanova', 'f', '03.12.1995', 'Kazan', '', mysession)
    newdb.add_user('025345', 'Vasiliy' , 'Pupkin', 'm', '20.12.2000', 'Voronezh', '', mysession)
    newdb.add_user('345666', 'Fedor' , 'Pupkin', 'm', '20.12.2000', 'Nizhniy Novgorod', '', mysession)
    newdb.add_user('034534', 'Irina', 'Pupkina', 'f', '20.01.1996', 'Peterburg', '', mysession)
    newdb.update_state('123456', 'start', mysession)
    
    newdb.like('456789', '025345', mysession)
    newdb.like('025345', '345666', mysession)
    newdb.block('025345', '345666', mysession)
    newdb.match('456789', '025345', mysession)
    newdb.prefer_location('123456', 'Kazan', mysession)
    newdb.prefer_age('123456', '20-30', mysession)
    newdb.prefer_gender('123456', 'm', mysession)
    print(newdb.get_pref('123456', mysession))
    #add_user('id456789', 'Ivanova', 'f', '03.12.1995', 'Kazan', '')
    #add_user('id025345', 'Pupkin', 'm', '20.12.2000', 'Voronezh', '')
    #add_user('id345666', 'Pupkin', 'm', '20.12.2000', 'Nizhniy Novgorod', '')
    #add_user('id034534', 'Pupkina', 'f', '20.01.1996', 'Peterburg', '')
    #like(1,2)
    #like(1,4)
    mysession.close()