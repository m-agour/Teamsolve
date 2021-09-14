from website import db
import app
db.create_all(app=app.app)