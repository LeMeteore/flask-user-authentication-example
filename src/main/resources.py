import json
from flask import request, jsonify, make_response  # type:ignore
from flask_restful import Resource  # type:ignore

from src.main import db  # type:ignore
from src.main.models import Data  # type:ignore
from src.main.schemas import data_schema, datas_schema  # type:ignore
from src.main.utils import token_required, token_and_role_required  # type:ignore
from src.main.models import User  # type:ignore


class DataResource(Resource):
    def get(self, eid=None):
        if eid:
            data = data_schema.dump(Data.query.get_or_404(eid))
        else:
            data = datas_schema.dump(Data.query.all())
        # return jsonify(data)
        return data

    @token_required
    def post(self, current_user):
        fooo = request.data.decode("utf-8") # I shoould do request.get_json()
        json_data = json.loads(fooo)
        data = Data(json_data=json_data)
        data.save()

        resp = make_response(
            {'message': 'New data created!', "data": json_data}, 201
        )
        return resp


class UserResource(Resource):

    @token_and_role_required("admin")
    def get(self, current_user, pubid=None):
        if pubid:
            users = User.query.filter_by(pubid=pubid).first()
        else:
            users = User.query.all()

        output = []
        for user in users:
            user_data = {}
            user_data['pubid'] = user.pubid
            user_data['username'] = user.username
            output.append(user_data)
        return output

    @token_and_role_required("superadmin")
    def post(self, current_user):
        data = request.get_json()
        new_user = User(username=data['username'], password=data['password'])
        new_user.save()

        # return jsonify({'message': 'New user created!'}), 201
        # Object of type Response is not JSON serializable

        resp = make_response(
            {'message': 'New data created!', "data": data}, 201
        )
        return resp
