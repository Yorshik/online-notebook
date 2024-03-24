from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase
import datetime
from flask_login import UserMixin
import sqlalchemy


class Note(SqlAlchemyBase, UserMixin):
    __tablename__ = 'notes'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    the_folder = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('folders.id'))
    folder = relationship('folders')
    hashed_password = sqlalchemy.Column(sqlalchemy.String, default='none')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
