import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:/DB_NAME}'
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(str(os.getcwdb()), str(DB_NAME))
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////home/raaed/Desktop/Projects/Teamsolve/database.db"
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Team, Problem

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    # with app.app_context():
    #     if not Problem.query.get(int(1)):
    #         load_problems(app)
            # test()

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
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

def test():
    from .models import User, Team, Problem
    user1 = User(name="demon", password="hello1234e", email="dodico@com")
    user2 = User(name="demon2",password="hello1234",  email="doddico@com")
    user3 = User(name="demon3",password="hello1234",  email="dodfico@com")
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.commit()
    user1.solutions.append(Problem.query.get(1))
    user2.solutions.append(Problem.query.get(1))
    user2.solutions.append(Problem.query.get(2))
    user3.solutions.append(Problem.query.get(2))
    user2.solutions.append(Problem.query.get(3))
    db.session.commit()
