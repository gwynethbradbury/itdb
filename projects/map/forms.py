from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class DownloadTableForm(Form):
    tablename = StringField('tablename', validators=[DataRequired()])
    whole_table = BooleanField('whole_table', default=True)