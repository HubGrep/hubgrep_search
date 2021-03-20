from flask_security.models import fsqla_v2 as fsqla
import enum
from hubgrep import db


# Define models
fsqla.FsModels.set_db_info(db)

class Role(db.Model, fsqla.FsRoleMixin):
    pass

class User(db.Model, fsqla.FsUserMixin):
    pass



# todo
class HosterType(enum.Enum):
    github = 0
    gitlab = 1
    gitea = 2
    

class HostingService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
    user = db.relationship('User',
        backref=db.backref('hosting_service', lazy=True))

    type = db.Column(db.String(80), unique=True, nullable=False)

    # should this be unique, or can we use it to store multiple 
    # api keys for a backend?
    base_url = db.Column(db.String(500), unique=True, nullable=False)

    # could be json, but thats only supported for postgres
    config = db.Column(db.Text)
