import datetime

import sqlalchemy
from flask import jsonify, abort, request
from flask_restful import Resource, reqparse
import time
from data.db_session import create_session
from data.folder import Folder
from data.user import User
from scripts.api_keys import free, pro, admin
import re

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('password')

parser2 = reqparse.RequestParser()
parser2.add_argument('apikey', required=True)


def match_name(string: str, pattern: str) -> bool:
    pattern = pattern.replace("<int>", r"\d+").replace("<str>", r".+")
    return bool(re.match(pattern, string))


def abort_if_folder_not_found(folder_id):
    session = create_session()
    folder = session.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        abort(404)


def get_unique_name_of_folder(user_id):
    t1 = time.time()
    session = create_session()
    folders = session.query(Folder).filter(Folder.owner == user_id).all()
    user = session.query(User).filter(User.id == user_id).first()
    if folders:
        max_name = max(folders, key=lambda note: (note.id, match_name(note.name, f'{user.nickname} folder <int>'))).name
    else:
        max_name = f'{user.nickname} folder 0'
    new_name = f'{max_name.split()[0]} {max_name.split()[1]} {str(int(max_name.split()[2]) + 1)}'
    t2 = time.time()
    print(t2 - t1, f'get unique name of folder, user id: {user_id}')
    return new_name


class FoldersResource(Resource):
    def get(self, folder_id):
        t1 = time.time()
        abort_if_folder_not_found(folder_id)
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if args.apikey not in [free, pro, admin]:
            abort(403)
        db_sess = create_session()
        folder = db_sess.query(Folder).filter(Folder.id == folder_id).first()
        if not folder:
            abort(422)
        t2 = time.time()
        print(t2 - t1, f'get request, folder id: {folder_id}')
        return jsonify(
            {
                'user': folder.to_dict(),
                'status': 200
            }
        )

    def put(self, folder_id):
        t1 = time.time()
        if not request.json:
            abort(400)
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(400)
        if args.apikey != admin:
            abort(403)
        try:
            args = parser.parse_args()
        except ValueError:
            abort(400)
        abort_if_folder_not_found(folder_id)
        db_sess = create_session()
        folder = db_sess.query(Folder).filter(Folder.id == folder_id).first()
        if not folder:
            abort(422)
        db_sess.delete(folder)
        folder.name = args.name
        folder.modified_date = datetime.datetime.now()
        if args.password:
            folder.set_password(args.password)
        else:
            folder.hashed_password = 'none'
        db_sess.add(folder)
        db_sess.commit()
        t2 = time.time()
        print(t2 - t1, f'put request, folder id: {folder_id}')
        return jsonify(
            {
                'edited_folder': folder.to_dict()
            }
        )

    def delete(self, folder_id):
        t1 = time.time()
        abort_if_folder_not_found(folder_id)
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if args.apikey != admin:
            abort(403)
        session = create_session()
        folder = session.query(Folder).filter(Folder.id == folder_id).first()
        if not folder:
            abort(422)
        session.delete(folder)
        session.commit()
        t2 = time.time()
        print(t2 - t1, f'delete request, folder id: {folder_id}')
        return jsonify({'success': 'OK'})


class FoldersListResource(Resource):
    def get(self, user_id):
        t1 = time.time()
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if args.apikey not in [free, pro, admin]:
            abort(403)
        db_sess = create_session()
        try:
            folders = db_sess.query(Folder).filter(Folder.owner == user_id).all()
        except sqlalchemy.exc.TimeoutError:
            print(user_id)
        if not folders:
            abort(422)
        t2 = time.time()
        print(t2 - t1, f'many get request, user id: {user_id}')
        return jsonify(
            {
                'folders':
                    [item.to_dict()
                     for item in folders],
                'status': 200
            }
        )

    def post(self, user_id):
        t1 = time.time()
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if args.apikey not in [pro, admin]:
            abort(403)
        try:
            args = parser.parse_args()
        except ValueError:
            abort(422)
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
        t2 = time.time()
        print(t2 - t1, f'post request, user id: {user_id}')
        return jsonify({'id': folder.id})
