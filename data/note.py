from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from data.db_session import SqlAlchemyBase
import datetime
from flask_login import UserMixin
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin


class Note(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'notes'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    the_folder = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('folders.id'))
    hashed_password = sqlalchemy.Column(sqlalchemy.String, default='none')
    content = sqlalchemy.Column(sqlalchemy.String)
    folder = relationship('Folder')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    @classmethod
    def from_dict(cls, data):
        cls.__dict__.update(data)
        return cls()