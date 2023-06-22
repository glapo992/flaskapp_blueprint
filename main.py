from app import create_app, db, cli

app = create_app()

cli.register(app)

from app.models import Users, Posts, followers
@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'Users':Users, 'Posts':Posts, 'followers':followers}