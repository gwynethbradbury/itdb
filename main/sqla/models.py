
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, Time, text

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from wtforms import form, fields, validators

Base = declarative_base()
metadata = Base.metadata

# region iaas classes
class News(Base):
    __tablename__ = 'News'

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    body = Column(Text)
    created_on = Column(Date)
    updated_on = Column(Date)


class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    news_id = Column(ForeignKey(u'News.id'), index=True)
    username = Column(String(20))
    comment = Column(Text)
    visible = Column(Integer)
    created_on = Column(Date)

    news = relationship(u'News')


class IaasEvents(Base):
    __tablename__ = 'iaas_events'

    id = Column(Integer, primary_key=True)
    title = Column(String(60))
    subtitle = Column(String(60))
    description = Column(String(255))
    room = Column(String(60))
    eventdate = Column(Date)
    starttime = Column(Time)
    endtime = Column(Time)


class PermittedSvc(Base):
    __tablename__ = 'permitted_svc'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer)
    svc_id = Column(Integer)


class Roles(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True)
    description = Column(String(250))


class Services(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class Subscribers(Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(60))


class SvcInstances(Base):
    __tablename__ = 'svc_instances'

    id = Column(Integer, primary_key=True)
    project_display_name = Column(String(30))
    instance_identifier = Column(String(70))
    svc_type_id = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=False)

# class DatabaseService(Base):
#     __tablename__ = 'database_service'
#
#     id = Column(Integer, primary_key=True)
#     svc_instance_id = 0


# endregion



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