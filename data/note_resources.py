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
    db_notes = session.query(Note).all()
    for db_note in db_notes:
        if db_note.id == note_id:
            note = db_note
            break
    if not note:
        abort(404)


def get_unique_name_of_note(user_id, folder_id):
    t1 = time.time()
    session = create_session()
    notes = []
    db_notes = session.query(Note).all()
    for note in db_notes:
        if note.the_folder == folder_id:
            notes.append(note)
    users = session.query(User).all()
    for db_user in users:
        if db_user.id == user_id:
            user = db_user
            break
    if notes:
        new_name = f'{user.nickname} note {len(notes) + 1}'
    else:
        new_name = f'{user.nickname} note 1'
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
        notes = db_sess.query(Note).all()
        for db_note in notes:
            if db_note.id == note_id:
                note = db_note
                break
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
        notes = db_sess.query(Note).all()
        for db_note in notes:
            if db_note.id == note_id:
                note = db_note
                break
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
        notes = session.query(Note).all()
        for db_note in notes:
            if db_note.id == note_id:
                note = db_note
                break
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
        notes = []
        db_notes = db_sess.query(Note).all()
        for db_note in db_notes:
            if db_note.the_folder == folder_id:
                notes.append(db_note)
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
