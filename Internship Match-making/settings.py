from app import app, db
from app.models import User, Appointment, Dog, Service,Host

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User,  Host=Host)
