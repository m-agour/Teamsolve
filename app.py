from website import create_app
from website.models import User, Problem, Team
from website import db
import os

port = int(os.environ.get('PORT', 5000))

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=port)

