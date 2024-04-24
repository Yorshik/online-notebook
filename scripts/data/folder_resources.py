import datetime

from flask import jsonify, abort, request
from flask_restful import Resource, reqparse

from data.db_session import create_session
from data.folder import Folder
from data.user import User
from data.api_keys import get_api_key

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('password')

parser2 = reqparse.RequestParser()
parser2.add_argument('apikey', required=True)
parser2.add_argument('access_level', required=True)


def abort_if_folder_not_found(folder_id):
    session = create_session()
    folder = session.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        abort(404)


def abort_if_user_not_found(user_id):
    session = create_session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        abort(404)


class FoldersResource(Resource):
    def get(self, user_id, folder_id):
        abort_if_user_not_found(user_id)
        abort_if_folder_not_found(folder_id)
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if get_api_key(args.access_level) != args.apikey:
            abort(403)
        db_sess = create_session()
        folder = db_sess.query(Folder).filter(Folder.id == folder_id, Folder.owner == user_id).first()
        if not folder:
            return jsonify(
                {
                    'args': (user_id, folder_id)
                }
            )
        return jsonify(
            {
                'user': folder.to_dict(),
                'status': 200
            }
        )

    def put(self, user_id, folder_id):
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
        abort_if_folder_not_found(folder_id)
        db_sess = create_session()
        folder = db_sess.query(Folder).filter(Folder.id == folder_id, Folder.owner == user_id).first()
        if not folder:
            return jsonify({
                'args': (user_id, folder_id)
            })
        db_sess.delete(folder)
        folder.name = args.name
        folder.owner = user_id
        folder.modified_date = datetime.datetime.now()
        if args.password:
            folder.set_password(args.password)
        else:
            folder.hashed_password = 'none'
        db_sess.add(folder)
        db_sess.commit()
        return jsonify(
            {
                'edited_user': folder.to_dict()
            }
        )

    def delete(self, user_id, folder_id):
        abort_if_user_not_found(user_id)
        abort_if_folder_not_found(folder_id)
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if not (args.access_level == 'admin' and get_api_key(args.access_level) == args.apikey):
            abort(403)
        session = create_session()
        folder = session.query(Folder).filter(Folder.id == folder_id, Folder.owner == user_id).first()
        if not folder:
            return jsonify(
                {
                    'args': (user_id, folder_id)
                }
            )
        session.delete(folder)
        session.commit()
        return jsonify({'success': 'OK'})


class FoldersListResource(Resource):
    def get(self, user_id):
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if get_api_key(args.access_level) != args.apikey:
            abort(403)
        abort_if_user_not_found(user_id)
        db_sess = create_session()
        folders = db_sess.query(Folder).filter(Folder.owner == user_id).all()
        if not folders:
            return jsonify(
                {
                    'args': user_id
                }
            )
        return jsonify(
            {
                'users':
                    [item.to_dict()
                     for item in folders],
                'status': 200
            }
        )

    def post(self, user_id):
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
        abort_if_user_not_found(user_id)
        session = create_session()
        folder = Folder()
        folder.name = args.name
        folder.owner = user_id
        folder.modified_date = datetime.datetime.now()
        if args.password:
            folder.set_password(args.password)
        else:
            folder.hashed_password = 'none'
        session.add(folder)
        session.commit()
        return jsonify({'id': folder.id})
