from website import create_app
from website.models import User, Problem, Team
from website import db


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=80)

