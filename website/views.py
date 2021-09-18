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
    with app.app_context():
        if request.method == 'POST':
            current_user.darkMode = not current_user.darkMode
            db.session.commit()

        team = get_team()
        user = User.query.get(current_user.id)
        # update_user_and_mates(team)
        if not team:
            team = Team(name="", problemsNum=0, index=0, members=[], listNum=0, id=9999)
            return render_template("home.html", user=user, team=team, problemset=[], solved=[],
                                   code=encrypt_id(team.id), team_mates=[], colors=[])

        sol = get_today_solved_problems_ids(get_current_user())
        problems = get_today_problems_list()
        team_mates = get_team_mates()
        team_mates_ind = range(len(team_mates))
        team_mates = [(team_mates[i].name, len(get_today_solved_problems_list(team_mates[i])), i) for i in
                      team_mates_ind]

        team_mates = sorted(team_mates, key=lambda x: x[1], reverse=True)

        colors = ['#e6194B', '#4363d8', '#9A6324', '#911eb4', '#469990', '#808000', '#000075']

        while len(colors) < len(team_mates):
            colors += colors

        team = get_team()
        dues = get_dues_list(get_current_user())

        update_user_and_mates(team)
        new_day(team)

        # thread = Thread(target=update_user_and_mates, args=(team,))
        # thread.daemon = True
        # thread.start()
        return render_template("home.html", user=user, team=team, problems=problems, solved=sol,
                               code=encrypt_id(team.id), team_mates=team_mates, colors=colors, dues=dues)


@views.route('/solved')
@login_required
def solved():
    problemIndex = int(request.args.get('num'))
    new = request.args.get('type') == 'new'
    get_current_user().solutions.append(Problem.query.get(problemIndex))

    if not new:
        for i in list(Problem.query.filter(Problem.id == problemIndex).all()):
            get_current_user().dues.remove(i)
    else:
        get_team().solvedToday = True

    db.session.commit()
    return redirect(url_for('views.home'))


@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not get_current_user().teamId:
        return redirect(url_for('views.home'))

    set_problems_count = len(Set.query.get(get_team().setId).problems.all())
    if request.method == 'POST':
        set_id = int(request.form['radio'])
        if request.form['btn'] == 'change':
            name = request.form.get('name')
            try:
                number = int(request.form.get('number'))
            except:
                flash("Please enter the goal.", category='error')
                return render_template("team.html", user=get_current_user())

            try:
                index = int(request.form.get('index'))
            except:
                flash("Please enter the index.", category='error')
                return render_template("team.html", user=get_current_user())

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
                team = get_team()
                team.name = name
                team.problemsNum = number
                team.index = index
                if set_id != team.setId:
                    team.setId = set_id
                    team.index = 0
                db.session.commit()
                flash('Team settings has been modified!', category='success')
                return redirect(url_for('views.settings'))

        elif request.form['btn'] == 'leave':
            get_current_user().teamId = None
            db.session.commit()
            flash('You left the team!', category='success')
            return redirect(url_for('views.home'))

    sets = Set.query.filter(Set.type != 'category').all()
    sets = [(x, len(x.problems.all())) for x in sets]
    return render_template("settings.html", user=get_current_user(), team=get_team(), sets=sets,
                           set_count=set_problems_count)


def get_team():
    return Team.query.get(get_current_user().teamId)


def get_current_user():
    return User.query.get(current_user.id)
    # return current_user


def get_problem_name(problem_id):
    return Problem.query.get(problem_id).name


def get_problems_start_id():
    return get_team().index


def get_problems_number():
    return get_team().problemsNum


def get_today_problems_list():
    setId = get_team().setId
    start = get_problems_start_id()
    end = start + get_problems_number()
    if setId != 1:
        return list(Set.query.get(setId).problems.filter_by().all())[start:end]
    else:
        return list(Problem.query.filter(Problem.id >= start + 1, Problem.id < end + 1).all())


def get_today_problems_ids():
    start = get_problems_start_id()
    end = start + get_problems_number()
    return [i for i in range(start, end)]


def get_today_problems_names():
    return [get_problem_name(i) for i in get_today_problems_ids()]


def get_today_solved_problems_list(user: User):
    today = get_today_problems_list()
    solved_overall = list(user.solutions.filter().all())
    solved_today = [x for x in today if x in solved_overall]
    return solved_today


def get_today_unsolved_problems_list(user: User):
    alle = get_today_problems_list()
    sol = get_today_solved_problems_list(user)
    return [i for i in alle if i not in sol]


def get_today_solved_problems_ids(user: User):
    return [i.id for i in get_today_solved_problems_list(user)]


def get_team_mates():
    teamMates = list(User.query.filter_by(teamId=get_current_user().teamId))
    teamMates.remove(get_current_user())
    return teamMates


def new_day(team):
    team = get_team()
    if is_new_day(team):
        if someone_solved_today(team):
            tz = pytz.timezone('Africa/Cairo')
            date = datetime.datetime.now(tz).date()
            set_dues(team)
            team.index += team.problemsNum
            team.solvedToday = False
            team.updated = date
            db.session.commit()



def set_dues(team):
    members = list(User.query.filter(User.teamId == team.id).all())
    for i in members:
        for j in get_today_unsolved_problems_list(i):
            i.dues.append(j)


def is_new_day(team):
    tz = pytz.timezone('Africa/Cairo')
    date = datetime.datetime.now(tz).date()
    return str(team.updated) != str(date)


def someone_solved_today(team):
    return team.solvedToday


def get_dues_list(user):
    return list(user.dues.filter().all())


def update_user_solved_problems(user):
    sol = False
    solved_on_codeforces = get_solved_problems(user.handle)
    solutions = user.solutions
    for i in solved_on_codeforces:
        problem = solutions.filter(Problem.code == i).first()
        if not problem:
            problem = Problem.query.filter(Problem.code == i).first()
            if problem:
                if problem not in get_dues_list(user):
                    sol = True
                user.solutions.append(problem)
    db.session.commit()
    return sol


def update_user_and_mates(team):
    lst = User.query.filter_by(teamId=1).all()
    for i in lst:
        if update_user_solved_problems(i):
            get_team().solvedToday = True
    db.session.commit()


def update_all_teams():
    teams = Team.query.filter_by(teamId=get_current_user().teamId).all()
    for team in teams:
        update_user_and_mates(team)
