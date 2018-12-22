from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__, static_folder='../static',
            template_folder='../static')

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html', name='Suhaas')


@socketio.on('connect')
def on_connect():
    print('Connected to client!')


@socketio.on('disconnect')
def on_connect():
    print('Disconnected from client!')


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5000, debug=True)
    socketio.run(app)
