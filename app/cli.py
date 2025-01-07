import click
from flask.cli import with_appcontext
from app.models import User, db

@click.command('create-admin')
@click.argument('balance', type=float)
@click.argument('commission_rate', type=float)
@click.argument('webhook_url', type=str)
@swag_from({
    'tags': ['Admin'],
    'description': 'Create an admin user with predefined parameters.',
    'parameters': [
        {
            'in': 'body',
            'name': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'balance': {'type': 'number', 'description': 'Admin balance'},
                    'commission_rate': {'type': 'number', 'description': 'Admin commission rate'},
                    'webhook_url': {'type': 'string', 'description': 'Admin webhook URL'}
                },
                'required': ['balance', 'commission_rate', 'webhook_url']
            }
        }
    ],
    'responses': {
        201: {'description': 'Admin created successfully'},
        400: {'description': 'Admin with this webhook URL already exists'}
    }
})
@with_appcontext
def create_admin(balance, commission_rate, webhook_url):
    if User.query.filter_by(webhook_url=webhook_url).first():
        click.echo("Admin with this webhook URL already exists.")
        return
    admin = User(balance=balance, commission_rate=commission_rate, webhook_url=webhook_url)
    db.session.add(admin)
    db.session.commit()
    click.echo(f"Admin created with ID: {admin.id}")
