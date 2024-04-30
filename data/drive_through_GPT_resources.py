from flask_restful import Resource, reqparse
from flask import jsonify, abort
from scripts.api_keys import admin
from scripts.yan_gpt import drive_through

parser = reqparse.RequestParser()
parser.add_argument('apikey', required=True)
parser.add_argument('content', required=True)


class DriveThroughGPTResource(Resource):
    def get(self):
        try:
            args = parser.parse_args(strict=True)
        except ValueError:
            abort(400)
        if args.apikey != admin:
            abort(403)
        try:
            ask = args.content
            answer = drive_through(ask)
        except Exception as error:
            print(f"Ошибка: {error}")
            abort(500)
        return jsonify(
            {
                'content': answer
            }
        )
