from .db_session import SqlAlchemyBase
import datetime
from flask_login import UserMixin
import sqlalchemy
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    nickname = sqlalchemy.Column(sqlalchemy.String, unique=True)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    @classmethod
    def from_dict(cls, data):
        cls.id = data['id']
        cls.email = data['email']
        cls.nickname = data['nickname']
        cls.hashed_password = data['hashed_password']
        return cls()