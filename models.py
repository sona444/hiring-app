from app import app
from flask_mongoengine import MongoEngine

app.config['MONGODB_SETTINGS'] = {
    'db': 'clustor0',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine()
db.init_app(app)

class candidates(db.Document):
    name = db.StringField()
    email = db.StringField()
    def to_json(self):
        return {"name": self.name,
                "email": self.email}