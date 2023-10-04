from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = '123'
socketio = SocketIO(app)

# Store chat rooms and messages
chat_rooms = {}
messages = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    if room not in chat_rooms:
        chat_rooms[room] = set()
    chat_rooms[room].add(username)
    emit('user_joined', {'username': username}, room=room)
    emit('active_users', {'users': list(chat_rooms[room])}, room=room)
    if room in messages:
        emit('message_history', {'messages': messages[room]}, room=room)  # Send message history

@socketio.on('leave')
def handle_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    chat_rooms[room].remove(username)
    emit('user_left', {'username': username}, room=room)
    emit('active_users', {'users': list(chat_rooms[room])}, room=room)

@socketio.on('message')
def handle_message(data):
    username = data['username']
    room = data['room']
    message = data['message']
    if room not in messages:
        messages[room] = []
    messages[room].append({'username': username, 'message': message})
    emit('message', {'username': username, 'message': message}, room=room)

@socketio.on('createRoomForActiveUsers')
def create_room_for_active_users(data):
    room = 'ActiveUsersRoom'  # You can customize the room name
    if room not in chat_rooms:
        chat_rooms[room] = set()
    chat_rooms[room].add(data['username'])
    emit('user_joined', {'username': data['username']}, room=room)
    emit('active_users', {'users': list(chat_rooms[room])}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
