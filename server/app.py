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

PUB_FREQ = 10  # resolution of data in (1 point / n seconds)
AVG_WINDOW = 2  # minutes
MAX_LEN = PUB_FREQ * 60 * AVG_WINDOW
cpu_util = psutil.cpu_percent()  # throwaway
utils_list = deque(maxlen=MAX_LEN)
loads_list = deque(maxlen=MAX_LEN)
alarm_list = deque(maxlen=10)
CPU_THRESHOLD = 75
LOAD_THRESHOLD = 1


def calcAverage(new_point, point_type):
    if point_type == 'CPU':
        utils_list.append(new_point)
        avg = sum(utils_list) / len(utils_list)
        return avg
    elif point_type == 'Load':
        loads_list.append(new_point)
        avg = sum(loads_list) / len(loads_list)
        return avg


class publishThread(threading.Thread):
    def __init__(self):
        self.frequency = PUB_FREQ
        self.cpu_alarm = False
        self.load_alarm = False
        super(publishThread, self).__init__()

    def publishAlarm(self, mode, activate, now):
        socketio.emit('alarm', {'type': mode, 'start': activate, 'timestamp': now})

    def publishUtilization(self):
        cpu_util = psutil.cpu_percent()
        now = datetime.now().isoformat()
        # print("Utilization at {} is {}".format(now, str(cpu_util)))
        avg = calcAverage(cpu_util, 'CPU')
        # print("Running average CPU Util is {}".format(avg))
        if avg >= CPU_THRESHOLD and not self.cpu_alarm:
            # print("###CPU alarm triggered.###")
            self.cpu_alarm = True
            self.publishAlarm('CPU', True, now)
        if avg < CPU_THRESHOLD and self.cpu_alarm:
            # print("###CPU alarm reset.###")
            self.cpu_alarm = False
            self.publishAlarm('CPU', False, now)
        socketio.emit('cpuUtil', {'util': cpu_util, 'timestamp': now})
        socketio.emit('stats', {'cpu_avg': avg, 'timestamp': now})

    def publishLoad(self):
        load = os.getloadavg()
        now = datetime.now().isoformat()
        # print("5 min load at {} is {}".format(now, str(load[1])))
        avg = calcAverage(load[1], 'Load')
        # print("Running average load is {}".format(avg))
        if avg >= LOAD_THRESHOLD and not self.load_alarm:
            # print("###Load alarm triggered.###")
            self.load_alarm = True
            self.publishAlarm('Load', True, now)
        if avg < LOAD_THRESHOLD and self.load_alarm:
            # print("###Load alarm reset.###")
            self.load_alarm = False
            self.publishAlarm('Load', False, now)
        socketio.emit('loadAvg', {
                      'load_one': load[0],
                      'load_five': load[1],
                      'load_fifteen': load[2],
                      'timestamp': now
                      })
        socketio.emit('stats', {'load_avg': avg, 'timestamp': now})

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
