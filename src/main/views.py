from flask import make_response, request, jsonify, Blueprint  # type:ignore
from src.main.models import User  # type:ignore
from src.main.utils import token_required  # type:ignore

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=["POST"])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        resp = make_response(
            {"message": "Could not verify"}, 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'}
        )
        resp.headers['WWW-Authenticate'] = 'Basic realm="Login required!"'
        return resp

    user = User.query.filter_by(username=auth.username).first()

    if not user:
        resp = make_response(
            {"message": "No matching user found"}, 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'}
        )
        resp.headers['WWW-Authenticate'] = 'Basic realm="Login required!"'
        return resp

    if user.verify_password(auth.password):
        token = user.generate_token()
        return jsonify({'token' : token})

    resp = make_response(
        {"message": "No auth, no user, nothing"}, 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'}
    )
    resp.headers['WWW-Authenticate'] = 'Basic realm="Login required!"'
    return resp



# @auth.route('/user', methods=['GET'])
# @token_required
# def get_all_users(current_user):
#     if not current_user.is_admin:
#         return jsonify({'message' : 'Cannot perform that function!'})
#     users = User.query.all()
#     output = []
#     for user in users:
#         user_data = {}
#         user_data['pubid'] = user.pubid
#         user_data['username'] = user.username
#         user_data['is_admin'] = user.is_admin()
#         output.append(user_data)
#     return jsonify({'users' : output})


# @auth.route('/user/<pubid>', methods=['GET'])
# @token_required
# def get_one_user(current_user, pubid):
#     if not current_user.is_admin:
#         return jsonify({'message' : 'Cannot perform that function!'})

#     user = User.query.filter_by(pubid=pubid).first()

#     if not user:
#         return jsonify({'message' : 'No user found!'})

#     user_data = {}
#     user_data['pubid'] = user.pubid
#     user_data['username'] = user.username
#     user_data['is_admin'] = user.is_admin()

#     return jsonify({'user' : user_data})


# @auth.route('/user', methods=['POST'])
# @token_required
# def create_user(current_user):
#     if not current_user.is_admin:
#         return jsonify({'message' : 'Cannot perform that function!'})

#     data = request.get_json()

#     new_user = User(username=data['username'], password=data['password'])
#     new_user.save()

#     return jsonify({'message' : 'New user created!'}), 201
