from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from conversation_handler import conversation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ASDJOAIHJFLKAGNALKGBNAJKLBG'
socketio = SocketIO(app, cors_allowed_origins="*")
user_ids = {}


@app.route("/")
def home():
    return render_template("index.html")


@socketio.on('connect')
def handle_connect():
    global user_ids
    print('USER CONNECTED!')
    print(request.sid)
    print('connected to ', request.sid)
    user_ids.setdefault(request.sid, conversation(''))
    emit('response', {'message': "Hello, I am Heal-Bot!"})


@socketio.on('sendMessage')
def handle_message(message):
    global user_ids
    print('in sendMessage')
    print('Message:', message)
    print(request.sid + ' says: ' + message['message'])
    user_ids[request.sid].update_utterance(message['message'])
    emit('response', {'message': user_ids[request.sid].parse_convo()})


@socketio.on('disconnect')
def handle_disconnect():
    global user_ids
    if request.sid in user_ids:
        print('user deleted')
        del user_ids[request.sid]
    print('user left')


@socketio.on_error()
def error_handler(e):
    print('Error!')
    print(e)
    

if __name__ == '__main__':
    socketio.run(app)
