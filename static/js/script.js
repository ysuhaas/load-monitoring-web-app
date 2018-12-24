$(document).ready(function () {

    // Connect to SocketIO server (local)
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    console.log('Connected to server!');
    myChart = drawChart();

    // Register socketIO callback functions:

    socket.on('cpuUtil', function (msg) {
        // console.log("Received new utilization datapoint: " + msg.util);
        // Construct a moment time object for this timestamp (ISO 8601)
        m = moment(msg.timestamp)
        // Add to chart
        addUtilDataPoint(msg.util, m, myChart);
    });

    socket.on('loadAvg', function (msg) {
        // console.log("Received new load datapoint: " + msg.load_one);
        // Construct a moment time object for this timestamp (ISO 8601)
        m = moment(msg.timestamp)
        // Add to chart
        addLoadDataPoint(msg, m, myChart);
    });

    socket.on('alarm', function (msg) {
        console.log("New alarm: " + msg.type);
        // Construct a moment time object for this timestamp (ISO 8601)
        m = moment(msg.timestamp)
        // Add alert to log
        addAlert(msg, m);
    });

    socket.on('stats', function (msg) {
        // Construct a moment time object for this timestamp (ISO 8601)
        m = moment(msg.timestamp)
        // Update stats
        addStats(msg, m);
    });

    $(".btn").click(function(){
        console.log('Sending a test message...');
        socket.emit('loadTest', 'Testing...');
    }); 

});

function drawChart() {
    // Enable responsive resizing 
    Chart.defaults.global.responsive = true;

    var chartConfig = {
        type: 'line',
        data: {
            datasets: [{
                label: 'CPU Utilization',
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                borderColor: 'rgba(255, 99, 132, 1)',
                fill: false,
                lineTension: 0,
                yAxisID: 'y-axis-1',
                cubicInterpolationMode: 'default',
                data: []
            },
            {
                label: 'Load Average (1 min)',
                backgroundColor: 'rgba(99, 164, 255, 0.5)',
                borderColor: 'rgba(99, 164, 255, 1)',
                fill: false,
                lineTension: 0,
                yAxisID: 'y-axis-2',
                cubicInterpolationMode: 'default',
                data: []
            },
            {
                label: 'Load Average (5 min)',
                backgroundColor: 'rgba(133, 255, 99, 0.5)',
                borderColor: 'rgba(133, 255, 99, 1)',
                fill: false,
                lineTension: 0,
                yAxisID: 'y-axis-2',
                cubicInterpolationMode: 'default',
                data: [],
            },
            {
                label: 'Load Average (15 min)',
                backgroundColor: 'rgba(255, 161, 99, 0.5)',
                borderColor: 'rgba(255, 161, 99, 1)',
                fill: false,
                lineTension: 0,
                yAxisID: 'y-axis-2',
                cubicInterpolationMode: 'default',
                data: []
            }]
        },
        options: {
            title: {
                display: true,
                text: 'CPU Utilization and Load Averages'
            },
            scales: {
                xAxes: [{
                    type: 'realtime',
                    realtime: {
                        duration: 600000,
                        delay: 2000,
                        pause: false
                    }
                }],
                yAxes: [{
                    id: 'y-axis-1',
                    type: 'linear',
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Utilization (%)'
                    },
                    position: 'left',
                    ticks: {
                        suggestedMin: 0,
                        suggestedMax: 100,
                        maxTicks: 10,
                        precision: 2
                    }
                },
                {
                    id: 'y-axis-2',
                    type: 'linear',
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Load Average'
                    },
                    position: 'right',
                    ticks: {
                        suggestedMin: 0,
                        suggestedMax: 5,
                        maxTicks: 10,
                        precision: 2
                    },
                    util: 'load'
                }]
            },
            tooltips: {
                mode: 'nearest',
                intersect: false,
                callbacks: {
                    label: function (tooltipItem, data) {
                        var label = data.datasets[tooltipItem.datasetIndex].label || '';

                        if (label) {
                            label += ': ';
                        }
                        label += Math.round(tooltipItem.yLabel * 100) / 100;
                        return label;
                    }
                }
            },
            hover: {
                mode: 'nearest',
                intersect: false,
                animationDuration: 0
            },
            responsiveAnimationDuration: 0,
            plugins: {
                streaming: {
                    frameRate: 10
                }
            }
        }
    }

    // get chart canvas
    var ctx = document.getElementById("myChart").getContext("2d");

    // create the chart using the chart canvas
    var myChart = new Chart(ctx, chartConfig);

    return myChart;
}

function addUtilDataPoint(util, timestamp, myChart) {
    // append the new data to the existing chart data
    myChart.data.datasets[0].data.push({
        x: timestamp,
        y: util
    });

    // update chart datasets keeping the current animation
    myChart.update({
        preservation: true
    });
}

function addLoadDataPoint(msg, timestamp, myChart) {
    // append the new data to the existing chart data
    myChart.data.datasets[1].data.push({
        x: timestamp,
        y: msg.load_one
    });
    myChart.data.datasets[2].data.push({
        x: timestamp,
        y: msg.load_five
    });
    myChart.data.datasets[3].data.push({
        x: timestamp,
        y: msg.load_fifteen
    });

    // update chart datasets keeping the current animation
    myChart.update({
        preservation: true
    });
}

function addAlert(msg, timestamp) {
    var item = '';
    if (msg.start) {
        item += '<li class="alarm"><span class="fa-li"><i class="fas fa-exclamation-circle"></i></span>';
        item += 'High ' + msg.type + ' generated an alarm: ';
        item += msg.type + ' = ' + Math.round(msg.value * 100)/100 + ' at time: ' + timestamp.format('HH:mm:ss');
        item += '</li>';
    } else {
        item += '<li class="recover"><span class="fa-li"><i class="fas fa-check"></i></span>';
        item += 'Alarm for high ' + msg.type + ' recovered at time: ' + timestamp.format('HH:mm:ss');
        item += '</li>';
    }
    $(".log ul").prepend(item);
}

function addStats(msg, timestamp) {
    if (msg.cpu_avg) {
        $('#avg-cpu').text(Math.round(msg.cpu_avg * 100) / 100)
    } else if (msg.load_avg) {
        $('#avg-load').text(Math.round(msg.load_avg * 100) / 100)
    }
}