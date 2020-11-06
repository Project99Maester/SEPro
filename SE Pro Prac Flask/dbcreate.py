from flask import app
from auth_flask import db, create_app,models


apps=create_app()
db.drop_all(app=apps)

db.create_all(app=apps) # pass the create_app result so Flask-SQLAlchemy gets the configuration.


