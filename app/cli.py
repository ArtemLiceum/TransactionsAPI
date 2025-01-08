import click
from flask.cli import with_appcontext
from app.models import User, db, UserRole


@click.command('create-admin')
@click.argument('webhook_url', type=str)
@with_appcontext
def create_admin(webhook_url):
    if User.query.filter_by(webhook_url=webhook_url).first():
        click.echo("Admin with this webhook URL already exists.")
        return
    admin = User(
        balance=100000.0,
        commission_rate=0.01,
        webhook_url=webhook_url,
        role=UserRole.ADMIN
    )

    db.session.add(admin)
    try:
        db.session.commit()
        click.echo(f"Admin created with ID: {admin.id}")
    except Exception as e:
        db.session.rollback()
        click.echo(f"Failed to create admin: {e}")
