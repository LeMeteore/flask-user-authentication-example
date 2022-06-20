from flask import Flask  # type:ignore
from flask_restful import Api  # type:ignore
from flask_bcrypt import Bcrypt  # type:ignore
from flask_sqlalchemy import SQLAlchemy  # type:ignore
from flask_marshmallow import Marshmallow  # type:ignore

db = SQLAlchemy()
ma = Marshmallow(db)

def create_app(config_filename=None):
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    if (app.config["ENV"] == 'development'):
        app.config.from_object('src.config.base.Config')

    elif (app.config["ENV"] == 'production'):
        app.config.from_object('src.config.base.ProdConfig')

    else:
        raise RuntimeError('Unknown environment setting provided.')

    if config_filename:
        app.config.from_pyfile(config_filename)
    db.init_app(app)
    api = Api(app)
    bcrypt = Bcrypt(app)

    from src.main.resources import DataResource  # type:ignore
    api.add_resource(DataResource,
                     '/datas/',
                     '/datas/<string:eid>')

    from src.main.resources import UserResource  # type:ignore
    api.add_resource(UserResource,
                     '/users/',
                     '/users/<string:pubid>')

    with app.app_context():
        # import blueprints
        from src.main.views import auth as auth_bp  # type:ignore
        # Register Blueprint
        app.register_blueprint(auth_bp)

        db.create_all()

        return app, db, api, bcrypt
