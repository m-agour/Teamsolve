import datetime
from threading import Thread
import pytz
from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db, app
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Team, Problem, Set
from .auth import encrypt_id
from .codeforces.codeforces_api import *

views = Blueprint("views", __name__)


@views.route('/', methods=["GET", "POST"])
@login_required
def home():
    if request.method == 'POST':
        current_user.darkMode = not current_user.darkMode
        db.session.commit()

    team = get_team(current_user.teamId)
    # update_user_and_mates(team)
    if not team:
        team = Team(name="", problemsNum=0, index=0, members=[], listNum=0, id=9999)
        return render_template("home.html", user=current_user, team=team, problemset=[], solved=[],
                               code=encrypt_id(team.id), team_mates=[], colors=[])

    with app.app_context():
        sol = get_today_solved_problems_ids(current_user)
        problems = get_today_problems_list(current_user)
        team_mates = get_team_mates()
        team_mates_ind = range(len(team_mates))
        team_mates = [(team_mates[i].name, len(get_today_solved_problems_list(team_mates[i])), i) for i in
                      team_mates_ind]

        team_mates = sorted(team_mates, key=lambda x: x[1], reverse=True)

        colors = ['#e6194B', '#4363d8', '#9A6324', '#911eb4', '#469990', '#808000', '#000075']

        while len(colors) < len(team_mates):
            colors += colors
        team = get_team(current_user.teamId)
        new_day(team)
        update_user_and_mates(team)
        # thread = Thread(target=update_user_and_mates, args=(team,))
        # thread.daemon = True
        # thread.start()

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
        get_team(current_user.teamId).solvedToday = True

    db.session.commit()
    return redirect(url_for('views.home'))


@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not current_user.teamId:
        return redirect(url_for('views.home'))

    set_problems_count = len(Set.query.get(get_team(current_user.teamId).setId).problems.all())
    if request.method == 'POST':
        set_id = int(request.form['radio'])
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

            elif index > set_problems_count:
                flash('Index is so large.', category='error')

            else:
                team = get_team(current_user.teamId)
                team.name = name
                team.problemsNum = number
                team.index = index
                if set_id != team.setId:
                    team.setId = set_id
                    index = 1
                db.session.commit()
                flash('Team settings has been modified!', category='success')
                return redirect(url_for('views.settings'))

        elif request.form['btn'] == 'leave':
            current_user.teamId = None
            db.session.commit()
            flash('You left the team!', category='success')
            return redirect(url_for('views.home'))

    sets = Set.query.filter(Set.type != 'category').all()
    sets = [(x, len(x.problems.all())) for x in sets]
    return render_template("settings.html", user=current_user, team=get_team(current_user.teamId), sets=sets,
                           set_count=set_problems_count)


def get_team(id):
    return Team.query.get(id)


def get_problem_name(id):
    return Problem.query.get(id).name


def get_problems_start_id(user: User):
    return get_team(user.teamId).index + 1


def get_problems_number(user: User):
    return get_team(user.teamId).problemsNum


def get_today_problems_list(user: User):
    start = get_problems_start_id(user)
    end = start + get_problems_number(user)
    return list(Problem.query.filter(Problem.id >= start, Problem.id < end).all())


def get_today_problems_ids(user: User):
    start = get_problems_start_id(user)
    end = start + get_problems_number(user)
    return [i for i in range(start, end)]


def get_today_problems_names(user: User):
    return [get_problem_name(i) for i in get_today_problems_ids(user)]


def get_today_solved_problems_list(user: User):
    start = get_problems_start_id(user)
    end = start + get_problems_number(user)
    return user.solutions.filter(Problem.id >= start, Problem.id < end).all()


def get_today_unsolved_problems_list(user: User):
    alle = get_today_problems_list(user)
    sol = get_today_solved_problems_list(user)
    return [i for i in alle if i not in sol]


def get_today_solved_problems_ids(user: User):
    return [i.id for i in get_today_solved_problems_list(user)]


def get_team_mates():
    teamMates = list(User.query.filter_by(teamId=current_user.teamId))
    teamMates.remove(current_user)
    return teamMates


def new_day(team):
    with app.app_context():
        if is_new_day(team):
            team.updated = datetime.datetime.now().date()
            # if someone_solved_today(team):
            set_dues(team)
            team.index += team.problemsNum
            team.solvedToday = False
            db.session.commit()


def set_dues(team):
    mates = list(User.query.filter(User.teamId == team.id).all())
    for i in mates:
        for j in get_today_unsolved_problems_list(i):
            i.dues.append(j)
    db.session.commit()


def is_new_day(team):
    tz = pytz.timezone('Africa/Cairo')
    date = datetime.datetime.now(tz).date()
    return str(team.updated) != str(date)


def someone_solved_today(team):
    return team.solvedToday


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
    db.session.commit()
    return sol


def update_user_and_mates(team):
    with app.app_context():
        lst = User.query.filter_by(teamId=1).all()
        for i in lst:
            if update_user_solved_problems(i):
                team.solvedToday = True
        db.session.commit()


def update_all_teams():
    with app.app_context():
        teams = Team.query.filter_by(teamId=current_user.teamId).all()
        for team in teams:
            update_user_and_mates(team)
