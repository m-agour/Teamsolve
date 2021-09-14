import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
import psycopg2

db = SQLAlchemy()
DB_NAME = "database.db"

sqlite = False


def create_app():
    app = Flask(__name__)
    if not sqlite:
        # app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
        app.config['SECRET_KEY'] = "l_uz9HnfFDGC7XnLFjs8yAVrGDBPlRdJ"
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ttnwfvvb:l_uz9HnfFDGC7XnLFjs8yAVrGDBPlRdJ@tai.db.elephantsql.com/ttnwfvvb"

    else:
        app.config['SECRET_KEY'] = 'hello darkness my old friend'
        PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(PROJECT_ROOT, 'database.db')

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Team, Problem

    try:
        db.create_all(app=app)
    except:
        ...
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    with app.app_context():
        if not Problem.query.get(int(1)):
            load_problems(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not sqlite:
        if not os.path.exists('website/' + DB_NAME):
            db.create_all(app=app)
            print('Created Database!')


def load_problems(app):
    from website.models import Problem
    problems = json.load(open("assets/problems.json", "r"))
    for i in range(len(problems)):
        prob = Problem(name=problems[i])
        db.session.add(prob)
    db.session.commit()


