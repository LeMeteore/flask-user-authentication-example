import json
import pytest  # type:ignore
import pathlib  # type:ignore
from src.main import create_app  # type:ignore
from src.main.models import User, Role, Data  # type:ignore
from base64 import b64encode
import time


def get_api_headers(username, password):
    return {
        'Authorization':
        'Basic ' + b64encode(
            (username + ':' + password).encode('utf-8')).decode('utf-8'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def application(request):
    app, db, api, bcryp = create_app("tests/tests_configuration.py")
    # db.session.auto_commit = True
    ctx = app.app_context()
    # make current context available everywhere during the tests
    ctx.push()
    db.create_all()
    r1 = Role(name="admin")
    r1.save()
    r2 = Role(name="superadmin")
    r2.save()
    User(username="username1", password="password1").save()
    User(username="username2", password="password2", role_id=r1.rid).save() # can get users
    User(username="username3", password="password3", role_id=r2.rid).save() # can post users
    Data(json_data={"name": "foo", "firstname": "bar"}).save()

    def teardown():
        # delete database file
        db.session.remove()
        db.drop_all()
        pathlib.Path(app.config["DATABASE_PATH"].split(":")[-1]).unlink()
        # delete context
        ctx.pop()

    # call teardown function after the request is finished
    request.addfinalizer(teardown)
    return app


@pytest.fixture
def client(application):
    client = application.test_client()
    return client


def test_get_datas(client):
    with client.get('/datas') as r:
        assert r.status_code == 200
        assert r.status_code == 200
        assert isinstance(r.json, list)
        assert len(r.json) > 0
        assert "json_data" in r.json[0].keys()
        assert r.json[0]["json_data"] == {'name': 'foo', 'firstname': 'bar'}


def test_post_token_is_missing(client):
    with client.post('/datas') as r:
        assert r.status_code == 401
        assert r.json == {'message': 'Token is missing'}


def test_bad_login(client):
    with client.post('/login',
                     headers=get_api_headers("badusername", "badsecret")) as r:
        assert r.status_code == 401
        assert r.json == {'message': 'No matching user found'}


def test_good_login(client):
    with client.post('/login',
                     headers=get_api_headers("username1", "password1")) as r:
        assert r.status_code == 200
        assert "token" in r.json
        assert isinstance(r.json["token"], str)


def test_post_datas(client):
    with client.post('/login',
                     headers=get_api_headers("username1", "password1")) as r:
        token = r.json["token"]

    with client.post(
            '/datas',
            headers={"x-access-token": token, 'Content-Type': 'application/json'},
            data=json.dumps({"age": "43"})) as r:
        assert r.status_code == 201
        assert r.json == {'data': {'age': '43'}, 'message': 'New data created!'}


def test_invalid_signature(client):
    with client.post('/login',
                     headers=get_api_headers("username1", "password1")) as r:
        token = r.json["token"]

    with client.get(
            '/users',
            headers={"x-access-token": token+'e'}) as r:
        assert r.status_code == 401
        assert r.json == {'message': 'Signature verification failed'}


def test_expired_signature(client):
    with client.post('/login',
                     headers=get_api_headers("username1", "password1")) as r:
        token = r.json["token"]
    time.sleep(61) # how to better simulate this ???
    with client.get(
            '/users',
            headers={"x-access-token": token, 'Content-Type': 'application/json'}) as r:
        assert r.status_code == 401
        assert r.json == {'message': 'Signature has expired'}


def test_get_users_with_wrong_role(client):
    with client.post('/login',
                     headers=get_api_headers("username1", "password1")) as r:
        token = r.json["token"]
    # trying to get users but I don't have the right role
    with client.get(
            '/users',
            headers={"x-access-token": token}) as r:
        assert r.status_code == 401
        assert r.json == {'message': 'You do not have the required role to perform this operation'}


def test_get_users_with_right_role(client):
    with client.post('/login',
                     headers=get_api_headers("username2", "password2")) as r:
        token = r.json["token"]
    # trying to get users but I have the right role
    with client.get(
            '/users',
            headers={"x-access-token": token, 'Content-Type': 'application/json'}) as r:
        assert r.status_code == 200
        assert isinstance(r.json, list)
        assert len(r.json) > 0
        assert len(r.json) == 3


def test_post_users(client):
    with client.post('/login',
                     headers=get_api_headers("username3", "password3")) as r:
        token = r.json["token"]
    # trying to post users with the right role
    with client.post(
            '/users',
            headers={"x-access-token": token, 'Content-Type': 'application/json'},
            data=json.dumps({"username": "newuser", "password": "43"})) as r:
        assert r.status_code == 201
        assert "message" in r.json.keys()
        assert "data" in r.json.keys()
        assert r.json["message"] == "New data created!"
