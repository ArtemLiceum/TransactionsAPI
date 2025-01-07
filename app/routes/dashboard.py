from flask import Blueprint, render_template, session, jsonify, request
from app.models import User, Transaction
from app import db
from flasgger import swag_from

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@swag_from({
    'tags': ['Dashboard'],
    'description': 'Get statistics about the platform, including users, transactions, and recent transactions.',
    'responses': {
        200: {
            'description': 'Dashboard statistics and recent transactions',
            'schema': {
                'type': 'object',
                'properties': {
                    'total_users': {'type': 'integer'},
                    'total_transactions': {'type': 'integer'},
                    'total_transaction_amount': {'type': 'number'},
                    'recent_transactions': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'amount': {'type': 'number'},
                                'status': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        }
    }
})
def dashboard():
    total_users = User.query.count()
    total_transactions = Transaction.query.count()
    total_transaction_amount = db.session.query(db.func.sum(Transaction.amount)).scalar() or 0
    recent_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(5).all()
    refresh_interval = session.get('refresh_interval', 10)
    return render_template('dashboard.html',
                           total_users=total_users,
                           total_transactions=total_transactions,
                           total_transaction_amount=total_transaction_amount,
                           recent_transactions=recent_transactions,
                           refresh_interval=refresh_interval)

@bp.route('/set_refresh_interval', methods=['POST'])
@swag_from({
    'tags': ['Dashboard'],
    'description': 'Set the auto-refresh interval for the dashboard.',
    'parameters': [
        {
            'in': 'body',
            'name': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'refresh_interval': {
                        'type': 'integer',
                        'enum': [0, 10, 15, 30, 60],
                        'description': 'Auto-refresh interval in seconds.',
                        'example': 10
                    }
                }
            },
            'required': True,
            'description': 'Interval value to set.'
        }
    ],
    'responses': {
        200: {
            'description': 'Refresh interval successfully updated',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Refresh interval updated'},
                    'refresh_interval': {'type': 'integer', 'example': 10}
                }
            }
        },
        400: {
            'description': 'Invalid interval value',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Invalid interval'}
                }
            }
        }
    }
})
def set_refresh_interval():
    refresh_interval = request.json.get('refresh_interval')

    valid_intervals = [0, 10, 15, 30, 60]  # в секундах
    if refresh_interval not in valid_intervals:
        return jsonify({'error': 'Invalid interval'}), 400

    session['refresh_interval'] = refresh_interval
    return jsonify({'message': 'Refresh interval updated', 'refresh_interval': refresh_interval})