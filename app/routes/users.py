from flask import Blueprint, render_template, redirect, url_for, flash
from flasgger import swag_from
from app.models import User, db
from app.forms import UserForm

bp = Blueprint('users', __name__)


@bp.route('/users', methods=['GET', 'POST'])
@swag_from({
    'tags': ['Users'],
    'description': 'Manage users. Create a new user or view all users.',
    'parameters': [
        {
            'in': 'body',
            'name': 'body',
            'required': False,
            'schema': {
                'type': 'object',
                'properties': {
                    'balance': {'type': 'number', 'description': 'Initial balance of the user'},
                    'commission_rate': {'type': 'number', 'description': 'Commission rate for the user'},
                    'webhook_url': {'type': 'string', 'description': 'Webhook URL for notifications'}
                },
                'required': ['balance', 'commission_rate']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'List of users',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'balance': {'type': 'number'},
                        'commission_rate': {'type': 'number'},
                        'webhook_url': {'type': 'string'}
                    }
                }
            }
        },
        201: {'description': 'User created successfully'},
        400: {'description': 'Invalid input'}
    }
})
def users():
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            balance=form.balance.data,
            commission_rate=form.commission_rate.data,
            webhook_url=form.webhook_url.data
        )
        db.session.add(user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('users.users'))
    users_list = User.query.all()
    return render_template('users.html', form=form, users=users_list)

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@swag_from({
    'tags': ['Users'],
    'description': 'Delete a user by ID.',
    'parameters': [
        {
            'in': 'path',
            'name': 'user_id',
            'type': 'integer',
            'required': True,
            'description': 'ID of the user to delete'
        }
    ],
    'responses': {
        200: {'description': 'User deleted successfully'},
        404: {'description': 'User not found'}
    }
})
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('users.users'))
