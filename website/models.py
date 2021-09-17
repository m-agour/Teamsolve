from . import db
from flask_login import UserMixin

sols = db.Table('sols',
                db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                db.Column('problem_id', db.Integer, db.ForeignKey('problem.id'))
                )

due = db.Table('due',
               db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
               db.Column('problem_id', db.Integer, db.ForeignKey('problem.id'))
               )

problem_set = db.Table('problem_set',
                       db.Column('set_id', db.Integer, db.ForeignKey('set.id')),
                       db.Column('problem_id', db.Integer, db.ForeignKey('problem.id'))
                       )


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    problemsNum = db.Column(db.Integer)
    index = db.Column(db.Integer)
    members = db.relationship('User')
    updated = db.Column(db.DATE)
    solvedToday = db.Column(db.Boolean)
    setId = db.Column(db.Integer, db.ForeignKey('set.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    handle = db.Column(db.String(30))
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    teamId = db.Column(db.Integer, db.ForeignKey('team.id'))
    darkMode = db.Column(db.Boolean)


class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    solveCount = db.Column(db.Integer)
    name = db.Column(db.String(50))
    code = db.Column(db.String(20))
    judge = db.Column(db.String(15))
    solvers = db.relationship('User', secondary=sols, backref=db.backref('solutions', lazy='dynamic'))
    leavers = db.relationship('User', secondary=due, backref=db.backref('dues', lazy='dynamic'))
    sets = db.relationship('Set', secondary=problem_set, backref=db.backref('problems', lazy='dynamic'))


class Set(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    type = db.Column(db.String(50))
    subscribers = db.relationship('Team')
