from datetime import datetime
from dbdash import db,login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    uId = db.Column(db.Integer, primary_key=True)
    uFirstname = db.Column(db.String(20), nullable=False)
    uLastname = db.Column(db.String(20), nullable=False)
    uEmail = db.Column(db.String(25), unique=True, nullable=False)
    uPassword = db.Column(db.String(60),nullable=False)
    uImage = db.Column(db.String(60), default='undraw_profile.svg')
    uCreated = db.Column(db.DateTime, default=datetime.utcnow)
    uStatus = db.Column(db.String(2),default='00')

    def get_id(self):
        return(self.uId)

    def __repr__(self):
        return f"User('{self.uFirstname}', '{self.uEmail}', '{self.uImage}')"