import datetime
from hubgrep import security
from flask_security import hash_password
from hubgrep import db

def create_admin(admin_email, admin_password):
    """ Create a database admin user with username (from email) and password. """
    admin = security.datastore.find_user(email=admin_email)
    if not admin:
        admin = security.datastore.create_user(
            email=admin_email, password=hash_password(admin_password)
        )
    admin.confirmed_at = datetime.datetime.now()
    admin_role = security.datastore.find_or_create_role("admin", permissions=["admin"])

    security.datastore.add_role_to_user(admin, admin_role)
    db.session.commit()
    return admin
