from dbdash import create_app
app=create_app()
from dbdash import db
with app.app_context():
    db.drop_all()
    db.create_all()