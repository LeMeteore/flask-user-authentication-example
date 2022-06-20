from flask import request, jsonify, make_response  # type:ignore
import jwt  # type:ignore
from functools import wraps
from src.main.models import User, Role  # type:ignore


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            # return jsonify({'message' : 'Token is missing!'}), 401
            resp = make_response({"message": "Token is missing"}, 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
            return resp
        try:
            current_user = User.verify_token(token)
        except jwt.exceptions.InvalidSignatureError as e:
            # return jsonify({'message' : str(e)}), 401
            resp = make_response({"message": str(e)}, 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
            return resp
        except jwt.exceptions.ExpiredSignatureError as e:
            # return jsonify({'message' : str(e)}), 401
            resp = make_response({"message": str(e)}, 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
            return resp
        if current_user is None:
            # return jsonify({'message' : 'User is None!'}), 401
            resp = make_response({"message": "No matching user found"}, 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
            return resp
        return f(current_user, *args, **kwargs)
    return decorated


def token_and_role_required(required_role):
    def outer(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if 'x-access-token' in request.headers:
                token = request.headers['x-access-token']
            if not token:
                # return jsonify({'message' : 'Token is missing!'}), 401
                resp = make_response({"message": "Token is missing"}, 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
                return resp
            try:
                current_user = User.verify_token(token)
            except jwt.exceptions.InvalidSignatureError as e:
                # return jsonify({'message' : str(e)}), 401
                resp = make_response({"message": str(e)}, 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
                return resp
            except jwt.exceptions.ExpiredSignatureError as e:
                # return jsonify({'message' : str(e)}), 401
                resp = make_response({"message": str(e)}, 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
                return resp
            if current_user is None:
                # return jsonify({'message' : 'User is None!'}), 401
                resp = make_response({"message": "No matching user found"}, 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
                return resp
            # now we check for the role
            current_user_role = Role.query.filter_by(rid=current_user.role_id).first()
            if current_user_role:
                if current_user_role.name == required_role:
                    return f(current_user, *args, **kwargs)
            else:
                resp = make_response({"message": "You do not have the required role to perform this operation"}, 401)
                return resp
        return decorated
    return outer
