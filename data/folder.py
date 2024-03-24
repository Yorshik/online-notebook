from sqlalchemy.orm import relationship

from .db_session import SqlAlchemyBase
import datetime
from flask_login import UserMixin
import sqlalchemy
from werkzeug.security import check_password_hash, generate_password_hash


class Folder(SqlAlchemyBase, UserMixin):
    __tablename__ = 'folders'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    owner = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = relationship('User')
    hashed_password = sqlalchemy.Column(sqlalchemy.String, default='none')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
