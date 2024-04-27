from flask import jsonify, abort, request
from flask_restful import Resource, reqparse

from data.db_session import create_session
from data.folder import Folder
from data.note import Note
from data.user import User
from scripts.api_keys import free, pro, admin

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('content', required=True)
parser.add_argument('password')

parser2 = reqparse.RequestParser()
parser2.add_argument('apikey', required=True)


def abort_if_note_not_found(note_id):
    session = create_session()
    note = session.query(Note).filter(Note.id == note_id).first()
    if not note:
        abort(404)


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


def get_unique_name_of_note():
    session = create_session()
    notes = session.query(Note).all()
    max_name = max(notes, key=lambda note: note.id).name
    return f'{max_name}1'


def get_note_by_nickname(note_name):
    session = create_session()
    note = session.query(Note).filter(Note.name == note_name).first()
    if note:
        return note.id


class NotesResource(Resource):
    def get(self, user_id, folder_id, note_id):
        abort_if_user_not_found(user_id)
        abort_if_folder_not_found(folder_id)
        abort_if_note_not_found(note_id)
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if args.apikey not in [free, pro, admin]:
            abort(403)
        db_sess = create_session()
        note = db_sess.query(Note).filter((Note.id == note_id) & (Note.the_folder == folder_id)).first()
        if not note:
            return jsonify(
                {
                    'args': (user_id, folder_id, note_id)
                }
            )
        return jsonify(
            {
                'note': note.to_dict(),
                'status': 200
            }
        )

    def put(self, user_id, folder_id, note_id):
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
        abort_if_folder_not_found(folder_id)
        abort_if_note_not_found(note_id)
        db_sess = create_session()
        note = db_sess.query(Note).filter(
            (Note.id == note_id) & (Note.the_folder == folder_id)
        ).first()
        if not note:
            return jsonify(
                {
                    'args': (user_id, folder_id, note_id)
                }
            )
        # db_sess.delete(note)
        # db_sess.commit()
        note.name = args.name
        note.content = args.content
        # note.id = note_id
        if args.password:
            note.set_password(args.password)
        else:
            note.hashed_password = 'none'
        db_sess.add(note)
        db_sess.commit()
        return jsonify(
            {
                'edited_note': note.to_dict()
            }
        )

    def delete(self, user_id, folder_id, note_id):
        abort_if_user_not_found(user_id)
        abort_if_folder_not_found(folder_id)
        abort_if_note_not_found(note_id)
        try:
            args = parser2.parse_args(strict=True)
        except ValueError:
            abort(403)
        if args.apikey != admin:
            abort(403)
        session = create_session()
        note = session.query(Note).filter(
            Note.id == note_id, Note.the_folder == folder_id
        ).first()
        if not note:
            return jsonify(
                {
                    'args': (user_id, folder_id, note_id)
                }
            )
        session.delete(note)
        session.commit()
        return jsonify({'success': 'OK'})


class NotesListResource(Resource):
    def get(self, user_id, folder_id):
        try:
            args = parser2.parse_args(strict=True)
        except ValueError:
            abort(403)
        if args.apikey not in [free, pro, admin]:
            abort(403)
        db_sess = create_session()
        notes = db_sess.query(Note).filter(Note.the_folder == folder_id).all()
        if not notes:
            return jsonify(
                {
                    'args': (user_id, folder_id)
                }
            )
        return jsonify(
            {
                'notes':
                    [item.to_dict()
                     for item in notes],
                'status': 200
            }
        )

    def post(self, user_id, folder_id):
        try:
            args = parser2.parse_args()
        except ValueError:
            abort(403)
        if args.apikey not in [pro, admin]:
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
        abort_if_folder_not_found(folder_id)
        session = create_session()
        note = Note()
        note.name = args.name
        note.the_folder = folder_id
        # note.folder.owner = user_id
        note.content = args.content
        if args.password:
            note.set_password(args.password)
        else:
            note.hashed_password = 'none'
        session.add(note)
        session.commit()
        return jsonify({'id': note.id})
