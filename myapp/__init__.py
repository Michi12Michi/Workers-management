from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)
Migrate(app, db)

# qui vanno importate tutte le blueprint
from myapp.core.views import core
from myapp.workers.views import users
from myapp.dates.views import dates

app.register_blueprint(core)
app.register_blueprint(users)
app.register_blueprint(dates)
