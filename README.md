# Load Monitoring Web Application

A simple web application to track average system load and CPU Utilization on your machine.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
It is __highly__ reccomended to use a virtual environment and/or package manager such as virtualenv or conda to avoid polluting the global Python namespace. Additionally, this application requires Python 3, so you may have to modify the commands below to `pip3` or `python3` depending on your aliases and local Python setup.

On the server side, all of the required modules are included in *requirements.txt*, so you can simply run: 

```bash
pip install -r requirements.txt
```

The client-side dependencies are all explicitly declared in the template (for now) so there is no need to download anything.


### Installing

To get up and running, first clone the repository to a location on your local computer: 

```bash
git clone git:://github.com/ysuhaas/load-monitoring-web
```

Then, from the server directory, run `app.py` with a Python 3 interpreter:

```bash
cd server/
python3 app.py
```
This should start the server, and in the terminal window you should see that a webserver has been started locally.

### Running

Now, in a web browser, simply navigate to [127.0.0.1/5000](127.0.0.1/5000). You should be able to see data streaming. Note that you can enable/disable data series on the graph by clicking on the label on the legend above the graph.


## Implementation


### Server-side

To query the system load and average CPU utilization of the system, we use the python modules `os` (included) and `psutil` (installed using pip). A basic webapp is created using Flask, and served on a local webserver. Socket.IO was used then to push messages to the client, using the Flask-SocketIO library.



### Client-side





### List of Frameworks/Libraries Used
Client-side:   

* [Chart.js](https://www.chartjs.org/) - JS Library for graphing...


