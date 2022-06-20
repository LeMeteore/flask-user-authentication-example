import pathlib

current_folder = pathlib.Path(__file__).parent.resolve()  # current directory
database_path = current_folder / "datas" / "test_db.sqlite"
database_uri = "sqlite:///{}".format(database_path)

DATABASE_PATH = database_uri
SQLALCHEMY_DATABASE_URI = database_uri
SQLALCHEMY_TRACK_MODIFICATIONS = False

ENV = "development"
TESTING = True
DEBUG = True
FLASK_ENV = 'development'
SECRET_KEY = 'GDtfDCFYjD'
