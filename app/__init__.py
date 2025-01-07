from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger
import os

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret-key')
    app.config['SWAGGER'] = {
        'title': 'Transaction API',
        'uiversion': 3
    }
    app.config['SESSION_TYPE'] = 'filesystem'

    db.init_app(app)
    migrate.init_app(app, db)
    Swagger(app)

    from .routes import dashboard, users, transactions
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(transactions.bp)

    return app
