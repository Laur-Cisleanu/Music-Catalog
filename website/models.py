#from . import db
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin

engine = create_engine('sqlite:///D:\Python\Projects\Music-Catalog\library.db', echo=True)
Base = declarative_base()

#class Songs(db.Model):
#   id = db.Column(db.Integer, primary_key = True)
#   data = db.Column(db.String(10000))
#   user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Users(Base, UserMixin):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key = True)
    email = Column(String(150), unique = True)
    username = Column(String(150), unique = True)
    password = Column(String(1000))
    admin = Column(Integer)
    user_description = Column(Text)
    profile_picture = Column(Text)

    def __init__(self, user_id, email, username, password, admin, user_description, profile_picture):
        self.user_id = user_id
        self.email = email
        self.username = username
        self.password = password
        self.admin = admin
        self.user_description = user_description
        self.profile_picture = profile_picture
    
    def get_id(self):
           return (self.user_id)

Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

    






#base = declarative_base()
#
#class Songs(base):
#    __tablename__ = "Songs"
#
#    id = Column("Id", Integer, primary_key = True)
#    data = Column("link", String(10000))
#    user_id = Column("User_Id", Integer, ForeignKey('user.id'))
#
#    def __init__(self, id, data, user_id):
#        self.id = id
#        self.data = data
#        self.user_id = user_id
#
#    def __repr__(self):
#        return f"({self.id}) {self.data}, user_id = {self.user_id}"
#
#class Users(base, UserMixin):
#    __tablename__ = "Users"
#
#    id = Column("Id", Integer, primary_key = True)
#    email = Column("Email", String(150), unique = True)
#    username = Column("Username", String(150), unique = True)
#    password = Column("Password", String(150))
#    songs = db.relationship('Songs')
#
#    def __init__(self, id, email, username, password, songs):
#        self.id = id
#        self.email = email
#        self.username = username
#        self.password = password
#        self.songs = songs
#
#    def __repr__(self):
#        return f"({self.id}) {self.email}, {self.username}, {self.password}, {self.songs}"
#
#engine = create_engine("sqlite:///mydb.db" echo = True)
#base.metadata.create_all(bind=engine)
#
#Session = sessionmaker(bind = engine)
#session = Session()