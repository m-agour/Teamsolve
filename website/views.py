import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Team, Problem
from .auth import encrypt_id
from .codeforces.codeforces_api import *


views = Blueprint("views", __name__)


@views.route('/', methods=["GET", "POST"])
@login_required
def home():
    team = get_team()
    # update_user_and_mates(team)
    if not team:
        team = Team(name="", problemsNum=0, index=0, members=[], listNum=0, id=9999)
        return render_template("home.html", user=current_user, team=team, problemset=[], solved=[],
                               code=encrypt_id(team.id), team_mates=[], colors=[])
    new_day()
    sol = get_today_solved_problems_ids(current_user)
    problems = get_today_problems_list()
    team_mates = get_team_mates()
    team_mates_ind = range(len(team_mates))
    team_mates = [(team_mates[i].name, len(get_today_solved_problems_list(team_mates[i])), i) for i in team_mates_ind]
    team_mates = sorted(team_mates, key=lambda x: x[1], reverse=True)

    colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c']

    while len(colors) < len(team_mates):
        colors += colors

    return render_template("home.html", user=current_user, team=team, problems=problems, solved=sol,
                           code=encrypt_id(team.id), team_mates=team_mates, colors=colors)


@views.route('/solved')
@login_required
def solved():
    problemIndex = int(request.args.get('num'))
    new = request.args.get('type') == 'new'
    current_user.solutions.append(Problem.query.get(problemIndex))

    if not new:
        for i in list(Problem.query.filter(Problem.id == problemIndex).all()):
            current_user.dues.remove(i)
    else:
        get_team().solvedToday = True

    db.session.commit()
    return redirect(url_for('views.home'))


@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not current_user.teamId:
        return redirect(url_for('views.home'))
    if request.method == 'POST':
        if request.form['btn'] == 'change':
            name = request.form.get('name')
            try:
                number = int(request.form.get('number'))
            except:
                flash("Please enter the goal.", category='error')
                return render_template("team.html", user=current_user)

            try:
                index = int(request.form.get('index'))
            except:
                flash("Please enter the index.", category='error')
                return render_template("team.html", user=current_user)

            if not name:
                flash('Please enter a name.', category='error')

            elif number <= 0:
                flash('Problems number per day must be larger than 0.', category='error')

            elif number > 50:
                flash('Woo! take it easy champ, leave some for next month. (max is 50 per day)', category='error')

            elif index < 0:
                flash('Index must be greater than zero.', category='error')

            elif index > 7000:
                flash('Index is so large.', category='error')

            else:
                team = get_team()
                team.name = name
                team.problemsNum = number
                team.index = index
                db.session.commit()
                flash('Team settings has been modified!', category='success')
                return redirect(url_for('views.settings'))

        elif request.form['btn'] == 'leave':
            current_user.teamId = None
            db.session.commit()
            flash('You left the team!', category='success')
            return redirect(url_for('views.home'))
    return render_template("settings.html", user=current_user, team=get_team())


def get_team():
    return Team.query.get(current_user.teamId)


def get_problem_name(id):
    return Problem.query.get(id).name


def get_problems_start_id():
    return get_team().index + 1


def get_problems_number():
    return get_team().problemsNum


def get_today_problems_list():
    start = get_problems_start_id()
    end = start + get_problems_number()
    return list(Problem.query.filter(Problem.id >= start, Problem.id < end).all())


def get_today_problems_ids():
    start = get_problems_start_id()
    end = start + get_problems_number()
    return [i for i in range(start, end)]


def get_today_problems_names():
    return [get_problem_name(i) for i in get_today_problems_ids()]


def get_today_solved_problems_list(user):
    start = get_problems_start_id()
    end = start + get_problems_number()
    return user.solutions.filter(Problem.id >= start, Problem.id < end).all()


def get_today_unsolved_problems_list(user):
    return [i for i in get_today_problems_list() if i not in get_today_solved_problems_list(user)]


def get_today_solved_problems_ids(user):
    return [i.id for i in get_today_solved_problems_list(user)]


def get_team_mates():
    teamMates = list(User.query.filter_by(teamId=current_user.teamId))
    teamMates.remove(current_user)
    return teamMates


def new_day():
    team = get_team()
    update_user_and_mates(team)
    if is_new_day():
        team.updated = datetime.datetime.now().date()
        if someone_solved_today():
            set_dues()
            team.index += team.problemsNum
            team.solvedToday = False
        db.session.commit()


def set_dues():
    mates = list(User.query.filter(User.teamId == get_team().id).all())
    for i in mates:
        for j in get_today_unsolved_problems_list(i):
            i.dues.append(j)
    db.session.commit()


def is_new_day():
    return str(get_team().updated) != str(datetime.datetime.now().date())


def someone_solved_today():
    return get_team().solvedToday


def update_user_solved_problems(user):
    sol = False
    solved_on_codeforces = get_solved_problems(user.handle)
    solutions = user.solutions
    for i in solved_on_codeforces:
        problem = solutions.filter(Problem.code == i).first()
        if not problem:
            problem = Problem.query.filter(Problem.code == i).first()
            if problem:
                sol = True
                user.solutions.append(problem)
        else:
            db.session.commit()
            return sol
        db.session.commit()
        return sol


def update_user_and_mates(team):
    for i in User.query.filter_by(teamId=team.id).all():
        if update_user_solved_problems(i):
            team.solvedToday = True
            db.session.commit()


def update_all_teams():
    teams = Team.query.filter_by(teamId=current_user.teamId).all()
    for team in teams:
        update_user_and_mates(team)
