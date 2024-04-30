from flask import jsonify, abort, request
from flask_restful import Resource, reqparse
from sqlalchemy.exc import IntegrityError

from data.db_session import create_session
from data.user import User
from scripts.api_keys import free, pro, admin

parser = reqparse.RequestParser()
parser.add_argument('password', required=True)
parser.add_argument('email', required=True)
parser.add_argument('nickname', required=True)

parser2 = reqparse.RequestParser()
parser2.add_argument('apikey', required=True)


def abort_if_user_not_found(user_id):
    session = create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404)


def get_user_by_nickname(user_nickname):
    session = create_session()
    print(user_nickname, 'scuka')
    users = session.query(User).all()
    for user in users:
        if user.nickname == user_nickname:
            print(user)
            return user.id
    return user.id


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if args.apikey not in [free, pro, admin]:
            abort(403)
        db_sess = create_session()
        users = db_sess.query(User).all()
        for user in users:
            if user.id == user_id:
                return jsonify(
                    {
                        'user': user.to_dict(),
                        'status': 200
                    }
                )
        abort(404)

    def put(self, user_id):
        if not request.json:
            abort(400)
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if args.apikey != admin:
            abort(403)
        try:
            args = parser.parse_args()
        except ValueError:
            abort(400)
        abort_if_user_not_found(user_id)
        db_sess = create_session()
        users = db_sess.query(User).all()
        for db_user in users:
            if db_user.id == user_id:
                user = db_user
        db_sess.delete(user)
        user.email = args.email
        user.set_password(args.password)
        user.nickname = args.nickname
        try:
            db_sess.add(user)
            db_sess.commit()
        except IntegrityError:
            abort(406)
        return jsonify(
            {
                'user': user.to_dict()
            }
        )

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if args.apikey != admin:
            abort(403)
        session = create_session()
        users = session.query(User).all()
        for db_user in users:
            if db_user.id == user_id:
                user = db_user
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if args.apikey not in [free, pro, admin]:
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
        if args.apikey not in [pro, admin]:
            abort(403)
        try:
            args = parser.parse_args()
        except ValueError:
            abort(400)
        session = create_session()
        user = User()
        user.email = args.email
        user.set_password(args.password)
        user.nickname = args.nickname
        try:
            session.add(user)
            session.commit()
        except IntegrityError:
            abort(406)
        return jsonify(
            {
                'user': user.to_dict()
            }
        )
