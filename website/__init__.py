import datetime
import json

import pytz
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from .codeforces.codeforces_api import *

db = SQLAlchemy()

app = Flask(__name__)

DB_NAME = "database.db"

sqlite = False


def create_app():
    global app

    if not sqlite:
        # app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
        app.config['SECRET_KEY'] = "l_uz9HnfFDGC7XnLFjs8yAVrGDBPlRdJ"
        app.config[
            'SQLALCHEMY_DATABASE_URI'] = "postgresql://ttnwfvvb:l_uz9HnfFDGC7XnLFjs8yAVrGDBPlRdJ@tai.db.elephantsql.com/ttnwfvvb"

    else:
        app.config['SECRET_KEY'] = 'hello darkness my old friend'
        PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(PROJECT_ROOT, 'database.db')

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Team, Problem, Set

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
            load_problems()
            load_sets()
            set_my_team()

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not sqlite:
        if not os.path.exists('website/' + DB_NAME):
            db.create_all(app=app)
            print('Created Database!')


def load_problems():
    from website.models import Problem, Set
    problems = generate_ordered_problems_id_name_solved()
    new_set = Set(name='Top solved', type='main')
    db.session.add(new_set)

    for i in range(len(problems)):
        name = problems[i][1]
        if len(name) > 50:
            name = name[:45] + '...'
        prob = Problem(code=problems[i][0], name=name, rating=problems[i][2], solveCount=problems[i][3],
                       judge='Codeforces')
        db.session.add(prob)
        new_set.problems.append(prob)
    db.session.commit()


def load_sets():
    from .models import User, Team, Problem, Set
    sets = json.load(open('website/codeforces/sets.json'))
    for s in sets:
        new_set = Set(name=s['name'], type=s['type'])
        db.session.add(new_set)
        for prob in s['set']:
            name = prob['name']
            code = prob['code']
            judge = prob['judge']

            if len(name) > 50:
                name = name[:45] + '...'

            problem = Problem.query.filter(Problem.code == code, Problem.judge == judge).first()

            if problem:
                ...
            else:
                problem = Problem(code=prob['code'], name=name, rating=9999, solveCount=0,
                               judge='Codeforces')
                db.session.add(problem)

            new_set.problems.append(problem)

    db.session.commit()


def set_my_team():
    from .models import User, Team, Problem, Set
    tz = pytz.timezone('Africa/Cairo')
    date = datetime.datetime.now(tz).date()
    my_team = Team(name='ERROR', problemsNum=3, index=48, setId=0, updated=date, solvedToday=True, members=[])
    db.session.add(my_team)
    user1 = User(email='mohamedelfeky250@gmail.com', handle='Mohamed.-.Elfeky', password='sha256$FgzKH4Qn$6759112c8d461024fc4a240923c9de3ec0641452e0ea9ea3a3657a5da5bc652b', name='Mohamed Abdelfatah Elfeky', teamId='1', darkMode=False)
    user2 = User(email='mo.aggour@gmail.com', handle='M_Agour', password='sha256$TM30OmFM$6eeefef0ac53ade11375cb35d243949e0ff428589b19b3768df13b4d4d931271', name='Mohamed Nagy', teamId='1',  darkMode=False)
    user3 = User(email='mostafahussinelsayed@gmail.com', handle='Mostafa_Hu', password='sha256$jcPUKg0q$c4be88c1476b43749c93f0b8f31fc8b3919b4a63494fb5bfb9236cf266ede997', name='Mustafa Hussin', teamId='1',  darkMode=False)
    db.session.add(user2)
    db.session.add(user1)
    db.session.add(user3)
    my_team.members.append(user2)
    my_team.members.append(user1)
    my_team.members.append(user3)
    db.session.commit()