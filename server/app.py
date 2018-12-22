from flask import Flask, render_template
from flask_socketio import SocketIO
import time
import threading
import psutil
from datetime import datetime

app = Flask(__name__, static_folder='../static',
            template_folder='../static')

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

cpu_util = psutil.cpu_percent()


class publishThread(threading.Thread):
    def __init__(self):
        self.frequency = 1
        super(publishThread, self).__init__()

    def publishUtilization(self):
        while True:
            cpu_util = psutil.cpu_percent()
            now = datetime.now()
            print("Utilization at {} is {}".format(now.ctime(), str(cpu_util)))
            socketio.emit('cpuUtil', {'util': cpu_util})
            time.sleep(self.frequency)

    def run(self):
        self.publishUtilization()


@app.route('/')
def index():
    return render_template('dashboard.html', name='Suhaas')


@socketio.on('connect')
def on_connect():
    print('Connected to client!')
    thread = publishThread()
    thread.start()


@socketio.on('disconnect')
def on_connect():
    print('Disconnected from client!')


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5000, debug=True)
    socketio.run(app)
