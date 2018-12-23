from flask import Flask, render_template
from flask_socketio import SocketIO
import time
import threading
import psutil
from datetime import datetime
from collections import deque
import os

app = Flask(__name__, static_folder='../static',
            template_folder='../static')

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

PUB_FREQ = 2
MAX_LEN = PUB_FREQ * 60 * 10
cpu_util = psutil.cpu_percent()
util_list = deque()
curr_sum = 0


def calcAverage(new_point):
    # Manually implement maxlen functionality to make average calc O(1)
    if len(util_list) < MAX_LEN:
        curr_sum += new_point
        util_list.append(new_point)
        return curr_sum / len(util_list)
    else:
        curr_sum -= util_list.popleft()
        curr_sum += new_point
        util_list.append(new_point)
        return curr_sum / MAX_LEN


class publishThread(threading.Thread):
    def __init__(self):
        self.frequency = PUB_FREQ
        self.cpu_alarm = False
        self.load_alarm = False
        super(publishThread, self).__init__()

    def publishUtilization(self):
        cpu_util = psutil.cpu_percent()
        now = datetime.now().isoformat()
        print("Utilization at {} is {}".format(now, str(cpu_util)))
        util_list.append(cpu_util)
        socketio.emit('cpuUtil', {'util': cpu_util, 'timestamp': now})

    def publishLoad(self):
        load = os.getloadavg()
        now = datetime.now().isoformat()
        print("Utilization at {} is {}".format(now, str(load[0])))
        socketio.emit('loadAvg', {
                      'load_one': load[0], 
                      'load_five': load[1], 
                      'load_fifteen': load[2], 
                      'timestamp': now
                      })

    def run(self):
        while True:
            self.publishUtilization()
            self.publishLoad()
            time.sleep(self.frequency)


@app.route('/')
def index():
    return render_template('dashboard.html')


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
