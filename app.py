from app import create_app
from app.cli import create_admin

app = create_app()
app.cli.add_command(create_admin)

if __name__ == '__main__':
    app.run(debug=True)
