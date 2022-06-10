from flask import request, jsonify  # type:ignore
import jwt  # type:ignore
from functools import wraps
from src.main.models import User  # type:ignore


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            print(token)
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401
        try:
            current_user = User.verify_token(token)
        except jwt.exceptions.InvalidSignatureError as e:
            return jsonify({'message' : str(e)}), 401
        except jwt.exceptions.ExpiredSignatureError as e:
            return jsonify({'message' : str(e)}), 401

        if current_user is None:
            return jsonify({'message' : 'User is None!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated
