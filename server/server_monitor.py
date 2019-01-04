import eventlet
import os
import psutil
import threading
from collections import deque
from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO
from multiprocessing import Pool, cpu_count


# Start a Flask server and SocketIO instance
app = Flask(__name__, static_folder='../static',
            template_folder='../static')

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
cpu_util = psutil.cpu_percent()  # initialize
first_client_connect = True
pub_thread = None

"""Constants"""
# Alarms
cpu_alarm = False
load_alarm = False

# Thresholds
CPU_THRESHOLD = 75
LOAD_THRESHOLD = psutil.cpu_count(logical=False)

# Data resolution and retention
PUB_FREQ = 10  # resolution of data in (1 point / n seconds)
LOAD_TEST_DURATION = 120.0  # seconds
AVG_WINDOW = 2  # minutes
MAX_LEN = PUB_FREQ * 60 * AVG_WINDOW  # number of points to store/avg

utils_list = deque(maxlen=MAX_LEN)  # CPU utilization points
loads_list = deque(maxlen=MAX_LEN)  # Avg. load points
# TODO add recent alarm store and load

@app.route('/')
def dashboard_route():
    """
    Return a route to the root template (an HTML template for the dashboard).
    """
    return render_template('dashboard.html')


@socketio.on('connect')
def on_connect():
    """
    Defines a callback function which is called when the socketIO instance
    recives a 'connect' message (on each new client connected). Spawns a 
    publish thread when the first client connects.
    """
    global first_client_connect
    global pub_thread

    if first_client_connect:
        pub_thread = eventlet.spawn(publishThreadTarget, PUB_FREQ)
        first_client_connect = False
    print('Connected to client!')


@socketio.on('disconnect')
def on_disconnect():
    """
    Defines a callback function which is called when the socketIO instance
    recives a 'disconnect' message (on each new client disconnected). 
    """

    print('Disconnected from a client!')


@socketio.on('loadTest')
def start_load_test(message):
    """
    Defines a callback function which is called when the client requests
    a load test. Start a pool of (traditional, non-eventlet) threads that
    will cause increased system load, and terminate after some time.
    """
    processes = cpu_count()
    pool = Pool(processes)
    print("Starting the load test.")
    pool.map_async(loadTestTarget, range(processes))
    t = threading.Timer(LOAD_TEST_DURATION, end_load_test, args=[pool])
    t.start()


def resetState():
    """
    Resets the alarm and data state to the default.
    """
    global cpu_alarm
    global load_alarm
    cpu_alarm = False
    load_alarm = False
    loads_list.clear()
    utils_list.clear()


def end_load_test(pool):
    """
    End the ongoing load test by killing all the spawned threads

    Parameters:  
    pool (multiprocessing.Pool): Thread pool of spawned load test threads
    """
    pool.terminate()
    print("Finished the load test.")


def loadTestTarget(x):
    """
    Defines a thread to repeat an arbitrary operation to increase load and
    CPU utilization.
    """
    while True:
        x * x


def publishThreadTarget(wait_time):
    """
    Defines a thread to accumulate and publish load data, and sleep for a given
    amount of time (in seconds), on an infinite loop.

    Parameters:  
    wait_time (int): Amount of time (seconds) to sleep
    """
    while True:
        publishUtilization()
        publishLoad()
        eventlet.sleep(wait_time)


def publishUtilization():
    """
    Get the current CPU utilization, calculate the new running average,
    check alarm status, and emit on the socketIO instance the utilization
    at the current time, the new running average, and an alarm event (if
    there was a change in alarm state).
    """
    global cpu_alarm
    cpu_util = psutil.cpu_percent()
    now = datetime.now().isoformat()
    # print("Utilization at {} is {}".format(now, str(cpu_util)))
    avg = calcAverage(cpu_util, 'CPU')
    # print("Running average CPU Util is {}".format(avg))
    if avg >= CPU_THRESHOLD and not cpu_alarm:
        print("CPU Alarm START")
        cpu_alarm = True
        socketio.emit('alarm',
                      {'type': 'CPU', 'value': avg, 'start': True, 'timestamp': now})
    if avg < CPU_THRESHOLD and cpu_alarm:
        print("CPU Alarm RECOVER")
        cpu_alarm = False
        socketio.emit('alarm',
                      {'type': 'CPU', 'value': avg, 'start': False, 'timestamp': now})
    socketio.emit('cpuUtil', {'util': cpu_util, 'timestamp': now})
    socketio.emit('stats', {'cpu_avg': avg, 'timestamp': now})


def publishLoad():
    """
    Get the current load average, calculate the new running average (using
    the 1-minute average), check alarm status, and emit on the socketIO
    instance the load average measured at the current time, the new running
    average, and an alarm event (if there was a change in alarm state).
    """
    global load_alarm
    load = os.getloadavg()
    now = datetime.now().isoformat()
    # print("1 min load at {} is {}".format(now, str(load[])))
    avg = calcAverage(load[0], 'Load')
    # print("Running average load is {}".format(avg))
    if load[0] >= LOAD_THRESHOLD and not load_alarm:
        print("Load Alarm START")
        load_alarm = True
        socketio.emit('alarm',
                      {'type': 'Load', 'value': load[0], 'start': True, 'timestamp': now})
    if load[0] < LOAD_THRESHOLD and load_alarm:
        print("Load Alarm RECOVER")
        load_alarm = False
        socketio.emit('alarm',
                      {'type': 'Load', 'value': load[0], 'start': False, 'timestamp': now})
    socketio.emit('loadAvg', {
        'load_one': load[0],
        'load_five': load[1],
        'load_fifteen': load[2],
        'timestamp': now
    })
    socketio.emit('stats', {'load_avg': avg, 'timestamp': now})


def calcAverage(new_point, point_type):
    """
    Given a new point and its type, add it to the dataset and return the new
    average for the measurement.

    Parameters:  
    new_point (float): New data point to add  
    point_type(str): Type of measurement ('CPU' or 'Load')
    """
    if point_type == 'CPU':
        utils_list.append(new_point)
        avg = sum(utils_list) / len(utils_list)
        return avg
    elif point_type == 'Load':
        loads_list.append(new_point)
        avg = sum(loads_list) / len(loads_list)
        return avg

print(cpu_count())
print(os.getloadavg())
print(psutil.cpu_count(logical=False))

# eventlet.spawn(publishThreadTarget, PUB_FREQ)
if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5000, debug=True)
    socketio.run(app)
    pass
