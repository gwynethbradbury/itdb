
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, Time, text

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from wtforms import form, fields, validators

Base = declarative_base()
metadata = Base.metadata




# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        # if user is None:
        #     raise validators.ValidationError('Invalid user')
        #
        # # we're comparing the plaintext pw with the the hash from the db
        # if not check_password_hash(user.password, self.password.data):
        # # to compare plain text passwords use
        # # if user.password != self.password.data:
        #     raise validators.ValidationError('Invalid password')

    def get_user(self):
        return views.current_user.uid_trim()
        # return db.session.query(User).filter_by(login=self.login.data).first()