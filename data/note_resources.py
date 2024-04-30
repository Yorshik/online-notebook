import re
import time

from flask import jsonify, abort, request
from flask_restful import Resource, reqparse

from data.db_session import create_session
from data.note import Note
from data.user import User
from scripts.api_keys import free, pro, admin

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('content', required=True)
parser.add_argument('password')

parser2 = reqparse.RequestParser()
parser2.add_argument('apikey', required=True)


def match_name(string: str, pattern: str) -> bool:
    pattern = pattern.replace("<int>", r"\d+").replace("<str>", r".+")
    return bool(re.match(pattern, string))


def abort_if_note_not_found(note_id):
    session = create_session()
    note = session.query(Note).filter(Note.id == note_id).first()
    if not note:
        abort(404)


def get_unique_name_of_note(user_id, folder_id):
    t1 = time.time()
    session = create_session()
    notes = session.query(Note).filter(Note.the_folder == folder_id).all()
    user = session.query(User).filter(User.id == user_id).first()
    if notes:
        max_name = max(notes, key=lambda note: (note.id, match_name(note.name, f'{user.nickname} note <int>'))).name
    else:
        max_name = f'{user.nickname} note 0'
    new_name = f'{max_name.split()[0]} {max_name.split()[1]} {str(int(max_name.split()[2]) + 1)}'
    t2 = time.time()
    print(t2 - t1, f'get unique name of note, user id: {user_id}, folder id: {folder_id}')
    return new_name


class NotesResource(Resource):
    def get(self, note_id):
        t1 = time.time()
        abort_if_note_not_found(note_id)
        try:
            args = parser2.parse_args(strict=True)
        except ValueError:
            abort(400)
        if args.apikey not in [free, pro, admin]:
            abort(403)
        db_sess = create_session()
        note = db_sess.query(Note).filter(Note.id == note_id).first()
        if not note:
            abort(422)
        t2 = time.time()
        print(t2 - t1, f'get request, note id: {note_id}')
        return jsonify(
            {
                'note': note.to_dict(),
                'status': 200
            }
        )

    def put(self, note_id):
        t1 = time.time()
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
        abort_if_note_not_found(note_id)
        db_sess = create_session()
        note = db_sess.query(Note).filter(Note.id == note_id).first()
        if not note:
            abort(422)
        db_sess.delete(note)
        note.name = args.name
        note.content = args.content
        if args.password:
            note.set_password(args.password)
        else:
            note.hashed_password = 'none'
        db_sess.add(note)
        db_sess.commit()
        t2 = time.time()
        print(t2 - t1, f'put request, note id: {note_id}')
        return jsonify(
            {
                'note': note.to_dict()
            }
        )

    def delete(self, note_id):
        t1 = time.time()
        abort_if_note_not_found(note_id)
        try:
            args = parser2.parse_args(strict=True)
        except ValueError:
            abort(403)
        if args.apikey != admin:
            abort(403)
        session = create_session()
        note = session.query(Note).filter(Note.id == note_id).first()
        if not note:
            abort(422)
        session.delete(note)
        session.commit()
        t2 = time.time()
        print(t2 - t1, f'delete request, note id: {note_id}')
        return jsonify({'success': 'OK'})


class NotesListResource(Resource):
    def get(self, folder_id):
        t1 = time.time()
        try:
            args = parser2.parse_args(strict=True)
        except ValueError:
            abort(403)
        if args.apikey not in [free, pro, admin]:
            abort(403)
        db_sess = create_session()
        notes = db_sess.query(Note).filter(Note.the_folder == folder_id).all()
        if not notes:
            abort(422)
        t2 = time.time()
        print(t2 - t1, f'many get request, folder id: {folder_id}')
        return jsonify(
            {
                'notes':
                    [item.to_dict()
                     for item in notes],
                'status': 200
            }
        )

    def post(self, folder_id):
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
            abort(400)
        session = create_session()
        note = Note()
        note.name = args.name
        note.the_folder = folder_id
        note.content = args.content
        if args.password:
            note.set_password(args.password)
        else:
            note.hashed_password = 'none'
        session.add(note)
        session.commit()
        t2 = time.time()
        print(t2 - t1, f'post request, folder id: {folder_id}')
        return jsonify({'note': note.to_dict()})
