import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash, generate_password_hash

from data.db_session import SqlAlchemyBase


class Folder(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'folders'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    owner = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    hashed_password = sqlalchemy.Column(sqlalchemy.String, default=generate_password_hash('none'))

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    @classmethod
    def from_dict(cls, data):
        cls.__dict__.update(data)
        return cls()
