import os

from app import create_app, db
from app.models import User

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User
    }

# Create database tables when the application starts
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
