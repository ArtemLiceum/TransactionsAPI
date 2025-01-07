from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import Transaction, TransactionStatus, User
from app.forms import TransactionStatusForm
from app import db
from flasgger import swag_from



bp = Blueprint('transactions', __name__)

@bp.route('/transactions')
@swag_from({
    'tags': ['Transactions'],
    'description': 'Get a list of all transactions.',
    'responses': {
        200: {
            'description': 'List of transactions',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'amount': {'type': 'number'},
                        'commission': {'type': 'number'},
                        'status': {'type': 'string'},
                        'user_id': {'type': 'integer'},
                        'created_at': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        }
    }
})
def transactions():
    transactions = Transaction.query.all()
    return render_template('transactions.html', transactions=transactions)

@bp.route('/transactions/<int:transaction_id>', methods=['GET', 'POST'])
@swag_from({
    'tags': ['Transactions'],
    'description': 'View or update the status of a transaction by ID.',
    'parameters': [
        {
            'in': 'path',
            'name': 'transaction_id',
            'type': 'integer',
            'required': True,
            'description': 'ID of the transaction to view or update'
        },
        {
            'in': 'body',
            'name': 'body',
            'required': False,
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'enum': ['confirmed', 'canceled'], 'description': 'New status'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Transaction details or status updated',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'amount': {'type': 'number'},
                    'commission': {'type': 'number'},
                    'status': {'type': 'string'},
                    'user_id': {'type': 'integer'},
                    'created_at': {'type': 'string', 'format': 'date-time'}
                }
            }
        },
        400: {'description': 'Invalid status or other input error'},
        404: {'description': 'Transaction not found'}
    }
})
def transaction_detail(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    form = TransactionStatusForm()

    if form.validate_on_submit():
        if transaction.status == TransactionStatus.PENDING:
            new_status = TransactionStatus(form.status.data)
            transaction.status = new_status
            db.session.commit()

            # Если транзакция переходит в статус confirmed
            if new_status == TransactionStatus.CONFIRMED:
                user = transaction.user
                if user.balance < transaction.amount:
                    flash('Insufficient balance in user wallet!', 'danger')
                else:
                    user.balance -= transaction.amount
                    db.session.commit()
                    flash('Transaction confirmed and balance updated successfully!', 'success')
            else:
                flash('Transaction status updated successfully!', 'success')
        else:
            flash('Transaction status cannot be changed!', 'danger')
        return redirect(url_for('transactions.transaction_detail', transaction_id=transaction_id))

    return render_template('transaction_detail.html', transaction=transaction, form=form)


@bp.route('/create_transaction', methods=['POST'])
@swag_from({
    'tags': ['Transactions'],
    'description': 'Create a new transaction for a user with calculated commission.',
    'parameters': [
        {
            'in': 'body',
            'name': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'integer', 'description': 'ID of the user'},
                    'amount': {'type': 'number', 'description': 'Transaction amount'}
                },
                'required': ['user_id', 'amount']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Transaction created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'transaction_id': {'type': 'integer'}
                }
            }
        },
        400: {'description': 'Invalid input'},
        404: {'description': 'User not found'},
        422: {'description': 'Insufficient funds'}
    }
})
def create_transaction():
    data = request.get_json()

    try:
        user_id = int(data.get('user_id', 0))
        amount = float(data.get('amount', 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input: user_id and amount must be numeric"}), 400

    if user_id <= 0 or amount <= 0:
        return jsonify({"error": "user_id and amount must be positive numbers"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Проверка, хватает ли средств на балансе с учетом комиссии
    if user.balance < amount + amount * user.commission_rate:
        # Если средств недостаточно, создаем отмененную транзакцию
        transaction = Transaction(amount=amount, commission=0, status=TransactionStatus.CANCELED, user=user)
        db.session.add(transaction)
        db.session.commit()

        return jsonify(
            {"error": "Insufficient funds. Transaction canceled.", "transaction_id": transaction.id}), 422

    # Если средств достаточно, создаем транзакцию
    commission = amount * user.commission_rate
    transaction = Transaction(amount=amount, commission=commission, user=user)

    # Вычитаем сумму транзакции с баланса пользователя
    user.balance -= (amount + commission)
    db.session.add(transaction)
    db.session.commit()

    return jsonify({"message": "Transaction created successfully", "transaction_id": transaction.id}), 201

@bp.route('/cancel_transaction', methods=['POST'])
@swag_from({
    'tags': ['Transactions'],
    'description': 'Cancel a pending transaction.',
    'parameters': [
        {
            'in': 'body',
            'name': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'transaction_id': {'type': 'integer', 'description': 'ID of the transaction to cancel'}
                },
                'required': ['transaction_id']
            }
        }
    ],
    'responses': {
        200: {'description': 'Transaction canceled successfully'},
        400: {'description': 'Invalid input or transaction cannot be canceled'},
        404: {'description': 'Transaction not found'}
    }
})
def cancel_transaction():
    data = request.get_json()

    try:
        transaction_id = int(data.get('transaction_id', 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input: transaction_id must be numeric"}), 400

    if transaction_id <= 0:
        return jsonify({"error": "transaction_id must be a positive number"}), 400

    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    if transaction.status != TransactionStatus.PENDING:
        return jsonify({"error": "Only pending transactions can be canceled"}), 400

    transaction.status = TransactionStatus.CANCELED
    db.session.commit()

    return jsonify({"message": "Transaction canceled successfully"}), 200

@bp.route('/check_transaction', methods=['GET'])
@swag_from({
    'tags': ['Transactions'],
    'description': 'Check the details of a transaction.',
    'parameters': [
        {
            'in': 'query',
            'name': 'transaction_id',
            'type': 'integer',
            'required': True,
            'description': 'ID of the transaction to check'
        }
    ],
    'responses': {
        200: {
            'description': 'Transaction details',
            'schema': {
                'type': 'object',
                'properties': {
                    'transaction_id': {'type': 'integer'},
                    'amount': {'type': 'number'},
                    'commission': {'type': 'number'},
                    'status': {'type': 'string'},
                    'user_id': {'type': 'integer'},
                    'created_at': {'type': 'string', 'format': 'date-time'}
                }
            }
        },
        400: {'description': 'Invalid input'},
        404: {'description': 'Transaction not found'}
    }
})
def check_transaction():
    try:
        transaction_id = int(request.args.get('transaction_id', 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input: transaction_id must be numeric"}), 400

    if transaction_id <= 0:
        return jsonify({"error": "transaction_id must be a positive number"}), 400

    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    return jsonify({
        "transaction_id": transaction.id,
        "amount": transaction.amount,
        "commission": transaction.commission,
        "status": transaction.status.value,
        "user_id": transaction.user_id,
        "created_at": transaction.created_at.isoformat()
    }), 200