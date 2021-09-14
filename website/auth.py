import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Team
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user, user_logged_out

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    logged_in = True
    try:
        x = current_user.id
    except:
        logged_in = False

    if logged_in:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/create-team', methods=['GET', 'POST'])
@login_required
def createTeam():
    if current_user.teamId:
        flash("You have already joined a team.", category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        name = request.form.get('name')
        try:
            number = int(request.form.get('number'))
        except:
            flash("Please enter your goal.", category='error')
            return render_template("team.html", user=current_user)

        if not name:
            flash('Please enter the name.', category='error')

        if current_user.teamId:
            flash("You have already joined a team.", category='error')
            return redirect(url_for('views.home'))

        elif number <= 0:
            flash('Problems number per day must be larger than 0.', category='error')

        elif number > 50:
            flash('Woo! take it easy champ, leave some for next month. (max is 50 per day)', category='error')

        else:
            new_team = Team(name=name, problemsNum=number, index=0, members=[current_user], listNum=0,
                            solvedToday=False, updated=datetime.datetime.now().date())
            db.session.add(new_team)
            db.session.commit()
            join_team(new_team.id)
            flash('Team created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("team.html", user=current_user)


@auth.route('/join-team', methods=['GET', 'POST'])
@login_required
def joinTeam():
    if request.method == 'POST':
        code = request.form.get('code')
        print(decrypt_id(code))
        if not code:
            flash('Please enter the invitation code.', category='error')

        elif not Team.query.filter_by(id=decrypt_id(code)).first():
            flash('Please enter a valid invitation code.', category='error')

        else:
            team_id = decrypt_id(code)
            join_team(team_id)
            flash('Joined Team!', category='success')
            return redirect(url_for('views.home'))

    return render_template("join-team.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    email = ""
    name = ""

    if is_logged_in():
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        pass1 = request.form.get('password1')
        pass2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif pass1 != pass2:
            flash('Passwords don\'t match.', category='error')
        elif len(pass1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, name=name, password=generate_password_hash(pass1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user, email=email, name=name)


def generate_invitation_code():
    return encrypt_id(current_user.teamId)


def encrypt_id(num):
    return str(hex((51 + num) * 651)[2:])[::-1].upper()


def decrypt_id(enc):
    return int(int(enc[::-1], 16) / 651 - 51)


def join_team(team_id):
    current_user.teamId = team_id
    db.session.commit()


def is_logged_in():
    try:
        x = current_user.id
    except:
        return False

    return True


