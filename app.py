from datetime import datetime
import os

from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, logout_user, login_user, login_required, UserMixin, current_user
from sqlalchemy import Integer, String, Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column
from dotenv import load_dotenv

from request_parser import body_to_args

load_dotenv()
# Initialize application and extensions
app = Flask(__name__)
# Create ORM
db = SQLAlchemy()

# Allow cross site requests
# NOTE: This should probably have an origin
# whitelist in the future
cors = CORS(app, supports_credentials=True)

# Create login manager
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    """
    Given the user id, get the user object
    """
    return User.query.get(int(user_id))


# Initialize login manager
login_manager.init_app(app)

# Use a sqlite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///messages.db"

# Initialize database
db.init_app(app)

# Read or create secret key
app.secret_key = os.environ.get("SECRET_KEY")
if app.secret_key is None:
    app.secret_key = os.urandom(24)
    with open(".env", "w") as f:
        f.write(f"SECRET_KEY={app.secret_key}")

# Association table for users and conversations
user_conversation_association = Table(
    'user_conversation_association',
    db.Model.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), nullable=False),
    Column('conversation_id', Integer, ForeignKey(
        'conversation.id'), nullable=False)
)


class User(UserMixin, db.Model):
    """
    A user in the system
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    conversations = db.relationship(
        'Conversation',
        secondary=user_conversation_association,
        backref='participants'
    )


class Conversation(db.Model):
    """
    A group of messages associated with some users
    """
    id: Mapped[int] = mapped_column(primary_key=True)

    # Relationship with User - Many-to-One (many conversations can belong to one user)
    messages = db.relationship(
        'Message', backref='conversation', cascade='all, delete-orphan')


class Message(db.Model):
    """
    A single message
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()

    # Currently unused
    timestamp: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    conversation_id: Mapped[int] = mapped_column(
        db.ForeignKey('conversation.id'))

    to_user_id: Mapped[str] = mapped_column(db.ForeignKey('user.id'))

    from_user_id: Mapped[str] = mapped_column(db.ForeignKey('user.id'))


# Create all database tables
with app.app_context():
    db.create_all()


@app.route("/")
def get_root():
    """
    Serve built vue app
    """
    return send_file("web/dist/index.html")


@app.route("/signin", methods=["POST"])
@body_to_args
def sign_in(username: str, password: str):
    """
    Handle authentication
    """
    user = User.query.filter_by(username=username).first()
    if not user:
        return {"success": False}, 401
    if check_password_hash(user.hashed_password, password):
        login_user(user)
        return {"success": True}
    return {"success": False}, 401


@app.route("/logout")
def logout():
    """
    A route to end an authenticated session
    """
    logout_user()
    return {"success": True}


@app.route("/signup", methods=["POST"])
@ body_to_args
def sign_up(username: str, password: str):
    """
    Create a new user
    """
    #  Make sure username isn't already taken
    if User.query.filter_by(username=username).first() is not None:
        return {"success": False, "message": "User already exists"}, 400

    # Hash password
    hashed_password = generate_password_hash(password)

    # Create the user
    user = User(username=username,
                hashed_password=hashed_password)

    # Add to database
    db.session.add(user)
    db.session.commit()

    # Start an authenticated session
    login_user(user)
    return {"success": True}


@login_required
@app.route('/conversations')
def conversations():
    """
    Get the current user's conversations.

    NOTE: This sends the user's entire message history. It's not super efficient.
    """
    # Can't get an anonymous user's conversations
    if current_user.is_anonymous:
        return {"success": False, "reason": "You must be logged in"}, 401

    # Get current user's conversations
    conversations = current_user.conversations

    # Json serializable representation of conversations
    serialized_conversations = []

    for conversation in conversations:
        # Figure out who the other participant in the conversation is
        participants = conversation.participants.copy()
        participants.remove(current_user)
        other_user = participants[0]

        # Add a json object representing the conversation
        serialized_conversations.append({
            "user": other_user.username,
            "id": conversation.id,
            "messages": [{
                "text": message.text,
                "to": User.query.filter_by(id=message.to_user_id).first().username,
                "from": User.query.filter_by(id=message.from_user_id).first().username,
            } for message in conversation.messages]
        })
    # Return the list of conversations
    return serialized_conversations


@login_required
@app.route('/send-message', methods=["POST"])
@ body_to_args
def add_message(message: str, conversationId: int):
    """
    Send a message
    """
    # Get the conversation
    conversation = Conversation.query.filter_by(id=conversationId).first()
    # Get the participants
    participants = conversation.participants.copy()

    # Find the participant that isn't us
    participants.remove(current_user)
    other_user = participants[0]

    # Create the message object
    message = Message(text=message, conversation_id=conversationId,
                      from_user_id=current_user.id, to_user_id=other_user.id)

    # Add the message to the database
    db.session.add(message)
    db.session.commit()
    return {"success": True}


@ login_required
@ app.route('/add-conversation', methods=["POST"])
@ body_to_args
def add_conversation(user: str):
    """
    Create a new conversation with another user
    """
    # Get the other user
    user = User.query.filter_by(username=user).first()

    # Handle user not existing
    if user is None:
        return {"success": False, "reason": "User not found"}, 404

    # A conversation already exists if it has
    # the current user and the other user as participants
    conversation_exists = Conversation.query  \
        .filter(Conversation.participants.contains(current_user)) \
        .filter(Conversation.participants.contains(user)).first()

    # Don't allow duplicate conversations
    if conversation_exists:
        return {"success": False, "reason": "Conversation already exists"}, 400

    # Create the conversation
    conversation = Conversation(participants=[current_user, user])

    # Add conversation to the database
    db.session.add(conversation)
    db.session.commit()
    return {"success": True, "id": conversation.id}


@ app.route('/assets/<path:path>')
def send_assets(path):
    """
    Serve built js and css
    """
    return send_from_directory("web/dist/assets/", path)
