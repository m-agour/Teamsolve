import datetime
import pytz
from . import db, app
from flask_login import current_user
from .models import User, Team, Problem, Set
from .codeforces.codeforces_api import *


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
                if problem in get_dues_list(user):
                    user.dues.remove(problem)
                else:
                    sol = True
                user.solutions.append(problem)
    db.session.commit()
    return sol


def update_user_and_mates():
    lst = User.query.filter_by(teamId=1).all()
    for i in lst:
        if update_user_solved_problems(i):
            get_team().solvedToday = True
    db.session.commit()


def update_all_teams():
    teams = Team.query.filter_by(teamId=get_current_user().teamId).all()
    for team in teams:
        update_user_and_mates()


def cleanup():
    db.session.close()
    engine_container = db.get_engine(app)
    engine_container.dispose()


def join_team(team_id):
    current_user.teamId = team_id
    db.session.commit()