from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, send_file, send_from_directory
from api_helper_functions import request_data_parser
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, logout_user, login_user, login_required, UserMixin, current_user
from sqlalchemy import Integer, String, Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column
app = Flask(__name__)
db = SQLAlchemy()
cors = CORS(app, supports_credentials=True)
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    print(f"looking up {user_id}")
    return User.query.get(int(user_id))


login_manager.init_app(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///messages.db"
db.init_app(app)
app.secret_key = "a secret "

user_conversation_association = Table(
    'user_conversation_association',
    db.Model.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), nullable=False),
    Column('conversation_id', Integer, ForeignKey(
        'conversation.id'), nullable=False)
)


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    conversations = db.relationship(
        'Conversation',
        secondary=user_conversation_association,
        backref='participants'
    )


class Conversation(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    # Relationship with User - Many-to-One (many conversations can belong to one user)
    messages = db.relationship(
        'Message', backref='conversation', cascade='all, delete-orphan')


class Message(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    conversation_id: Mapped[int] = mapped_column(
        db.ForeignKey('conversation.id'))
    to_user_id: Mapped[str] = mapped_column(db.ForeignKey('user.id'))
    from_user_id: Mapped[str] = mapped_column(db.ForeignKey('user.id'))


with app.app_context():
    db.create_all()


@app.route("/")
def get_root():
    return send_file("web/dist/index.html")


@app.route("/signin", methods=["POST"])
@request_data_parser
def sign_in(username: str, password: str):
    user = User.query.filter_by(username=username).first()
    if not user:
        return {"success": False}, 401
    if check_password_hash(user.hashed_password, password):
        login_user(user)
        return {"success": True}
    return {"success": False}, 401


@app.route("/signup", methods=["POST"])
@ request_data_parser
def sign_up(username: str, password: str):
    hashed_password = generate_password_hash(password)
    user = User(username=username,
                hashed_password=hashed_password)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return {"success": True}


@login_required
@app.route('/conversations')
def conversations():
    if current_user.is_anonymous:
        return {"success": False, "reason": "You must be logged in"}, 401
    conversations = current_user.conversations
    serialized_conversations = []
    for conversation in conversations:
        participants = conversation.participants.copy()
        participants.remove(current_user)
        other_user = participants[0]
        serialized_conversations.append({
            "user": other_user.username,
            "id": conversation.id,
            "messages": [{
                "text": message.text,
                "to": User.query.filter_by(id=message.to_user_id).first().username,
                "from": User.query.filter_by(id=message.from_user_id).first().username,
            } for message in conversation.messages]
        })
    return serialized_conversations


@login_required
@app.route('/conversation', methods=["POST"])
@request_data_parser
def conversation(id: int):
    conversation = Conversation.query.filter_by(id=id).first()
    return [message.text for message in conversation.messages]


@login_required
@app.route('/send-message', methods=["POST"])
@ request_data_parser
def add_message(message: str, conversationId: int):
    conversation = Conversation.query.filter_by(id=conversationId).first()
    participants = conversation.participants.copy()
    participants.remove(current_user)
    other_user = participants[0]
    message = Message(text=message, conversation_id=conversationId,
                      from_user_id=current_user.id, to_user_id=other_user.id)
    db.session.add(message)
    db.session.commit()
    return {"success": True}


@ login_required
@ app.route('/add-conversation', methods=["POST"])
@ request_data_parser
def add_conversation(user: str):
    user = User.query.filter_by(username=user).first()
    if user is None:
        return {"success": False, "reason": "User not found"}, 404

    if Conversation.query.filter(Conversation.participants.contains(current_user)).filter(Conversation.participants.contains(user)).first():
        return {"success": False, "reason": "Conversation already exists"}, 400
    conversation = Conversation(participants=[current_user, user])
    db.session.add(conversation)
    db.session.commit()
    return {"success": True, "id": conversation.id}


@ app.route('/assets/<path:path>')
def send_assets(path):
    return send_from_directory("web/dist/assets/", path)
