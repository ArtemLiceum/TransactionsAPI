from enum import Enum
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, URL


class TransactionStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    EXPIRED = "expired"

class UserForm(FlaskForm):
    balance = FloatField('Balance', validators=[DataRequired(message="Balance is required")])
    commission_rate = FloatField('Commission Rate', validators=[DataRequired(message="Commission rate is required")])
    webhook_url = StringField('Webhook URL', validators=[URL(message="Invalid URL")])
    submit = SubmitField('Submit')

class TransactionStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        (TransactionStatus.CONFIRMED.value, 'Confirmed'),
        (TransactionStatus.CANCELED.value, 'Canceled')
    ], validators=[DataRequired(message="Status is required")])
    submit = SubmitField('Update')