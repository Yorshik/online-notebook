import datetime

from sqlalchemy.exc import IntegrityError
from flask import jsonify, abort, request
from flask_restful import Resource, reqparse

from data.db_session import create_session
from data.user import User
from data.api_keys import get_api_key

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('surname', required=True)
parser.add_argument('password', required=True)
parser.add_argument('email', required=True)
parser.add_argument('nickname', required=True)

parser2 = reqparse.RequestParser()
parser2.add_argument('apikey', required=True)
parser2.add_argument('access_level', required=True)


def abort_if_user_not_found(user_id):
    session = create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404)


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if get_api_key(args.access_level) != args.apikey:
            abort(403)
        db_sess = create_session()
        user = db_sess.query(User).filter(User.id == user_id).first()
        return jsonify(
            {
                'user': user.to_dict(),
                'status': 200
            }
        )

    def put(self, user_id):
        if not request.json:
            abort(400)
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if not (args.access_level == 'admin' and get_api_key(args.access_level) == args.apikey):
            abort(403)
        try:
            args = parser.parse_args()
        except ValueError:
            abort(400)
        abort_if_user_not_found(user_id)
        db_sess = create_session()
        user = db_sess.query(User).filter(User.id == user_id).first()
        db_sess.delete(user)
        user.surname = args.surname
        user.name = args.name
        user.email = args.email
        user.set_password(args.password)
        user.nickname = args.nickname
        user.modified_date = datetime.datetime.now()
        try:
            db_sess.add(user)
            db_sess.commit()
        except IntegrityError:
            abort(406)
        return jsonify(
            {
                'edited_user': user.to_dict()
            }
        )

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if not (args.access_level == 'admin' and get_api_key(args.access_level) == args.apikey):
            abort(403)
        session = create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if get_api_key(args.access_level) != args.apikey:
            abort(403)
        db_sess = create_session()
        users = db_sess.query(User).all()
        return jsonify(
            {
                'users':
                    [item.to_dict()
                     for item in users],
                'status': 200
            }
        )

    def post(self):
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if not (args.access_level in ['admin', 'pro'] and get_api_key(args.access_level) == args.apikey):
            abort(403)
        try:
            args = parser.parse_args()
        except ValueError:
            return jsonify(
                {
                    'error': 'Bad request'
                }
            )
        session = create_session()
        user = User()
        user.surname = args.surname
        user.name = args.name
        user.email = args.email
        user.set_password(args.password)
        user.nickname = args.nickname
        user.modified_date = datetime.datetime.now()
        try:
            session.add(user)
            session.commit()
        except IntegrityError:
            abort(406)
        return jsonify({'id': user.id})
